from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import indicator 
from pyalgotrade.utils import collections
import numpy as np
import pandas as pd
from pandas import DataFrame, read_csv
from pyalgotrade import broker
from pyalgotrade.technical import vol 
from pyalgotrade.technical import linreg 
from pyalgotrade.barfeed import indfeed
import operator
from itertools import chain


class MLStrategy(strategy.BacktestingStrategy):

    def __init__(self,feed,instruments,ind_dt,ts):
        strategy.BacktestingStrategy.__init__(self,feed)
        self.__position    = [] 
        self.__instruments = instruments
        self.__ts          = ts
        self.__ydate       = '' 

        self.getBroker().setMaxHoldingDays(5)

        self.__features  = {}
        self.__feacount  = {}
        self.__indicators = {}
        self.__instance   = {}
        for inst in self.__instruments:
            bars = feed.getDataSeries(inst)
            self.__indicators[inst] = indicator.Indicator(bars, 250)

            self.__features[inst] = collections.ListDeque(20)  
            self.__instance[inst] = collections.ListDeque(20)  

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
    
    def setFeaList(self, inst, ft):
        self.__features[inst].append(ft)

    def onBars(self,bars):
        # init--Get Date Time
        bartime = bars.getDateTime()
        for inst in self.__instruments:
            if inst in bars:
                cprice = bars[inst].getClose()
                self.setFeaList(inst, self.__indicators[inst][-1])
                if len(self.__features[inst]) == 20:
                    self.__instance[inst].append((bartime, inst, cprice, list(chain(*self.__features[inst]))))
                if len(self.__instance[inst]) == 20:
                    hist_cprice = self.__instance[inst][-20][2]
                    hist_fts    = self.__instance[inst][-20][3]

                    zhangfu = (cprice - hist_cprice) / hist_cprice
                    print bartime.date(), inst, ','.join([str(x) for x in hist_fts]), zhangfu 
# ----
