from pyalgotrade import strategy
from pyalgotrade.technical import ma
import numpy as np
import pandas as pd
from pandas import DataFrame, read_csv
from pyalgotrade import broker
from pyalgotrade.technical import vol 
from pyalgotrade.technical import linreg 
from pyalgotrade.barfeed import indfeed
import operator


class DtStrategy(strategy.BacktestingStrategy):

    def __init__(self,feed,instruments,ind_dt,ts):
        strategy.BacktestingStrategy.__init__(self,feed)

        self.__indicator = indfeed.Feed()
        self.__indicator.addBarsFromCSV('dt',"./data/dtboard.csv.out")

        self.__position    = [] 
        self.__instruments = instruments
        self.__ts          = ts
        self.__ydate       = '' 

        self.lastday = dict()
        self.df      = pd.read_csv(ind_dt,dtype = {'code':np.str})
        self.tdays   = np.array(self.df['Date'].unique())

        self.getBroker().setMaxHoldingDays(5)

        self.__preVol = dict()
        self.__ma5    = dict()
        self.__vol    = dict()
        self.__slope  = dict()
        for inst in self.__instruments:
            prices = feed[inst].getPriceDataSeries()
            self.__ma5[inst] = ma.SMA(prices,5)
            # volums = feed[inst].getVolumeDataSeries()
            # self.__vol[inst] = vol.VOLUME(volums,5,10,20)
            # self.__slope[inst] = linreg.Slope(prices,6)

    def slopeFilter(self,inst):
        ret = False
        if len(self.__slope[inst]) > 0:
            val = self.__slope[inst][-1]
            if val < 2.0 and val > -0.8:
                ret = True 
        return ret

    def onSelectInst(self,insts,df,keydate,bars):
        inst = 0 
        if len(keydate) == 0:
            return inst
        key  = 'rate'
        vals = {}
        for i in insts:
            (code,indval) = self.__indicator.getMatch(i, keydate)
            if code is not None:
                vals[code] = indval[key]
        if len(vals) > 0:
            sorted_x = sorted(vals.items(), key=operator.itemgetter(1), reverse=True)
            for st in sorted_x:
                code = st[0]
                rate = st[1]
                if rate > 2.0:
                    inst = code 
                    break
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
                        p.exitRange(True, price * 0.9, price * 1.10)
                    else:
                        if not exorder.isFilled():
                            tmp.append(p)
                else:
                    tmp.append(p)
            self.__position = tmp

        inst = self.onSelectInst(self.__instruments, self.df, ndate, bars)
        if inst == 0:
            return
        nowprice = bars[inst].getPrice()
        shares = 0
        cash   = self.getBroker().getCash()
        shares = int( cash * 0.90 / nowprice )
        if shares > 100 * 10:
            # self.__position.append(self.enterLong(inst,shares,False))
            limitPrice = nowprice * 1.06
            self.__position.append(self.enterLongLimit(inst,limitPrice,shares,False))
# ----
