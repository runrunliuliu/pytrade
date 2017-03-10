from utils.utils import FileUtils
from collections import OrderedDict
import os
import abc
import json
import redis


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

        self.__rdayk = redis.ConnectionPool(host='127.0.0.1', port=6379)

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

    # GET DAY Signal from redis
    def getNday(self, code, path):
        key   = code + '_' + self.__nday
        dbstr = self.__ndayk.get(key)
        if dbstr is None:
            return None
        val = json.loads(dbstr)
        for p in path:
            if len(val) > 0:
                val = val[p]
        return val

    def loadSignals(self, period='ALL'):
        # connect2redis
        self.__ndayk = redis.Redis(connection_pool=self.__rdayk)

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
