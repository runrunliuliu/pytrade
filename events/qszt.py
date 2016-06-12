from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from pyalgotrade.technical import xingtai 
from pyalgotrade.technical import qszt 


class QingShiZT(eventprofiler.Predicate):

    def __init__(self, feed):
        self.__XT  = {}
        self.__ma  = {}
        for instrument in feed.getRegisteredInstruments():
            priceDS = feed[instrument].getAdjCloseDataSeries()
            bars = feed.getDataSeries(instrument)
            self.__XT[instrument] = qszt.QiangShiZhangTing(bars, 10, 5)
            self.__ma[instrument] = ma.SMA(priceDS,5)

    def eventOccurred(self, instrument, bards):
        ret = False

        print 'Debug:',bards[-1].getDateTime(),self.__ma[instrument][-1]
        if self.__XT[instrument][-1] is not None and self.__XT[instrument][-1][0] == 1:
            if bards[-1].getHigh() == bards[-1].getLow():
                print "EVENT Cancel YZB:", bards[-1].getDateTime(),instrument
                return ret
            print "EVENT OK", bards[-1].getDateTime(), instrument
            ret = True
        return ret
#
