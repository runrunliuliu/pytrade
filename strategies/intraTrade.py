from pyalgotrade import strategy
from pyalgotrade.technical import ma
import numpy as np
import pandas as pd
from pandas import DataFrame, read_csv
from pyalgotrade import broker
from pyalgotrade import bar 
from pyalgotrade.technical import stoch 
from pyalgotrade.technical import rsi
import time
import datetime


class IntraTrade(strategy.BacktestingStrategy):

    def __init__(self,feed,instruments,ind_dt,ts):
        strategy.BacktestingStrategy.__init__(self,feed,cash_or_brk=200)

        self.__position  = [] 
        self.__intrapost = dict()

        self.__instruments = instruments
        self.__ts          = ts
        self.__ydate       = '' 

        self.lastday = dict()
        self.df      = pd.read_csv(ind_dt,dtype={'code':np.str})
        self.tdays   = np.array(self.df['Date'].unique())
        
        self.__prices = feed.getDataSeries(self.__instruments)
        self.__KDJ = stoch.StochasticOscillator(self.__prices,9)

        rsiPeriod = 6
        self.__priceDS = feed[self.__instruments].getPriceDataSeries()
        self.__rsi = rsi.RSI(self.__priceDS, rsiPeriod)

        self.__PK = None
        self.__PD = None
        self.__fakeShares = 0

        self.__prevJ = None
        self.__buydays = set() 
        
        self.getBroker().setMaxHoldingDays(2)

    def onEnterOk(self, position):
        entorder = position.getEntryOrder()
        execInfo = entorder.getExecutionInfo()
        inst     = entorder.getInstrument()
        price    = execInfo.getPrice()
        shares   = execInfo.getQuantity()
        self.error("BUY: " + str(inst) + " at $%.2f shares:%.2f orderid:%d" % (price,shares,entorder.getId()))

    def onExitOk(self, position):
        extorder = position.getExitOrder()
        execInfo = extorder.getExecutionInfo()
        inst     = position.getEntryOrder().getInstrument()
        price    = execInfo.getPrice()
        shares   = execInfo.getQuantity()
        self.error("SELL: " + str(inst) + " at $%.2f shares:%.2f orderid:%d" % (price,shares,extorder.getId()))

    def onEnterCanceled(self, position):
        inst = position.getEntryOrder().getInstrument()
        info = position.getCancelDesc()
        self.info("%s inst - Execinfo: %s" % (
            inst,
            info
        ))

    def buySignal(self,bartime):
        # return self.getKDJ()
        return self.getRSI()

    def getRSI(self):
        ret = False
        if self.__rsi[-1] < 10:
            ret = True
        return ret

    def getKDJ(self):
        ret = False 
        K = self.__KDJ.getK()[-1]
        D = self.__KDJ.getD()[-1]
        J = 100000
        if K is not None and D is not None:
            J = 3 * K - 2 * D
        
        if J < -10:
            ret = True

        return ret

    def checkTimeEnter(self,bartime):
        ret = False

        nowday = bartime.date().strftime('%Y-%m-%d')
        nowday = nowday + ' 10:30:00'
        tmpdt  = datetime.datetime.strptime(nowday, "%Y-%m-%d %H:%M:%S")
        threshold = time.mktime(tmpdt.timetuple())

        current   = time.mktime(bartime.timetuple())
        if current > threshold:
            ret = True
        return ret

    def onBars(self,bars):
        inst = self.__instruments 
        bartime = bars.getDateTime()
        hour = bartime.hour
        minu = bartime.minute
        if self.__fakeShares > 0:
            oinst = inst 
            if oinst in self.__intrapost:
                intrapos = self.__intrapost[oinst]
                exorder  = intrapos.getExitOrder()
                if intrapos.getEntryOrder().isFilled() and exorder is None:
                    execInfo = intrapos.getEntryOrder().getExecutionInfo()
                    price    = execInfo.getPrice()
                    intrapos.exitRange(True, price * 0.9, price * 1.02)
                if exorder is not None:
                    if exorder.isFilled():
                        del self.__intrapost[oinst]
                    else:
                        if hour == 14 and minu == 50:
                            self.getBroker().cancelOrder(exorder)
                            intrapos.exitMarket()
            else:
                if self.buySignal(bartime):
                    shares = int(self.getBroker().getCash() * 0.5 / bars[inst].getPrice())
                    if shares > self.__fakeShares:
                        shares = self.__fakeShares
                    if shares > 0 and self.checkTimeEnter(bartime) and bartime.date() not in self.__buydays:
                        shares = 1
                        pos = self.enterLong(inst,shares,False)
                        self.__intrapost[oinst] = pos
                        self.__buydays.add(bartime.date())

        if len(self.__position) == 0:
            shares = int(self.getBroker().getCash() * 0.5 / bars[inst].getPrice())
            if shares > 0:
                self.__fakeShares = shares
# --
