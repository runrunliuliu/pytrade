from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma


class NoRiseInPeriod(eventprofiler.Predicate):

    def __init__(self, feed):
        smaPeriod = 30 
        self.__returns = {}
        self.__volrate = {}
        self.__ma = {}
        self.__ma250 = {}
        for instrument in feed.getRegisteredInstruments():
            priceDS = feed[instrument].getAdjCloseDataSeries()
            # Returns over the adjusted close values.
            self.__returns[instrument] = roc.RateOfChange(priceDS,10)
            # MA over the adjusted close values.
            self.__ma[instrument]    = ma.SMA(priceDS, smaPeriod)
            self.__ma250[instrument] = ma.SMA(priceDS,250)

        self.__daysum = {}
        self.__enterDay = []
   
    def getDaySum(self):
        for d in self.__enterDay:
            print d,self.__daysum[d]

    def collectEnterDay(self,bards):
        count = 1
        date = bards[-1].getDateTime().date().strftime('%Y-%m-%d')
        if date in self.__daysum:
            count = self.__daysum[date] + 1
        else:
            self.__enterDay.append(date)
        self.__daysum[date] = count

    def buySignal(self, instrument, bars):
        return True
        ret = False
        matmp = self.__ma[instrument]
        ma250 = self.__ma250[instrument]
        if len(matmp) < 2:
            return ret
        if ma250[-1] is None:
            return ret

        if matmp[-2] is not None \
                and matmp[-1] > matmp[-2] \
                and bars[-1].getClose() > ma250[-1] \
                and bars[-1].getClose() < ma250[-1] * 1.02:
            ret = True
        return ret

    def eventOccurred(self, instrument, bards):
        ret = False

        if len(self.__ma[instrument]) == 0:
            return ret 
        
        returns = self.__returns[instrument][-1]
        if returns < 0.08 and self.buySignal(instrument, bards):
        # if returns > 0.20 and self.buySignal(instrument, bards):
            if bards[-1].getHigh() == bards[-1].getLow():
                print "EVENT Cancel YZB:", bards[-1].getDateTime(),instrument
                return ret

            self.collectEnterDay(bards)        

            print "EVENT OK", bards[-1].getDateTime(), instrument
            ret = True
        return ret
#
