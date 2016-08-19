# coding:utf-8
from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from pyalgotrade.technical import priceseg 
from pyalgotrade.technical import xingtai 
from pyalgotrade.technical import qszt 
from pyalgotrade.technical import indicator 
from prettytable import PrettyTable

from collections import OrderedDict
from operator import itemgetter


class MacdSeg(eventprofiler.Predicate):

    def __init__(self, feed, baseinfo):
        self.__macd = {}
        self.__roc  = {}
        self.__gd   = None

        self.__fvalley = None
        self.__fpeek   = None
        self.__desline = None
        self.__incline = None
        self.__dropout = None

        self.__cxshort  = [] 
        self.__observed = [] 
        self.__qushi = []
        self.__dt = []
        self.__nbs = []

        self.__ftDes = None
        self.__ftInc = None
        
        self.__nowdesline = None
        
        self.__baseinfo = baseinfo

        self.__trianglesignal = OrderedDict() 
        self.__qushisignal = OrderedDict() 
        self.__dtsignal = OrderedDict() 
        self.__nbsignal = OrderedDict()
        self.__qsline = OrderedDict()

        self.__qs = []

        for instrument in feed.getRegisteredInstruments():
            bars = feed.getDataSeries(instrument)
            self.__macd[instrument] = priceseg.MacdSegment(bars, 5, inst=instrument)

    def getFtInc(self):
        return self.__ftInc

    def getFtDes(self):
        return self.__ftDes

    def getDropOut(self):
        return self.__dropout

    def getObserved(self):
        return self.__observed

    def getGD(self):
        return self.__gd

    def getValley(self):
        return self.__fvalley

    def getPeek(self):
        return self.__fpeek

    def getHL(self):
        return self.__hlcluster

    def getDesLine(self):
        return self.__desline

    def getNowDesLine(self):
        return self.__nowdesline

    def getNowIncLine(self):
        return self.__nowincline

    def getIncLine(self):
        return self.__incline

    def getCXshort(self):
        return self.__cxshort

    def getQUSHI(self):
        return self.__qushi

    def getDT(self):
        return self.__dt

    def handleTriangle(self, dateTime, triangle, inst, instname):
        rets = None
        score = triangle[0][0]
        
        dprice = 'NULL' 
        if triangle[2] is not None:
            dprice = triangle[2] 
        gprice = 'NULL' 
        if triangle[3] is not None:
            gprice = triangle[3] 
        key    = 'NULL'
        if triangle[4] is not None:
            key = triangle[4].getKey()
            self.__qsline[key] = triangle[4]

        rets = (inst, instname, score, dprice, gprice, key)
        return rets

    def triangleBuySignal(self, dateTime, inst, triangle):
        ret = 0 
        if triangle is None:
            return ret 
        instname = self.__baseinfo.getName(inst) 
        arr = []
        if dateTime in self.__trianglesignal:
            arr = self.__trianglesignal[dateTime]
        tups = self.handleTriangle(dateTime, triangle, inst, instname)
        
        arr.append(tups)
        arr = sorted(arr, key=itemgetter(2), reverse=True)
        self.__trianglesignal[dateTime] = arr 
        return ret

    def handleQUSHI(self, dateTime, qushi, inst, instname):
        rets = None
        score  = qushi[0]
        dprice = 'NULL' 
        gprice = 'NULL' 
        key    = qushi[1] 

        rets = (inst, instname, score, dprice, gprice, key)
        return rets

    def qushiBuySignal(self, dateTime, inst, qushi):
        ret = 0 
        if qushi is None:
            return ret 
        instname = self.__baseinfo.getName(inst) 
        arr = []
        if dateTime in self.__qushisignal:
            arr = self.__qushisignal[dateTime]
        tups = self.handleQUSHI(dateTime, qushi, inst, instname)
        arr.append(tups)
        arr = sorted(arr, key=itemgetter(2), reverse=True)
        self.__qushisignal[dateTime] = arr 
        return ret

    # ----------- DTBOARD -----------------------#
    def handleDT(self, dateTime, dt, inst, instname):
        rets = None
        score  =  dt[1]
        dprice = 'NULL' 
        gprice = 'NULL' 
        key    =  dt[0] 
        rets = (inst, instname, score, dprice, gprice, key)
        return rets

    def dtBuySignal(self, dateTime, inst, dt):
        ret = 0 
        if dt is None:
            return ret 
        instname = self.__baseinfo.getName(inst) 
        arr = []
        if dateTime in self.__dtsignal:
            arr = self.__dtsignal[dateTime]
        tups = self.handleDT(dateTime, dt, inst, instname)
        arr.append(tups)
        arr = sorted(arr, key=itemgetter(2), reverse=True)
        self.__dtsignal[dateTime] = arr 
        return ret

    # ----------- NBS -----------------------#
    def handleNBS(self, dateTime, NBS, inst, instname):
        rets = None
        score  = NBS[1]
        tprice = NBS[2] 
        gprice = NBS[3] 
        key    = NBS[0] 
        rets = (inst, instname, score, tprice, gprice, key)
        return rets

    def nbsBuySignal(self, dateTime, inst, NBS):
        ret = 0 
        # 过滤掉空信号和buy＝0的信号
        if NBS is None or NBS[0] == 0:
            return ret 
        instname = self.__baseinfo.getName(inst) 
        arr = []
        if dateTime in self.__nbsignal:
            arr = self.__nbsignal[dateTime]
        tups = self.handleNBS(dateTime, NBS, inst, instname)
        arr.append(tups)
        arr = sorted(arr, key=itemgetter(2), reverse=True)
        self.__nbsignal[dateTime] = arr 
        return ret
    # ----------- NBS END -----------------------#

    def getTradeSignal(self):
        return (self.__trianglesignal, self.__qushisignal, self.__dtsignal, self.__nbsignal)

    def updateQSdiff(self, nbar, dateTime, dtzq):
        close = nbar.getClose()
        for k, v in self.__qsline.iteritems():
            diff = (close - v.compute(dtzq[dateTime])) / v.compute(dtzq[dateTime])
            incpred = v.compute(dtzq[dateTime] + 1)
            self.__qs.append((dateTime, k, diff * 100, incpred)) 

    def getQS(self):
        return self.__qs

    def parseOb(self, ob):
        # Get The First which is triggle DAY
        if len(ob) > 0:
            for k, v in ob.iteritems():
                if len(v) == 1:
                    self.__observed.append((k, v[0]))

    def eventOccurred(self, instrument, bards):

        dateTime    = bards[-1].getDateTime()
        self.__bars = bards 

        ret = False
        self.__gd        = self.__macd[instrument][-1][0]
        self.__hlcluster = self.__macd[instrument][-1][3]
        self.__fvalley   = self.__macd[instrument][-1][4]
        self.__fpeek     = self.__macd[instrument][-1][5]
        self.__desline   = self.__macd[instrument][-1][6]
        self.__incline   = self.__macd[instrument][-1][7]

        self.__nowdesline = self.__macd[instrument][-1][8]
        self.__nowincline = self.__macd[instrument][-1][9]
        self.__dropout    = self.__macd[instrument][-1][14]

        observed = self.__macd[instrument][-1][17]
        self.parseOb(observed)
       
        cxshort  = self.__macd[instrument][-1][18]
        self.__cxshort.append((dateTime, cxshort))

        qushi = self.__macd[instrument][-1][19]
        self.__qushi.append((dateTime, qushi))
        
        dt = self.__macd[instrument][-1][20]
        self.__dt.append((dateTime, dt))

        NBS = self.__macd[instrument][-1][21]
        self.__nbs.append((dateTime, NBS))

        self.__ftDes = self.__macd[instrument][-1][15]
        self.__ftInc = self.__macd[instrument][-1][16]

        # Indicators
        vbeili   = self.__macd[instrument][-1][10]
        triangle = self.__macd[instrument][-1][11]
        instroc  = self.__macd[instrument][-1][12]
        dtzq     = self.__macd[instrument][-1][13]
        
        ret1 = self.triangleBuySignal(dateTime, instrument, triangle)
        ret2 = self.qushiBuySignal(dateTime, instrument, qushi)
        ret3 = self.dtBuySignal(dateTime, instrument, dt)
        ret4 = self.nbsBuySignal(dateTime, instrument, NBS)

        # print 'DEBUG', dateTime, self.__dtsignal

        self.updateQSdiff(bards[-1], dateTime, dtzq)

        self.__roc[instrument] = instroc

        if vbeili == 1:
            print "EVENT OK", dateTime, instrument, ret1, ret2, ret3, ret4
            ret = True
        return ret
#
