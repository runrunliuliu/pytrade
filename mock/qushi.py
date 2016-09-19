# coding:utf-8
from mock import mockbase
import sys
import os
import os.path
from collections import OrderedDict
from operator import itemgetter


class qushi(mockbase):

    def __init__(self, startday, baseday, codearr, dirs, forcetp):

        self.__stopwin = 1.10
        self.__stoplos = 0.92

        super(qushi,self).__init__(startday, baseday)

        self.__dropout     = {}
        self.__observed    = {}
        self.__qspred      = {}
        self.__qs          = {}
        self.__opset       = {} 
        self.__clset       = {}
        self.__hiset       = {}
        self.__lwset       = {}
        self.__lastdayk    = {}

        subdir = 'qushi'
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            fsize = fname.split('.')
            if len(fsize) > 2:
                continue
            code  = fname[0:8]
            self.loadTrades(dirs, subdir, code)

    # interface to be DONE
    def initExit(self, mtime, instdaymap, lastdayk):
        self.__exit = None 

    # interface to be DONE 
    def dumpSelect(self, tups, nday):
        self.__select = None

    def setStop(self, win, loss):
        self.__stopwin = win
        self.__stoplos = loss

    def mockrange(self):
        print 'TEST:', self.getsDay(), self.geteDay()

    def initDayK(self, op, hi, lw, cl, lastdayk):
        self.__opset    = op
        self.__clset    = cl
        self.__hiset    = hi
        self.__lwset    = lw
        self.__lastdayk = lastdayk

    def initZUHE(self, dirs, subdir, forcetp):
        zuhe     = {}
        ozuhe    = []
        fname = './data/zuhe.qushi.txt'
        if os.path.isfile(fname): 
            for line in open(fname):
                arr = line.strip().split(' ')
                zuhe[arr[2]] = arr[0]
                ozuhe.append(arr[2])
        return (zuhe, ozuhe)

    def buy(self, tup, nxday, nday, tp):
        buyprice = None
        return buyprice 
  
    def pred(self, pkey):
        ret = None
        if pkey in self.__qspred:
            ret = float(self.__qspred[pkey])
        return ret

    def filter(self, key):
        ret    = False
        reason = ''
        return (ret, reason)

    def forceSell(self, tup, tday, nxday, flag, ref=None):
        inst = tup[0]
        sellprice = None
        if nxday is None:
            return sellprice
        skey = inst + '|' + nxday
        if skey not in self.__hiset:
            skey = inst + '|' + self.__lastdayk[inst]
        if flag == 1:
            sellprice = float(self.__opset[skey])
        if flag == 2:
            op = float(self.__opset[skey])
            lw = float(self.__lwset[skey])
            if op < ref:
                sellprice = op
            else:
                if lw < ref:
                    sellprice = ref
        return sellprice

    def sell(self, tup, tday, nxday, instlast, baseday=None):
        sellprice = None
        return sellprice
# 
