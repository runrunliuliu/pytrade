from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from pyalgotrade.technical import xingtai 


class ShrinkVolRise(eventprofiler.Predicate):

    def __init__(self, feed):
        smaPeriod      = 60
        self.__returns = {}
        self.__volrate = {}
        self.__vXT     = {}
        self.__ma      = {}
        for instrument in feed.getRegisteredInstruments():
            priceDS = feed[instrument].getAdjCloseDataSeries()
            volDS   = feed[instrument].getVolumeDataSeries()
            # Returns over the adjusted close values.
            self.__returns[instrument] = roc.RateOfChange(priceDS, 1)
            self.__volrate[instrument] = roc.RateOfChange(volDS, 1)
            # MA over the adjusted close values.
            self.__ma[instrument] = ma.SMA(priceDS, smaPeriod)
    
            bars = feed.getDataSeries(instrument)
            self.__vXT[instrument] = xingtai.ShrinkVolRise(bars,5)

    def eventOccurred(self, instrument, bards):
        ret = False

        if len(self.__ma[instrument]) == 0:
            return ret 

        if self.__vXT[instrument][-1] is not None and self.__vXT[instrument][-1][0] == 1:
            if bards[-1].getHigh() == bards[-1].getLow():
                print "EVENT Cancel YZB:", bards[-1].getDateTime(),instrument
                return ret
            print "EVENT OK", bards[-1].getDateTime(), instrument
            ret = True

        # returns = self.__returns[instrument][-1]
        # volrate = self.__volrate[instrument][-1]
        # if returns > 0.098 and volrate < 0 and volrate > -0.5:
        #     if bards[-1].getHigh() == bards[-1].getLow():
        #         print "EVENT Cancel YZB:", bards[-1].getDateTime(),instrument
        #         return ret
        #     print "EVENT OK", bards[-1].getDateTime(), instrument
        #     ret = True
        
        return ret
#
