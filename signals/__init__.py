from utils.utils import FileUtils
from collections import OrderedDict
import os
import abc
import json


class XTsignal(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, dirs, nday):
        self.__dirs = dirs
        self.__nday = nday

        self.__nmonk  = None
        self.__nweek  = None
        self.__ndayk  = None
        self.__n30min = None
        self.__n60min = None

        # GET CODE LIST
        self.__codes = []
        fs = FileUtils('','','')
        codearr = fs.os_walk(dirs + '/dayk/xingtai/')
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            code  = fname[0:8]
            self.__codes.append(code)

        self.__codename = dict()
        for line in open(dirs + '/stockinfo.csv'):
            arr = line.strip().split(',')
            self.__codename[arr[1]] = arr[2]

        self.__dtzq  = OrderedDict() 
        self.__zqdt  = OrderedDict() 
        zq = 0
        for line in open(dirs + '/dayk/ZS000001.csv'):
            arr = line.strip().split(',')
            dt  = arr[0]

            self.__dtzq[dt] = zq
            self.__zqdt[zq] = dt

            zq = zq + 1

    def getPrevDay(self):
        zq   = self.__dtzq[self.__nday]
        pday = self.__zqdt[zq - 1]
        return pday

    # load Data
    def loadJSON(self, period):
        ret = dict()
        for c in self.__codes:
            fname = self.__dirs + '/' + period + \
                '/xingtai/'  + c + '.xingtai.csv'
            if os.path.isfile(fname) is False:
                continue
            for line in open(fname):
                line = line.strip()
                arr  = line.split('\t')
                day = arr[0][0:10]
                if day == self.__nday:
                    ret[c] = json.loads(arr[1])
        return ret

    def loadSignals(self, period='ALL'):
        if period == 'ALL':
            self.__nmonk  = self.loadJSON('monk')
            self.__nweek  = self.loadJSON('week')
            self.__ndayk  = self.loadJSON('dayk')
            self.__n60min = self.loadJSON('60mink')
            self.__n30min = self.loadJSON('30mink')

        if period == 'dayk':
            self.__ndayk  = self.loadJSON('dayk')

    def getSignals(self):
        return (self.__nmonk, self.__nweek, self.__ndayk, \
                self.__n60min, self.__n30min)

    def getDay(self):
        return self.__nday

    def getCodes(self):
        return self.__codes

    def getName(self, code):
        ret  = 'NULL'
        code = code[2:]
        if code in self.__codename:
            ret = self.__codename[code]
        return ret
#
