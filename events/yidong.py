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


class YiDong(eventprofiler.Predicate):

    def __init__(self, feed, ts):
        self.__ts = ts

        self.__indicator = indfeed.Feed()
        self.__indicator.addBarsFromCSV('yd',"./data/yd.csv.out", index=['Date','code','period'])

        self.__ma = {}

        for instrument in feed.getRegisteredInstruments():
            priceDS = feed[instrument].getAdjCloseDataSeries()
            self.__ma[instrument] = ma.SMA(priceDS,60)

    def eventOccurred(self, instrument, bards):
        ret = False

        datetime = bards[-1].getDateTime()
        ndate    = self.__ts.tostring(datetime)

        # period = (9,)
        # period = (10,)
        # period = (13,)
        
        period = (1,)
        (code0,indval) = self.__indicator.getMatch(instrument, ndate, (0,))
        (code1,indval) = self.__indicator.getMatch(instrument, ndate, period)
        if code1 is not None and code0 is not None and self.__ma[instrument][-1] is not None:
            minp = indval['percentageamin']
            maxp = indval['percentageamax']
            if maxp > 50 and (maxp + minp) > 0:
                print "EVENT OK", bards[-1].getDateTime(), instrument
                ret = True
        return ret
#
