# coding:utf-8
from mock import mockbase
import sys
import os
from collections import OrderedDict
from operator import itemgetter


class NBS(mockbase):

    def __init__(self, startday, baseday, codearr, dirs, forcetp):

        self.__stopwin = 1.20
        self.__stoplos = 0.90

        super(NBS, self).__init__(startday, baseday)

        self.__dropout     = {}
        self.__observed    = {}
        self.__qs          = {}
        self.__opset       = {} 
        self.__clset       = {}
        self.__hiset       = {}
        self.__lwset       = {}
        self.__lastdayk    = {}

        subdir = 'nbs'
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            fsize = fname.split('.')
            if len(fsize) > 2:
                continue
            code  = fname[0:8]
            self.loadMtime(dirs, code)
            self.loadTrades(dirs, subdir, code)

    def setStop(self, win, loss):
        self.__stopwin = win
        self.__stoplos = loss

    def mockrange(self):
        print 'TEST:', self.getsDay(), self.geteDay()

    def initDayK(self, op, hi, lw, cl, lastdayk):
        self.__opset    = op
        self.__clset    = cl
        self.__hiset    = hi
        self.__lwset    = lw
        self.__lastdayk = lastdayk

    def initZUHE(self, dirs, subdir, forcetp):
        zuhe     = {}
        ozuhe    = []
        for line in open('./data/zuhe.txt'):
            arr = line.strip().split(' ')
            zuhe[arr[2]] = arr[0]
            ozuhe.append(arr[2])
        return (zuhe, ozuhe)

    def buy(self, tup, nxday, nday, tp):
        buyprice = None; ret = True

        inst   = tup[0]
        name   = tup[1]
        
        dkey = inst + '|' + nxday
        if dkey not in self.__opset:
            ret = False
            print 'DEBUG:', nday, 'Drop Suspension ', inst, name, nxday, dkey
            return buyprice

        nxopen = float(self.__opset[dkey])
        nclose = float(self.__clset[inst + '|' + nday])

        # 过滤高空3个点或者低开1个点的价格
        jump = (nxopen - nclose) / nclose 
        if jump < -0.01 or jump > 0.03:
            print 'DEBUG:', nday, 'DROP BarOpen', inst, name, nxday, nclose, nxopen, jump  
            ret = False
        if ret is True:
            bkey = inst + '|' + nxday
            # 按次日的开盘价买入
            if tp == 0:
                if bkey in self.__opset:
                    buyprice = float(self.__opset[bkey])

        print 'TEST:', nday, inst, name, buyprice

        return buyprice 
  
    def pred(self, pkey):
        ret = 0.0 
        return ret

    def filter(self, key):
        ret    = False
        reason = ''
        return (ret, reason)

    def forceSell(self, tup, tday, nxday, flag, ref=None):
        inst = tup[0]
        sellprice = None
        if nxday is None:
            return sellprice
        skey = inst + '|' + nxday
        if skey not in self.__hiset:
            skey = inst + '|' + self.__lastdayk[inst]
        if flag == 1:
            sellprice = float(self.__opset[skey])
        if flag == 2:
            op = float(self.__opset[skey])
            lw = float(self.__lwset[skey])
            if op < ref:
                sellprice = op
            else:
                if lw < ref:
                    sellprice = ref
        return sellprice

    def sell(self, tup, tday, nxday, instlast, baseday=None):
        sellprice = None

        sigday = tup[0]

        tup  = tup[1]
        inst = tup[0]

        if nxday is None:
            return sellprice

        mkey = inst + '|' + tday
        skey = inst + '|' + nxday
        if skey not in self.__hiset:
            skey = inst + '|' + self.__lastdayk[inst]

        # low  = float(self.__lwset[skey])
        high = float(self.__hiset[skey])
        ops  = float(self.__opset[skey])
        cls  = float(self.__clset[skey])

        tprice = None
        trades = self.getTrades()[sigday]
        for t in trades:
            if t[0] == inst:
                tprice = float(t[3])
                break

        if self.getSZmtime() == 1:
            # 熊市止盈2
            pred = tprice 
            if high > pred * self.__stopwin:
                sellprice = pred * self.__stopwin
                if sellprice < ops:
                    sellprice = ops
        # 止盈1
        if sellprice is None:
            gd20price = self.getMtime()[mkey][21]
            if cls < gd20price:
                sellprice = cls

        if cls < tprice * self.__stoplos:
            sellprice = cls

        return sellprice
#
