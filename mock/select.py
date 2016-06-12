# coding:utf-8
import sys
import os
from collections import OrderedDict
from operator import itemgetter
from prettytable import PrettyTable


class select(object):

    def __init__(self, baseday, codearr, dirs, trade):

        self.__stopwin = 1.10
        self.__stoplos = 0.92

        self.__tradesignal = OrderedDict()
        self.__dropout   = {}
        self.__observed  = {}
        self.__qspred    = {}
        self.__qs        = {}
        self.__opset     = {} 
        self.__clset     = {}
        self.__hiset     = {}
        self.__lwset     = {}
        self.__baseday   = baseday

        # load zuhe
        self.__qsline = {}
        self.__zuhe  = {}
        self.__ozuhe = []
        for line in open('./data/zuhe.txt'):
            arr = line.strip().split(' ')
            self.__zuhe[arr[2]] = arr[0]
            self.__ozuhe.append(arr[2])
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            fsize = fname.split('.')
            if len(fsize) > 2:
                continue
            code  = fname[0:8]
            self.loadDayK(dirs, code)

        self.__trade = trade
        self.__trade.initDayK(self.__opset, self.__hiset, self.__lwset, self.__clset, self.__lastdayk)
        self.__tradesignal = self.__trade.getTrades() 
        self.__mtime  = self.__trade.getMtime()

    def buy(self, tup, nxday, nday):
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
            print 'DEBUG:', nday, 'Drop ' + self.__dropout[dkey2], inst, name, nxday, dkey2

        return ret 
   
    def select(self):
        zuhe = PrettyTable(['T日', '代码', '名称', '止盈价', '止损价'])
        zuhe.float_format = '.4'
        zuhe.align = 'l'
        for k in self.__ozuhe:
            if k in self.__qsline:
                key = self.__qsline[k]
                pkey = k + '|' + self.__baseday + '|' + key[1]
                pred = self.__qspred[pkey]
                stopwin = pred * self.__stopwin 
                stoplos = pred * self.__stoplos 
                zuhe.add_row([self.__baseday, k, key[0], stopwin, stoplos]) 
        print zuhe

        zuhe = PrettyTable(['T日', '代码', '名称', '买入区间'])
        zuhe.float_format = '.4'
        zuhe.align = 'l'
        nday = self.__baseday
        tups = self.__tradesignal[nday] 
        for t in tups:
            nclose = float(self.__clset[t[0] + '|' + nday])
            pkey = t[0] + '|' + nday + '|' + t[5]
            tmp  = (t[3], t[4], self.__qspred[pkey] * 0.99, nclose * 0.99)
            tmin = "{:.4f}".format(self.maxTup(tmp))
            tmax = "{:.4f}".format(nclose * 1.03)
            if tmax < tmin:
                print 'DEBUG:','Drop Buy', t[0], t[1], tmin, tmax, nday
                continue
            price = '[' + str(tmin) + ' ' + str(tmax) + ']'
            zuhe.add_row([nday, t[0], t[1], price])
        print zuhe

    def loadDayK(self, dirs, code):
        day = 0; op  = 0; cl  = 0
        cnt = 0
        fname = dirs + '/' + code + '.csv'
        for line in open(fname):
            if cnt == 0:
                cnt = cnt + 1
                continue
            tmp  = line.strip().split(',')
            day = tmp[0]
            if day != self.__baseday:
                continue
            op  = tmp[1]
            hi  = tmp[2]
            lw  = tmp[3]
            cl  = tmp[4]
            self.__opset[code + '|' + day] = op
            self.__clset[code + '|' + day] = cl 
            self.__hiset[code + '|' + day] = hi
            self.__lwset[code + '|' + day] = lw 
            cnt = cnt + 1
#
