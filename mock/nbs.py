# coding:utf-8
from mock import mockbase
import sys
import os
import os.path
from collections import OrderedDict
from operator import itemgetter
from signals import exitsigs 
from prettytable import PrettyTable


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

    def resortTrades(self, tups):
        return tups

    def initExit(self, mtime, instdaymap, lastdayk):
        self.__exit = exitsigs.ExitSignals(mtime, instdaymap, lastdayk)

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
        zuhe  = {}
        ozuhe = []
        fname = './data/zuhe.nbs.txt'
        if os.path.isfile(fname): 
            for line in open(fname):
                arr = line.strip().split(' ')
                zuhe[arr[2]] = arr[0]
                ozuhe.append(arr[2])
        return (zuhe, ozuhe)

    # 选股
    def select(self, tup, nday):
        zuhe  = tup[0]
        ozuhe = tup[1]
        winn  = tup[2]
        loss  = tup[3]
        tzuhe = PrettyTable(['T日', '代码', '名称', '止盈价', '止损价', '收盘价'])
        tzuhe.float_format = '.4'
        tzuhe.align = 'l'
        for k in ozuhe:
            tprice = None
            sigday = zuhe[k]
            trades = self.getTrades()[sigday]
            name   = ''
            for t in trades:
                if t[0] == k:
                    tprice = float(t[3])
                    name   = t[1]
                    break
            sp      = '--' 
            stopwin = 1024
            # 熊市
            if self.getSZmtime() == 1:
                # 买入第三日不收在突破日收盘之上，卖出
                holds = self.__exit.HoldTime(k, sigday, nday)
                if holds == 3:
                    sigkey = k + '|' + sigday
                    sp     = self.__clset[sigkey]
                stopwin = tprice * winn

            mkey = k + '|' + nday
            md5120    = self.getMtime()[mkey][26]
            gd20price = self.getMtime()[mkey][21]
            sp = min([md5120, gd20price, sp])

            stoplos = tprice * loss
            tzuhe.add_row([nday, k, name, stopwin, stoplos, sp])
        print tzuhe

        # 选股
        tzuhe = PrettyTable(['T日', '代码', '名称', '得分', '收益率', '持有天数', '开仓价', '止盈价', '止损价', '手数'])
        tzuhe.float_format = '.4'
        tzuhe.align = 'l'
        trades = self.getTrades()[nday]

        stocks = []
        for t in trades:
            if float(t[2]) > 2000 and float(t[2]) < 3000:
                print 'DEBUG', 'Drop Buy MAGIC SCORE', nday, t[0], t[1], float(t[2])
                continue
            if float(t[5]) < 200 and float(t[6]) < 0.8:
                print 'DEBUG', 'Drop Buy DTBOARD', nday, t[0], t[1], t[5], t[6]
                continue

            nclose = float(self.__clset[t[0] + '|' + nday])
            tmin = "{:.4f}".format(nclose * 0.98) 
            tmax = "{:.4f}".format(nclose * 1.03)
            if tmax < tmin:
                print 'DEBUG:','Drop Buy', t[0], t[1], tmin, tmax, nday
                continue
            stocks.append((t[0], tmin, tmax))
            price = '[' + str(tmin) + ' ' + str(tmax) + ']'
            tzuhe.add_row([nday, t[0], t[1], t[2], '--', '--', price, '--', '--', '--'])
        print tzuhe

        self.dumpSelect(stocks, nday)

    def dumpSelect(self, tups, nday):
        f = open('./output/nbs/' + nday + '.sl.txt', 'w')
        for t in tups:
            line = t[0][-6:] + ',NBS,NBS,' + nday + ',' + t[1] + ',' + t[2]
            f.write(line)
            f.write('\n')
        f.close()

    def buy(self, tup, nxday, nday, tp):
        buyprice = None; ret = True

        inst   = tup[0]
        name   = tup[1]
        
        trades = self.getTrades()[nday]
        for t in trades:
            if t[0] == inst and float(t[2]) > 2000 and float(t[2]) < 3000:
                print 'DEBUG', 'Drop Buy MAGIC SCORE', nday, inst, t[1], float(t[2])
                return buyprice
            if t[0] == inst and float(t[5]) < 200 and float(t[6]) < 0.8:
                print 'DEBUG', 'Drop Buy DTBOARD', nday, inst, t[1], t[5], t[6]
                return buyprice

        dkey = inst + '|' + nxday
        if dkey not in self.__opset:
            ret = False
            print 'DEBUG:', nday, 'Drop Suspension ', inst, name, nxday, dkey
            return buyprice

        nxopen = float(self.__opset[dkey])
        nclose = float(self.__clset[inst + '|' + nday])

        # 过滤高空3个点或者低开1个点的价格
        jump = (nxopen - nclose) / nclose 
        if jump < -0.02 or jump > 0.03:
            print 'DEBUG:', nday, 'DROP BarOpen', inst, name, nxday, nclose, nxopen, jump  
            ret = False
        if ret is True:
            bkey = inst + '|' + nxday
            # 按次日的开盘价买入
            if tp == 0:
                if bkey in self.__opset:
                    buyprice = float(self.__opset[bkey])
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

    def sell(self, tup, tday, nxday, instlast, yday, baseday=None):
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
            # 买入第三日不收在突破日收盘之上，卖出
            holds = self.__exit.HoldTime(inst, sigday, tday)
            if holds == 3:
                sigkey = inst + '|' + sigday
                if cls < float(self.__clset[sigkey]):
                    print 'DEBUG:', 'HOLDS', sigkey, tday, holds
                    sellprice = cls
                    return sellprice

            # 熊市背离出场 
            exit = self.__exit.LFpeekBeiLi(inst, tday, high, cls)
            if exit == 1:
                print 'DEBUG:', 'LFBL', inst, tday, cls
                sellprice = cls
                return sellprice

            # 熊市止盈2
            pred = tprice 
            if high > pred * self.__stopwin:
                sellprice = pred * self.__stopwin
                if sellprice < ops:
                    sellprice = ops

        # BIAS止盈 
        if sellprice is None:
            md5120 = self.getMtime()[mkey][26]
            if md5120 != 1024 and cls < md5120:
                print 'DEBUG:', 'MD5120', inst, tday, cls, md5120
                sellprice = cls

        # 止盈1
        if sellprice is None:
            gd20price = self.getMtime()[mkey][21]
            if cls < gd20price:
                sellprice = cls

        if cls < tprice * self.__stoplos:
            print 'DEBUG:', 'STOP_LOSS', inst, nxday, tprice * self.__stoplos 
            sellprice = cls

        return sellprice
#
