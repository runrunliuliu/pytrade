from pyalgotrade.feed import csvfeed
from pyalgotrade.tools import utils
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed


class Statistic(strategy.BacktestingStrategy):

    def __init__(self,feed,instrument):
        strategy.BacktestingStrategy.__init__(self,feed)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__instrument = instrument
        self.__position = None
        self.__keeprice = [] 
        self.__keepdate = []
        self.ts = utils.TimeUtils()

    def onBars(self,bars):
        date  = self.ts.tostring(bars[self.__instrument].getDateTime())
        price = bars[self.__instrument].getPrice()
        self.__keeprice.append(price)
        self.__keepdate.append(date)

        for i in range(2,7):
            if i > len(self.__keeprice):
                break
            ind = -1 * i
            print self.__keepdate[ind],i - 1,(price - self.__keeprice[ind]) / self.__keeprice[ind]


def main():
  
    instrument = "sh600036"
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV(instrument, "data/SH600036.csv")
    st = Statistic(feed, instrument)
    st.run()

if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
