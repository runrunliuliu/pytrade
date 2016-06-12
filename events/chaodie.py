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


class ChaoDie(eventprofiler.Predicate):

    def __init__(self, feed, ts):
        self.__ts = ts

        self.__indicator = indfeed.Feed()
        self.__indicator.addBarsFromCSV('dt',"./data/dtboard.csv.out")

        self.__XT  = {}
        self.__ma  = {}

        for instrument in feed.getRegisteredInstruments():
            priceDS = feed[instrument].getAdjCloseDataSeries()
            bars = feed.getDataSeries(instrument)
            self.__XT[instrument] = chaodie.ChaoDie(bars, 1, 5, 0.90)
            self.__ma[instrument] = ma.SMA(priceDS,5)

    def eventOccurred(self, instrument, bards):
        ret = False

        datetime = bards[-1].getDateTime()
        ndate    = self.__ts.tostring(datetime)

        (code,indval) = self.__indicator.getMatch(instrument, ndate)
        if code is not None:
            print datetime,indval

        xt1 = self.__XT[instrument][-1][0]
        xt2 = self.__XT[instrument][-1][1]
        xt3 = self.__XT[instrument][-1][2]
        if xt1 is not None and len(xt1) > 5:
            na = np.asarray(xt1[-4:])
            nb = np.asarray(xt2[-4:])
            nc = np.asarray(xt3[-4:])
            if (na == 1).all() and (nb <= 0).all() and (nc < 1.5).all():
                print "EVENT OK", bards[-1].getDateTime(), instrument
                ret = True
        return ret
#
