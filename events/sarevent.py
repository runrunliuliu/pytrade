from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from pyalgotrade.technical import xingtai 
from pyalgotrade.technical import qszt 
from pyalgotrade.technical import chaodie 
from pyalgotrade.technical import sar 
from pyalgotrade.technical import indicator 
from pyalgotrade.barfeed import indfeed
import numpy as np


class SAREVENT(eventprofiler.Predicate):

    def __init__(self, feed, fs):
        self.__sar = dict()
        for instrument in feed.getRegisteredInstruments():
            bars = feed.getDataSeries(instrument)
            self.__sar[instrument] = sar.SAR(bars, 4)

    def eventOccurred(self, instrument, bards):
        ret = False

        if self.__sar[instrument][-1] is None:
            return ret

        sarval = self.__sar[instrument][-1][0]
        if sarval is not None and len(sarval) > 1 and sarval[-1] == -1 and sarval[-2] == 1:
            if bards[-1].getHigh() == bards[-1].getLow():
                print "EVENT Cancel YZB:", bards[-1].getDateTime(),instrument
                return ret
            print "EVENT OK", bards[-1].getDateTime(), instrument, sarval[-1], sarval[-2]
            ret = True
        return ret
#
