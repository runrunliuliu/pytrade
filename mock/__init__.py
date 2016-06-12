import abc
import os
import datetime
from collections import OrderedDict
from operator import itemgetter


class mockbase(object):

    __metaclass__ = abc.ABCMeta
   
    def __init__(self, startday, baseday, *args, **kw):
        self.__sdate = datetime.datetime.strptime(startday, "%Y-%m-%d")
        self.__edate = datetime.datetime.strptime(baseday, "%Y-%m-%d")
        self.__tradesignal = OrderedDict()
        self.__mtime = OrderedDict()

    def loadMtime(self, dirs, code):
        fname = dirs + '/mtime/' + code + '.cxshort.csv'
        if os.path.isfile(fname) is False:
            return
        cnt = 0
        for line in open(fname):
            if cnt == 0:
                cnt = cnt + 1
                continue
            tmp  = line.strip().split(',')
            day   = tmp[0]
            if self.checkDayRange(day) is False:
                cnt = cnt + 1
                continue
            for t in range(1, len(tmp)):
                tmp[t] = float(tmp[t])
            mtime = tuple(tmp[1:])
            self.__mtime[code + '|' + day] = mtime
            cnt = cnt + 1

    def loadTrades(self, dirs, subdir, code):
        fname = dirs + '/' + subdir + '/' + code + '.trade.csv'
        if os.path.isfile(fname) is False:
            return
        for line in open(fname):
            tmp  = line.strip().split(',')
            day  = tmp[0]
            if self.checkDayRange(day) is False:
                continue
            tmp[3] = float(tmp[3])
            tups   = tuple(tmp[1:len(tmp)])
            arr = []
            if day in self.__tradesignal:
                arr = self.__tradesignal[day]
            arr.append(tups)
            arr = sorted(arr, key=itemgetter(2), reverse=True)
            self.__tradesignal[day] = arr 

    def getMtime(self):
        return self.__mtime

    def getTrades(self):
        return self.__tradesignal

    @abc.abstractmethod
    def filter(self, pkey):
        raise NotImplementedError()

    @abc.abstractmethod
    def pred(self, pkey):
        raise NotImplementedError()

    @abc.abstractmethod
    def buy(self, tup, nxday, nday):
        raise NotImplementedError()

    @abc.abstractmethod
    def sell(self, tup, tday, nxday, instlast, baseday=None):
        raise NotImplementedError()

    def getsDay(self):
        return self.__sdate

    def geteDay(self):
        return self.__edate

    def checkDayRange(self, day):
        ret = True 
        date = datetime.datetime.strptime(day, "%Y-%m-%d")
        if date.date() < self.__sdate.date():
            ret = False 
        if date.date() > self.__edate.date():
            ret = False
        return ret
