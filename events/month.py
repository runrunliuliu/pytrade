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


class MONTH(eventprofiler.Predicate):
    def __init__(self):
        self.__zdf = dict()

    def get(self):
        return self.__zdf

    def eventOccurred(self, instrument, bards):

        datetime = bards[-1].getDateTime()
        ndate    = datetime.strftime('%Y-%m-%d')
        month = ndate.split('-')[1]

        instrument = instrument + '-' + month

        ret = False
        opens    = bards[-1].getOpen()
        close    = bards[-1].getClose()
        act = 0 
        if (close - opens) > 0: 
            act = 1
            ret = True
        if instrument in self.__zdf:
            actset = self.__zdf[instrument]
        else:
            actset = dict()
        if act == 1:
            if 'z' in actset:
                actset['z'] = actset['z'] + 1
            else:
                actset['z'] = 1
        if act == 0:
            if 'd' in actset:
                actset['d'] = actset['d'] + 1
            else:
                actset['d'] = 1
        self.__zdf[instrument] = actset

        return ret
#
