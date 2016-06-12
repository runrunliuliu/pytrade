from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
import numpy as np
import pandas as pd


class TimeHit(eventprofiler.Predicate):

    def __init__(self, feed, ts=None):
        self.__returns = {}
        self.__volrate = {}
        self.__ma = {}
        self.__ma250 = {}
        for instrument in feed.getRegisteredInstruments():
            priceDS = feed[instrument].getAdjCloseDataSeries()
            # Returns over the adjusted close values.
            self.__returns[instrument] = roc.RateOfChange(priceDS,1)

        self.__daysum = {}
        self.__enterDay = []
        self.__df = pd.read_csv('data/st.txt',dtype = {'code':np.str})
        self.__codeday = {}
        self.__used = set()
        tmparr = []
        for line in open('data/gaiming.txt'):
            tmparr.append(line.strip())

        for i in range(1,len(tmparr)):
            tmp = tmparr[-1 * i].split(',')
            self.__codeday[tmp[0]] = tmp[1] 
        self.__ts = ts 
   
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

    def buySignal(self, instrument, bars, day):
        ret = False
        if instrument in self.__codeday:
            day = self.__ts.tostring(day) 
            baseday = self.__codeday[instrument]
            key = instrument + ',' + baseday 
            if key not in self.__used and self.__ts.compare_dateTime(day,baseday):
                ret = True
                self.__used.add(key)
        # match = self.__df[(self.__df.Date == day) & (self.__df.code == instrument)]
        # if len(match) > 0:
        #     ret = True
        return ret

    def eventOccurred(self, instrument, bards):
        ret = False
        nowday = bards[-1].getDateTime().date()
        if self.buySignal(instrument, bards, nowday):
            print "EVENT OK", bards[-1].getDateTime(), instrument
            ret = True
        return ret
#
