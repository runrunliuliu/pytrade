from utils.utils import FileUtils
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

    # load Data
    def loadJSON(self, period):
        ret = dict()
        for c in self.__codes:
            fname = self.__dirs + '/' + period + \
                '/xingtai/'  + c + '.xingtai.csv'
            if os.path.isfile(fname) is False:
                return ret
            for line in open(fname):
                line = line.strip()
                arr  = line.split('\t')
                day = arr[0][0:10]
                if day == self.__nday:
                    ret[c] = json.loads(arr[1])
        return ret

    def loadSignals(self):
        self.__nmonk  = self.loadJSON('monk')
        self.__nweek  = self.loadJSON('week')
        self.__ndayk  = self.loadJSON('dayk')
        self.__n30min = self.loadJSON('30mink')

    def getSignals(self):
        return (self.__nmonk, self.__nweek, self.__ndayk, self.__n30min)

    def getCodes(self):
        return self.__codes
#
