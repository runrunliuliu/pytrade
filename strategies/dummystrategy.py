from pyalgotrade import strategy
from pyalgotrade.technical import ma


class DummyStrategy(strategy.BacktestingStrategy):

    def __init__(self,feed,instrument):
        strategy.BacktestingStrategy.__init__(self,feed)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__ma1 = ma.SMA(self.__prices,250)
        self.__instrument = instrument
        self.__store_close_price = []
        self.__store_ma250 = []
        self.breakprice = 0
        self.breaklast  = 0
        self.breaktimes = 0
        self.crossdown  = -1 
        self.crossup    = -1
        
        self.__position = None

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY: " + str(position.getEntryOrder().getInstrument()) + " at $%.2f" % (execInfo.getPrice()))

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL: " + str(position.getEntryOrder().getInstrument()) + " at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onBars(self,bars):
        date  = bars[self.__instrument].getDateTime()
        price = bars[self.__instrument].getPrice()

        self.__store_close_price.append(price)
        self.__store_ma250.append(self.__ma1[-1])

        wds = 30
        if len(self.__store_ma250) > wds:
            flag = 0
            for i in range(2,wds):
                if self.__store_close_price[-1 * i] > self.__store_ma250[-1 * i]:
                    flag = 1
                else:
                    flag = 0
                    break
            if flag == 1 and price < self.__ma1[-1]:
                self.breakprice = price
                self.crossdown  = 1

        if self.crossdown == 1:
            self.breaklast = self.breaklast + 1

        if self.crossdown == 1 and self.breaklast <= 5 and price > self.__ma1[-1]:
            self.crossup  = 1

        if self.crossdown == 1 and self.crossup == 1 and ( abs(price - self.__ma1[-1]) / price ) < 0.02:
            if self.__position is None:
                shares = int(self.getBroker().getCash() * 0.8 / bars[self.__instrument].getPrice())
                self.__position = self.enterLong(self.__instrument, shares, True)

            self.crossdown = -1
            self.crossup   = -1
            self.breakprice = 0
            self.breaklast  = 0

            print date,price,self.__ma1[-1],self.breakprice,self.breaklast

        if self.__position is not None and self.__position.getReturn() > 0.02:
            self.__position.exitMarket()

# --
