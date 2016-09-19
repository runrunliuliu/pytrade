# coding:utf-8
from mock import mockbase
import sys
import os
import os.path
from collections import OrderedDict
from operator import itemgetter


class triangle(mockbase):

    def __init__(self, startday, baseday, codearr, dirs, forcetp):

        self.__stopwin = 1.10
        self.__stoplos = 0.92

        super(triangle,self).__init__(startday, baseday)

        self.__dropout     = {}
        self.__observed    = {}
        self.__qspred      = {}
        self.__qs          = {}
        self.__opset       = {} 
        self.__clset       = {}
        self.__hiset       = {}
        self.__lwset       = {}
        self.__lastdayk    = {}

        subdir = 'triangle'
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            fsize = fname.split('.')
            if len(fsize) > 2:
                continue
            code  = fname[0:8]
            self.loadMtime(dirs, code)
            self.loadQS(dirs, subdir, code)
            self.loadDrop(dirs, subdir, code)
            self.loadOB(dirs, subdir, code)
            self.loadTrades(dirs, subdir, code)

    def initExit(self, mtime, instdaymap, lastdayk):
        self.__exit = None 

    def dumpSelect(self, tups, nday):
        self.__select = None

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

    def initZUHE(self, dirs, subdir):
        qsline = {}
        zuhe  = {}
        ozuhe = []
        zfname = './data/zuhe.txt'
        if os.path.isfile(zfname): 
            for line in open(zfname):
                arr = line.strip().split(' ')
                zuhe[arr[2]] = arr[0]
                ozuhe.append(arr[2])
                code  = arr[2]
                fname = dirs + '/' + subdir + '/' + code + '.trade.csv'
                if os.path.isfile(fname) is False:
                    return
                for line in open(fname):
                    tmp  = line.strip().split(',')
                    day  = tmp[0]
                    if day == zuhe[code]:
                        qsline[code] = (tmp[2],tmp[6])
        return (qsline, zuhe, ozuhe)

    def pred(self, pkey):
        ret = None
        if pkey in self.__qspred:
            ret = float(self.__qspred[pkey])
        return ret

    def filter(self, key):
        ret    = False
        reason = ''
        if key in self.__observed:
            ret    = True
            reason = self.__observed[key]
        return (ret, reason)

    def checkBuy(self, tup, nday):
        ret = True
        inst   = tup[0]
        name   = tup[1]
        score  = tup[2]
        # 1. 过滤分数过低
        if score < 0.0:
            ret = False
        # 2. 过滤反弹高点, 放入观察仓位
        dkey2 = inst + '|' + nday
        if dkey2 in self.__dropout:
            ret = False
            print 'DEBUG:', nday, 'Drop ' + self.__dropout[dkey2], inst, name, dkey2
        return ret

    def buy(self, tup, nxday, nday, tp):
        buyprice = None; ret = True

        inst   = tup[0]
        name   = tup[1]
        dprice = tup[3]
        gprice = tup[4]
        
        ret = self.checkBuy(tup, nday)

        dkey = inst + '|' + nxday
        if dkey not in self.__opset:
            ret = False
            print 'DEBUG:', nday, 'Drop Suspension ', inst, name, nxday, dkey
            return buyprice
        nxopen = float(self.__opset[dkey])
        nclose = float(self.__clset[inst + '|' + nday])
        # 3. 过滤低于T + 1日开盘导致死叉的价格
        if dprice != 'NULL' and nxopen < float(dprice):
            print 'DEBUG:', nday, 'DROP Deadcross', inst, name, nxday, dprice, nxopen  
            ret = False
        # 4. 过滤低于T + 1日开盘形成金叉的价格
        if gprice != 'NULL' and nxopen < float(gprice):
            print 'DEBUG:', nday, 'DROP Goldcross', inst, name, nxday, gprice, nxopen  
            ret = False
        # 5. 过滤低于T + 1日趋势价格的0.99
        pkey = inst + '|' + nday + '|' + tup[5]
        if pkey in self.__qspred and nxopen < self.__qspred[pkey] * 0.99:
            print 'DEBUG:', nday, 'DROP WeakQuShi', inst, name, nxday, self.__qspred[pkey], nxopen  
            ret = False
        # 6. 过滤高空3个点或者低开1个点的价格
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
            # 按次日的收盘价买入
            if tp == 1:
                if bkey in self.__clset:
                    nxclose   = float(self.__clset[bkey])
                    jumpinday = (nxclose - nxopen) / nxopen
                    if jumpinday < 0.09 and jumpinday > -0.03 and nxclose >= self.__qspred[pkey] * 0.99:
                        buyprice = nxclose
                    else:
                        print 'DEBUG:', nday, 'DROP BarClose', inst, name, nxday, nxclose, nxopen, jumpinday 
                        ret = False
        return buyprice 
  
    # flag = 1, T + 1开盘价卖出
    # flag = 2, T + 1盘中低于参考价 ref,卖出
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

    def qsell(self, tup, tupday):
        ret     = 0
        comment = ''
        ref     = -1

        code = tup[0]
        key  = tup[5]
        day2 = tupday[0]
        day1 = tupday[1]
        nday = tupday[2]

        if day1 is None or day2 is None:
            comment = 'nday_None'
            return (ret, comment, ref)
        pkey2 = code + '|' + day2 + '|' + key 
        pkey1 = code + '|' + day1 + '|' + key 
        pkey0 = code + '|' + nday + '|' + key 

        if pkey0 in self.__qs and pkey1 in self.__qs and pkey2 in self.__qs:
            d0 = self.__qs[pkey0]
            d1 = self.__qs[pkey1]
            d2 = self.__qs[pkey2]
            if d0 < 0 and d1 < 0 and d2 < 0:
                skey2 = code + '|' + day2
                skey1 = code + '|' + day1
                skey0 = code + '|' + nday
                cl2 = float(self.__clset[skey2])
                op2 = float(self.__opset[skey2])
                cl1 = float(self.__clset[skey1])
                op1 = float(self.__opset[skey1])
                cl0 = float(self.__clset[skey0])
                op0 = float(self.__opset[skey0])
                if cl0 < cl1 and cl1 < cl2 \
                        and op2 > cl2 and op1 > cl1 and op0 > cl0:
                    ret     = 1
                    comment = 'QS_WORSE'
                    return (ret, comment, -1)
        return (ret, comment, -1)

    def sell(self, tup, tday, nxday, instlast, baseday=None):
        sellprice = None
        tup  = tup[1]
        inst = tup[0]
        if baseday is not None:
            skey = inst + '|' + baseday
            if skey not in self.__clset:
                skey = inst + '|' + self.__lastdayk[inst]
            sellprice = float(self.__clset[skey])
        else:
            if nxday is None:
                return sellprice
            skey = inst + '|' + nxday
            sday = tday
            if skey not in self.__hiset:
                skey = inst + '|' + self.__lastdayk[inst]
                sday = self.__lastdayk[inst]
            high = float(self.__hiset[skey])

            pkey = tup[0] + '|' + sday + '|' + tup[5]
            if pkey not in self.__qspred:
                pkey = instlast[tup[0]] + '|' + tup[5]
            pred = float(self.__qspred[pkey])

            ops  = float(self.__opset[skey])
            low  = float(self.__lwset[skey])

            if high > pred * self.__stopwin:
                sellprice = pred * self.__stopwin
                if sellprice < ops:
                    sellprice = ops

            if low  < pred * self.__stoplos:
                sellprice = pred * self.__stoplos
                if sellprice > ops:
                    sellprice = ops
        return sellprice
    
    def loadQS(self, dirs, subdir, code):
        fname = dirs + '/' + subdir + '/' + code + '.qs.csv'
        if os.path.isfile(fname) is False:
            return 
        for line in open(fname):
            tmp = line.strip().split(',')
            day = tmp[0]

            if self.checkDayRange(day) is False:
                continue

            key = tmp[1] 
            diff = tmp[2]
            pred = tmp[3]
            self.__qs[code + '|' + day + '|' + key]     = float(diff)
            self.__qspred[code + '|' + day + '|' + key] = float(pred)
 
    def loadOB(self, dirs, subdir, code):
        fname = dirs + '/' + subdir + '/' + code + '.ob.csv'
        if os.path.isfile(fname) is False:
            return 
        for line in open(fname):
            tmp = line.strip().split(',')
            day = tmp[1]
            if self.checkDayRange(day) is False:
                continue
            self.__observed[code + '|' + day] = tmp[2]

    def loadDrop(self, dirs, subdir, code):
        fname = dirs + '/' + subdir + '/' + code + '.drop.csv'
        if os.path.isfile(fname) is False:
            return 
        for line in open(fname):
            tmp = line.strip().split(',')
            day = tmp[1]
            if self.checkDayRange(day) is False:
                continue
            self.__dropout[code + '|' + day] = tmp[2]
