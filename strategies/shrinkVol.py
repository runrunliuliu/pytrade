from pyalgotrade import strategy
from pyalgotrade.technical import ma
import numpy as np
import pandas as pd
from pandas import DataFrame, read_csv
from pyalgotrade import broker
from pyalgotrade.technical import vol 
from pyalgotrade.technical import linreg 
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import xingtai 


class ShrinkVol(strategy.BacktestingStrategy):

    def __init__(self,feed,instruments,ind_dt,ts):
        strategy.BacktestingStrategy.__init__(self,feed)

        self.__position    = [] 
        self.__instruments = instruments
        self.__ts          = ts
        self.__ydate       = '' 

        self.lastday = dict()
        self.df      = pd.read_csv(ind_dt,dtype = {'code':np.str})
        self.tdays   = np.array(self.df['Date'].unique())

        self.getBroker().setMaxHoldingDays(5)

        self.__preVol     = dict()
        self.__ma120      = dict()
        self.__vol        = dict()
        self.__slope      = dict()
        self.__returns    = dict()
        self.__XT         = dict()

        for inst in self.__instruments:
            priceDS                 = feed[inst].getAdjCloseDataSeries()
            self.__returns[inst]    = roc.RateOfChange(priceDS, 1)
            self.__ma120[inst]      = ma.SMA(priceDS, 5)
            
            bars = feed.getDataSeries(inst)
            self.__XT[inst] = xingtai.ShrinkVolRise(bars,5)

    def onEnterOk(self, position):
        entorder = position.getEntryOrder()
        execInfo = entorder.getExecutionInfo()
        inst     = entorder.getInstrument()
        price    = format(execInfo.getPrice(),'<6.2f')
        shares   = format(execInfo.getQuantity(),'<10.2f')
        self.error(format("BUY:",'<6') + str(inst) + " at $%s shares:%s orderid:%d" % (price,shares,entorder.getId()))

    def onExitOk(self, position):
        extorder = position.getExitOrder()
        execInfo = extorder.getExecutionInfo()
        inst     = position.getEntryOrder().getInstrument()
        price    = format(execInfo.getPrice(),'<6.2f')
        shares   = format(execInfo.getQuantity(),'<10.2f')
        self.error("SELL: " + str(inst) + " at $%s shares:%s orderid:%d" % (price,shares,extorder.getId()))

    def onEnterCanceled(self, position):
        inst = position.getEntryOrder().getInstrument()
        info = position.getCancelDesc()
        self.info("%s inst - Execinfo: %s" % (
            inst,
            info
        ))

    def onSelectInst(self,insts,df,keydate,bars):
        inst = 0 
        d    = {}
        for i in insts:
            if i not in bars:
                continue
            if self.__ma120[i][-1] is None:
                continue 
            returns = self.__returns[i][-1]
            if self.__XT[i][-1] is not None and self.__XT[i][-1][0] == 1:
                d[i] = returns 
        sd = sorted(d.items(), key=lambda x: x[1])
        if len(sd) > 0:
            inst = sd[-1][0]
        return inst

    def onBars(self,bars):
        # init--Get Date Time
        bartime = bars.getDateTime()
        ndate   = self.__ts.tostring(bartime)
        if len(self.__position) > 0:
            tmp = []
            for p in self.__position:
                order = p.getEntryOrder()
                if order.isFilled():
                    execInfo = order.getExecutionInfo()
                    price    = execInfo.getPrice()
                    exorder  = p.getExitOrder()
                    if exorder is None:
                        p.exitRange(True, price * 0.9, price * 1.05)
                    else:
                        if not exorder.isFilled():
                            tmp.append(p)
                else:
                    tmp.append(p)

            self.__position = tmp

        inst = self.onSelectInst(self.__instruments, self.df, ndate, bars)
        if inst == 0:
            return
        shares = int(self.getBroker().getCash() * 0.9 / bars[inst].getPrice())

        if shares > 100 * 10:
            self.__position.append(self.enterLong(inst,shares,True))
# --
