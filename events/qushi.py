from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from pyalgotrade.technical import xingtai 
from pyalgotrade.technical import qszt 
from pyalgotrade.technical import chaodie 
from pyalgotrade.technical import indicator 
from pyalgotrade.barfeed import indfeed
import numpy as np


class QUSHI(eventprofiler.Predicate):

    def __init__(self, feed, fs):
        self.__signal = dict()
        dirs = './output'
        deals = fs.os_walk(dirs)
        for d in deals:
            arr   = d.split('-')
            fname = arr[2] + '-' + arr[3] + '-' + arr[4]
            nday  = fname[0:10]
            cnt   = 0 
            for line in open(dirs + '/' + fname):
                if cnt < 50 or cnt > 200:
                    cnt = cnt + 1
                    continue
                (code,name,act) = line.strip().split(',')
                self.__signal[nday + '-' + code] = act
                cnt = cnt + 1

    def eventOccurred(self, instrument, bards):
        ret = False

        datetime = bards[-1].getDateTime()
        ndate    = datetime.strftime('%Y-%m-%d')

        key = ndate + '-' + instrument
        
        if key in self.__signal and self.__signal[key] == 'BUY':
            ret = True
        return ret
#
