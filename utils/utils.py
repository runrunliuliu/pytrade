# coding:utf-8
import sys
import os
import math
import json
import time
import datetime
import numpy as np
from collections import OrderedDict
from operator import itemgetter
from prettytable import PrettyTable
from mock.triangle import triangle 
from random import shuffle


class TimeUtils(object):

    def tostring(self,datetime):
        return datetime.strftime('%Y-%m-%d')

    def string_toDatetime(self,string):
        return datetime.datetime.strptime(string, "%Y-%m-%d")

    """两个日期的比较, 当然也可以用timestamep方法比较,都可以实现."""
    def compare_dateTime(self,dateStr1,dateStr2):
        date1 = self.string_toDatetime(dateStr1)
        date2 = self.string_toDatetime(dateStr2)
        return date1.date() > date2.date()

    def comparedt(self,dateStr1,dateStr2, formats):
        date1 = datetime.datetime.strptime(dateStr1, formats)
        date2 = datetime.datetime.strptime(dateStr2, formats)
        return date1.date() < date2.date()

    """把字符串转成时间戳形式"""
    def string_toTimestamp(self,strTime):
        return time.mktime(self.string_toDatetime(strTime).timetuple())

    """ 指定日期加上 一个时间段，天，小时，或分钟之后的日期 """
    def dateTime_before(self,dateStr,days=0,hours=0,minutes=0):
        date1 = self.string_toDatetime(dateStr)
        date1 = date1 - datetime.timedelta(days=days,hours=hours,minutes=minutes)
        return date1.strftime("%Y-%m-%d")


class FileUtils(object):

    def __init__(self,basedir,path,outdir):
        self.outdir  = outdir
        self.basedir = basedir
        self.path    = path
        self.doneset = set()
        self.donedict = dict()

    def loadones(self):
        self.doneset  = self.os_walk('./output/done/' + self.path)

    def checkdone(self,ymd,code):
        [year,month,day] = ymd.split('-')
        datadir = self.basedir + '/output/' + self.path + '/' + code  + '/' + year
        check = code + '-' + year + '-' + ymd + '.done'
        if check in self.doneset:
            print >> sys.stderr, check + ' ' + ymd + ' is done...'
            return [0,0]
        return [datadir,year]

    def getpath(self,files,dirs):
        tmp  = files[:-4].split('-')
        code = tmp[0]
        year = tmp[2]
        mon  = tmp[3]
        day  = tmp[4]
        ymd  = year + '-' + mon + '-' + day

        pathf = code + '/' + year + '/' + ymd + '.txt'
        pathf = dirs + '/' + pathf

        return [ymd,pathf]

    def lsfolder(self,top_dir):
        return os.listdir(top_dir)

    def doneflag(self):
        for k,v in self.donedict.iteritems():
            donedir = self.outdir + '/output/done/' + self.path + '/' + v 
            if not os.path.exists(donedir):
                os.makedirs(donedir)
            with open(donedir + '/' + k.split('/')[-1], "w") as myfile:
                myfile.close() 

    def loadfiles(self):
        codes = self.lsfolder(self.basedir)
        paths = []
        
        for c in codes:
            files = self.os_walk(self.basedir + '/' + c)
            for f in files:
                [ymd,pathf] = self.getpath(f,self.basedir)
                [datadir,year] = self.checkdone(ymd,c)
                if year == 0:
                    continue 
                paths.append(pathf)
        return paths

    def os_walk(self,top_dir):  
        output = set() 
        for parent, dirnames, filenames in os.walk(top_dir):  
            for filename in filenames:
                xfile = os.path.abspath(os.path.join(parent, filename))  
                output.add('-'.join(xfile.split('/')[-3:]))
        return output


class DumpFeature(object):

    def __init__(self, obj, instfiles, dirpath, period):
        self.__inst   = instfiles
        self.__dir    = dirpath
        self.__period = period

        self.__gd = obj.getGD()
        self.__hl = obj.getHL()
        self.__peek   = obj.getPeek()
        self.__valley = obj.getValley()
        self.__desline = obj.getDesLine()
        self.__incline = obj.getIncLine()
        self.__nowdesc = obj.getNowDesLine()
        self.__nowinc  = obj.getNowIncLine()
        self.__trade   = obj.getTradeSignal()
        self.__qs      = obj.getQS()
        self.__dropout = obj.getDropOut()

        self.__cxshort = obj.getCXshort()
        self.__qcg     = obj.getQCG()
        self.__xingtai = obj.getXINGTAI()

        self.__indicator = obj.getIndicator()
        
        self.__qushi = obj.getQUSHI()
        self.__dt    = obj.getDT()

        self.__observed = obj.getObserved()

        self.__ftDes = obj.getFtDes()
        self.__ftInc = obj.getFtInc()

    def ToDump(self):

        self.GD2csv()
        self.HlCluster2csv()

        self.Vetex2csv(self.__peek, 'peek')
        self.Vetex2csv(self.__valley, 'valley')

        self.QSLine2csv(self.__desline, 'des')
        self.QSLine2csv(self.__incline, 'inc')
        self.QSLine2csv(self.__nowdesc, 'ndes')
        self.QSLine2csv(self.__nowinc, 'ninc')

        # 上升三角策略
        self.TradeSignal2csv('triangle', 0, 'trade')
        self.QS2csv('triangle', 0, 'qs')
        self.Drop2csv('triangle', 0, 'drop')
        self.Ob2csv('triangle', 0, 'ob')
        self.CX2csv('mtime')
        self.QCG2csv('qcg')
        self.XT2csv('xingtai')
        self.redisXT2csv('xingtai')
        # self.ind2csv('indicator')

        # 趋势线策略 
        self.TradeSignal2csv('qushi', 1, 'trade')
        
        # 龙虎榜策略 
        self.TradeSignal2csv('dtboard', 2, 'trade')

        # NBS策略 
        self.TradeSignal2csv('nbs', 3, 'trade')

        # K-LINE策略 
        self.TradeSignal2csv('kline', 4, 'trade')

        # MHead策略 
        self.TradeSignal2csv('mhead', 5, 'trade')

    def QCG2csv(self, subdir):
        dirs = self.__dir + '/' + subdir 
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.ft.csv', 'w')
        f.write('1date,2kdj,3macd1,4sxy,5zdf,6td1,7td2,8td3,9macd2,10macd3,11macd4,' \
                + '12macd5,13macd6,14macd7\n')
        for item in self.__qcg:
            if item is not None and item[1] is not None:
                v = item[1]
                out = ''
                for t in v:
                    out = out + ',' + str(t)
                f.write(item[0].strftime('%Y-%m-%d') + out)
                f.write('\n')

    def XT2csv(self, subdir):
        dirs = self.__dir + '/' + subdir
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.xingtai.csv', 'w')
        for cx in self.__xingtai:
            k = cx[0]
            v = cx[1]
            if v is None:
                continue
            out = json.dumps(v)
            dd  = k.strftime('%Y-%m-%d')
            if self.__period == '30min':
                dd  = k.strftime('%Y-%m-%d-%H-%M')
            if self.__period == '60min':
                dd  = k.strftime('%Y-%m-%d-%H-%M')
            f.write(dd + '\t' +  out)
            f.write('\n')
        f.close()

    # Deprace Dump indicator format
    def ind2csv(self, subdir):
        dirs = self.__dir + '/' + subdir
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.csv', 'w')

        for cx in self.__indicator:
            k = cx[0]
            v = cx[1]
            if v is None:
                continue
            # MA
            ma = v[0]
            dd  = k.strftime('%Y-%m-%d')

            arr = [] 
            for i in [5, 10, 20, 30, 60, 90, 120, 250]:
                val = '-1'
                if i in ma:
                    val = "{:.2f}".format(ma[i])
                arr.append(val)
            out = ','.join(arr)
            f.write(dd + ',' +  out)
            f.write('\n')
        f.close()

    # Dump AS redis format
    def redisXT2csv(self, subdir):
        dirs = 'output/redis/' + self.__dir + '/' + subdir
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.xingtai.csv', 'w')
        for cx in self.__xingtai:
            k = cx[0]
            v = cx[1]
            if v is None:
                continue
            out = json.dumps(v)
            dd  = k.strftime('%Y-%m-%d')
            if self.__period == '30min':
                dd  = k.strftime('%Y-%m-%d-%H-%M')
            if self.__period == '60min':
                dd  = k.strftime('%Y-%m-%d-%H-%M')
            f.write(self.__inst[0][1] + '_' + dd + '\t' +  out)
            f.write('\n')
        f.close()

    def CX2csv(self, subdir):
        dirs = self.__dir + '/' + subdir 
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.cxshort.csv', 'w')
        f.write('1Date,2cdif,3cdea,4Bear,5cxShort,6wsma5,7yby,8gfbl,9gfscore,' + \
                '10xingtai,11vret,12vscore,13nvpos,14pret,15pscore,16nppos,17slope,'  + \
                '18dma250,19pma250,20prext,21tkdk,22tkdf,23ma20GD,24lfbl,25lfblhi,26lfblcl,27qsell,' + \
                '28md5120,29tfbl,30fibs,31bias5120,32fbprice,33fbpress,34bddf,35goldseg,' + \
                '36ma5d,37peekzl,38pqs,39nqs\n')
        for cx in self.__cxshort:
            k = cx[0]
            v = cx[1]
            if v is None:
                continue
            out = ''
            for t in v:
                out = out + ',' + str(t)
            f.write(k.strftime('%Y-%m-%d') + out)
            f.write('\n')
        f.close()

    def GD2csv(self):
        f = open(self.__dir + self.__inst[0][1] + '.gd.csv', 'w')
        f.write('Date,GD\n')
        for k,v in self.__gd.iteritems():
            f.write(k.strftime('%Y-%m-%d %H:%M:%S') + ',' + str(v))
            f.write('\n')
        f.close()
    
    def Drop2csv(self, subdir, index, name):
        dirs = self.__dir + '/' + subdir 
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.' + name + '.csv', 'w')
        for k in self.__dropout:
            date   = k[0].strftime('%Y-%m-%d')
            reason = k[1]
            f.write(self.__inst[0][1] + ',' +  date + ',' + reason)
            f.write('\n')
        f.close()
 
    def Ob2csv(self, subdir, index, name):
        dirs = self.__dir + '/' + subdir 
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.' + name + '.csv', 'w')
        for o in self.__observed:
            reason = o[0]
            date   = o[1].strftime('%Y-%m-%d')
            f.write(self.__inst[0][1] + ',' +  date + ',' + reason)
            f.write('\n')
        f.close()
   
    def QS2csv(self, subdir, index, name):
        dirs = self.__dir + '/' + subdir 
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.' + name + '.csv', 'w')
        for k in self.__qs:
            date = k[0].strftime('%Y-%m-%d')
            key  = k[1]
            diff = k[2]
            pred = k[3]
            f.write(date + ',' + key + ',' + str(diff) + ',' + str(pred))
            f.write('\n')
        f.close()
    
    def HlCluster2csv(self):
        f = open(self.__dir + self.__inst[0][1] + '.hcluster.csv', 'w')
        f.write('id,mean,median,std,num\n')
        for k in self.__hl:
            ids    = k[0]
            mean   = k[1]
            median = k[2]
            std    = k[3]
            num    = k[4]
            f.write(str(ids) + ',' + str(mean) + ',' + str(median) + ',' + str(std) + ',' + str(num))
            f.write('\n')
        f.close()
    
    def Vetex2csv(self, lists, name):
        f = open(self.__dir + self.__inst[0][1] + '.' + name + '.csv', 'w')
        f.write('Date,val,pre,nex\n')
        for k in lists:
            date = k[0]
            val  = k[1]
            pre  = k[2]
            nex  = k[3]
            f.write(date.strftime('%Y-%m-%d') + ',' + str(val) + ',' + str(pre) + ',' + str(nex))
            f.write('\n')
        f.close()
    
    def QSLine2csv(self, dicts, name):
        f = open(self.__dir + self.__inst[0][1] + '.' + name + '.csv', 'w')
        pred = 0.0
        f.write('d1,v1,d2,v2,t1\n')
        for k,val in dicts.iteritems():
            for v in val:
                d1 = v[0]
                v1 = v[1]
                d2 = v[2]
                v2 = v[3]
                fkey = d1.strftime('%Y-%m-%d') + '|' +  d2.strftime('%Y-%m-%d')
                if name == 'ndes' or name == 'ninc':
                    if fkey not in self.__ftDes and fkey not in self.__ftInc:
                        continue
                    if fkey in self.__ftDes:
                        pred = self.__ftDes[fkey]
                    if fkey in self.__ftInc:
                        pred = self.__ftInc[fkey]
                f.write(d1.strftime('%Y-%m-%d') + ',' + str(v1) + ',' + d2.strftime('%Y-%m-%d') + ',' + str(v2) + ',' + str(pred))
                f.write('\n')
        f.close()

    def TradeSignal2csv(self, subdir, index, name):
        dirs = self.__dir + '/' + subdir 
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        f = open(dirs + '/' + self.__inst[0][1] + '.' + name + '.csv', 'w')
        for k,val in self.__trade[index].iteritems():
            for v in val:
                d1 = v[0]
                d2 = 'NULL'
                if v[1] is not None:
                    d2 = v[1].encode('utf8')
                d3 = str(v[2])
                d4 = str(v[3])
                d5 = str(v[4]) 
                d6 = str(v[5]) 
                d  = d1 + ',' + d2 + ',' + d3 + ',' + d4 + ',' + d5 + ',' + d6
                f.write(k.strftime('%Y-%m-%d') + ',' + d) 
                f.write('\n')
        f.close()


class FakeTrade(object):
    
    def __init__(self, codearr, dirs, startday, baseday, trade, forcetp):
        self.__zuhe   = []
        self.__switch = []

        self.__stopwin     = 1.13
        self.__stoplos     = 0.92
        self.__bearstopwin = 1.05
        self.__bearstoplos = 0.92
        self.__numzuhe     = 4
        self.__maxbuy      = 1

        if trade.getName() == 'nbs':
            self.__stopwin     = 1.05
            self.__stoplos     = 0.97
            self.__bearstopwin = 1.11
            self.__bearstoplos = 0.89
            self.__numzuhe     = 6
            self.__maxbuy      = 3

        if trade.getName() == 'kline':
            self.__numzuhe = 6
            self.__maxbuy  = 3

        self.__forcetp = forcetp 

        self.__cashbase  = 300000
        self.__cashtotal = self.__cashbase 
        self.__cashused  = 0

        self.__btdir  = './backtests'

        # bear = 1 熊市
        self.__bear   = 0
        self.__bearma = 0
        self.__openHD = 1 

        self.__days   = []
        self.__daymap = {}
        self.__mapday = {}

        self.__holds   = {}
        
        self.__instdaymap = {}
        self.__instmapday = {}
        self.__instdays   = {}
        self.__instlast   = {}
  
        self.__opset       = {} 
        self.__clset       = {}
        self.__hiset       = {}
        self.__lwset       = {}
        self.__lastdayk    = {}
       
        self.__preturns = None
        self.__startday = startday
        self.__baseday  = baseday

        self.__sdate = datetime.datetime.strptime(startday, "%Y-%m-%d")
        self.__edate = datetime.datetime.strptime(baseday, "%Y-%m-%d")

        self.__prefix = self.__sdate.strftime('%Y%m%d') + '_' + self.__edate.strftime('%Y%m%d')

        self.tradedays(dirs)

        self.__codemap = dict()
        self.__codearr = []

        num = 0
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            fsize = fname.split('.')
            if len(fsize) > 2:
                continue
            code  = fname[0:8]
            fname = dirs + '/' + code + '.csv'
            self.loadDayK(fname, code)
            
            self.__codearr.append(code)
            self.__codemap[code] = num
            num = num + 1

        self.__trade = trade
        self.__trade.initDayK(self.__opset, self.__hiset, self.__lwset, self.__clset, self.__lastdayk)

        self.__tradesignal = self.__trade.getTrades() 
        self.__mtime  = self.__trade.getMtime()

        self.__trade.initExit(self.__mtime, \
                              self.__instdaymap, \
                              self.__lastdayk)

    def checkDayRange(self, day):
        ret = True 
        date = datetime.datetime.strptime(day, "%Y-%m-%d")
        if date.date() < self.__sdate.date():
            ret = False 
        if date.date() > self.__edate.date():
            ret = False
        return ret

    def loadDayK(self, fname, code):
        day = 0; op  = 0; cl  = 0
        cnt = 0; daymap = {}; mapday = {}; days = []
        for line in open(fname):
            if cnt == 0:
                cnt = cnt + 1
                continue

            tmp  = line.strip().split(',')

            if self.checkDayRange(tmp[0]) is False:
                continue
            
            day = tmp[0]
            op  = tmp[1]
            hi  = tmp[2]
            lw  = tmp[3]
            cl  = tmp[4]
            self.__opset[code + '|' + day] = op
            self.__clset[code + '|' + day] = cl 
            self.__hiset[code + '|' + day] = hi
            self.__lwset[code + '|' + day] = lw 
            days.append(day)
            daymap[day] = cnt 
            mapday[cnt] = day 
            cnt = cnt + 1

        self.__instdaymap[code] = daymap
        self.__instmapday[code] = mapday
        self.__instdays[code]   = days 
        self.__lastdayk[code] = day

    def tradedays(self, path):
        cnt  = 0
        for line in open(path + '/ZS000001.csv'):
            tmp = line.strip().split(',')
            day = tmp[0]
            self.__days.append(day)
            self.__daymap[day] = cnt 
            self.__mapday[cnt] = day 
            cnt = cnt + 1

    def buy(self, tup, nxday, nday):
        tp = 0
        # if len(self.__zuhe) > 0:
        #    tp = 1
        buyprice = None
        buyprice = self.__trade.buy(tup, nxday, nday, tp)
        return buyprice 

    def sell(self, tup, tday, nxday, yday, baseday=None):
        sellprice = None
        sellprice = self.__trade.sell(tup, tday, nxday, self.__instlast, yday)
        return sellprice

    def updateStopWinLoss(self, tp):
        winn = self.__stopwin
        loss = self.__stoplos
        if self.__bear == 1 and tp != -1:
            winn = self.__bearstopwin 
            loss = self.__bearstoplos
        return (winn, loss)

    def updateBB(self, nday):
        bbkey = 'ZS000001|' + nday
        if bbkey in self.__mtime:
            ddif = float(self.__mtime[bbkey][0])
            ddea = float(self.__mtime[bbkey][1])

            self.__bear   = int(self.__mtime[bbkey][2])
            self.__bearma = int(self.__mtime[bbkey][3])
            tkdk = float(self.__mtime[bbkey][19])
            if tkdk < 0.0 and ddif < 0:
                self.__openHD = 0 
            else:
                if self.__openHD == 0:
                    if ddif > 0 and ddea > 0: 
                        self.__openHD = 1

    # 换仓
    def switchout(self, nday, yday, nxday, forcetp):
        flag = 0
        zuhe = []
        if len(self.__zuhe) == 0:
            return (flag, zuhe)
        
        # 根据市场情况设置不同的止盈和止损价位
        (winn, loss) = self.updateStopWinLoss(forcetp)

        for z in self.__zuhe:
            # 初始化trade的止盈止损
            self.__trade.setStop(winn, loss)

            (yday, nxday) = self.getDays(z[1][0], nday)
            buy    = z[2]
            shares = z[3]
            sp  = self.sell(z, nday, nxday, yday)

            (ret, comment, ref) = self.forceDrop(z[1], nday, forcetp + 1, nxday)
            if ret > 0:
                sp1 = self.__trade.forceSell(z[1], nday, nxday, ret, ref)
                sp = (sp1 if (sp is None or sp1 is None or sp1 > sp) else sp)
                if sp is not None:
                    print 'DEBUG:', nday, 'Switch', comment, z[1][0], nxday, sp, buy
            if sp is None:
                print 'DEBUG:', nday, 'Keep_ZUHE', z[1][0], nxday, buy
                zuhe.append(z)
            else:
                print 'DEBUG:', nday, 'Switch', z[1][0], nxday, sp, buy

                self.__cashused  = self.__cashused - buy * shares

                self.__switch.append((z, buy, sp, (sp-buy)/buy, nxday, shares))
                if z[1][0] in self.__holds:
                    del self.__holds[z[1][0]]
                if sp <= buy:
                    flag = 1
                else:
                    flag = 2
        return (flag, zuhe)

    def getDays(self, inst, nday):
        daymap = self.__instdaymap[inst]
        mapday = self.__instmapday[inst]
        yday  = None
        nxday = None
        if nday not in daymap:
            return (yday, nxday)
        bcnt  = daymap[nday]
        if (bcnt - 1) in mapday:
            yday  = mapday[bcnt - 1]
        if (bcnt + 1) in mapday:
            nxday = mapday[bcnt + 1]
        return (yday, nxday)

    def trackZH(self, nday, retslog):
        trades = [] 
        returns = 0.0

        self.__cashtotal = self.__cashbase 
        for s in self.__switch:
            returns = returns + 100 * float(s[3])
            buy    = float(s[1])
            sel    = float(s[2])
            shares = int(s[5])
            self.__cashtotal = (sel - buy) * shares + self.__cashtotal - 0.0015 * sel * shares

        fuying = 0
        if len(self.__zuhe) == 0:
            cash = self.__cashtotal + fuying
            fuli = 100 * (cash - self.__cashbase) / (self.__cashbase + 0.0)
            tup = None
            if self.__preturns is None:
                tup = (nday, 0, 0.0, 0.0, cash, fuli)
            else:
                tup = (nday, 0, 0.0, returns / 10.0, cash, fuli)
            retslog.append(tup)
            return trades 

        for z in self.__zuhe:
            sigday = z[0]
            tup    = z[1]
            shares = z[3]
            inst   = tup[0]
            name   = tup[1]
            (yday, bday) = self.getDays(inst, sigday)
            buy = float(self.__opset[inst + '|' + bday])
            
            skey = inst + '|' + nday
            if skey not in self.__clset:
                skey = self.__instlast[inst]

            sel = float(self.__clset[skey])
            roc = 100 * (sel - buy) / buy
            returns = returns + roc
            
            fuying = (sel - buy) * shares + fuying
            
            loss = 'NULL'
            self.__instlast[inst] = skey 
            trades.append((nday, sigday, inst, name, tup[2], buy, sel, roc, loss, tup[5], shares))

        # 计算复利
        cash = self.__cashtotal + fuying
        fuli = 100 * (cash - self.__cashbase + 0.0) / self.__cashbase 

        holds  = len(self.__zuhe)
        self.__preturns = (holds, returns / holds, returns / 10.0, cash, fuli)
        retslog.append((nday, holds, returns / holds, returns / 10.0, cash, fuli)) 
        return trades

    def sztime(self, nday, tp):
        ret     = 0
        comment = ''
        ref     = -1
        if tp == 5 and self.__bearma == 1:
            comment = 'No Buy Bear_Market_MA_WORSE'
            ret = 1
        if tp == 6 and self.__bearma == 1:
            comment = 'Clear Holds Bear_Market_MA_WORSE'
            ret = 1 
        if tp == 5 and self.__openHD == 0:
            comment = 'No Buy TKDK_Market_QUSHI_WORSE'
            ret = 1
        if tp == 6 and self.__openHD == 0:
            comment = 'Clear Holds TKDK_Market_QUSHI_WORSE'
            ret = 1
        return (ret, comment, ref)

    # 满足mtime某些条件，强制平仓或者放弃买入
    # tp 奇数: 买入
    # tp 偶数: 调仓
    def mtime(self, code, nday, tp, nxday):
        ret     = 0
        comment = ''
        ref     = -1
        yby     = 1000
        gfbeili = -1

        tkdk = 1024
        qsxt = 0
        vret = -1 
        pret = -1 
        bbkey = code + '|' + nday
        if bbkey in self.__mtime:
            yby     = float(self.__mtime[bbkey][5])
            gfbeili = float(self.__mtime[bbkey][6])
            gfscore = float(self.__mtime[bbkey][7])
            
            qsxt = float(self.__mtime[bbkey][8])
            vret = float(self.__mtime[bbkey][9])
            pret = float(self.__mtime[bbkey][12])

            dma250 = float(self.__mtime[bbkey][16])
            pma250 = float(self.__mtime[bbkey][17])
            
            prext  = float(self.__mtime[bbkey][18])
            comxt  = str(prext) + '|' +  str(qsxt)
            
            tkdk = float(self.__mtime[bbkey][19])

            pqs   = self.__mtime[bbkey][36]
            nqs   = self.__mtime[bbkey][37]
            comqs = str(pqs) + '|' + str(nqs) 

            # -------------- 买入 ---------------------------
            if tp == 1 and self.__bear == 1 and yby < -0.02:
                comment = 'No Buy Bear_Market_YBY'
                ret = 1
                return (ret, comment, ref)
            if tp == 7 and self.__bear == 1 and (vret + pret) == 2:
                comment = 'No Buy Bear_Market_BelowQS'
                ret = 1
                return (ret, comment, ref)
            if tp == 7 and self.__bear == 1 and (qsxt == 301 or qsxt == 103 or qsxt == 202) and (vret + pret) == 1:
                comment = 'No Buy Bear_Market_InDescQS_' + str(qsxt)
                ret = 1
                return (ret, comment, ref)
            if tp == 7 and dma250 <= 0.00005 and pma250 > -0.10 and pma250 < 0.08: 
                comment = 'No Buy ALL_Market_Around_DesMA250'
                ret = 1
                return (ret, comment, ref)
            if tp == 7 and (comxt == '101.0|102.0' or comxt == '301.0|302.0'): 
                comment = 'No Buy ALL_Market_' + comxt
                ret = 1
                return (ret, comment, ref)
            if comqs == '1302.0|2303.0':
                comment = 'No Buy ALL_Market_COMQS_' + comqs
                ret = 1
                return (ret, comment, ref)

        # -------------- 调仓 ---------------------------
        if tp == 8 and self.__bear == 1 and ((vret + pret) == 2 or (qsxt == 202 and (vret + pret) == 1)):
            comment = 'No Hold Bear_Market_TurnInto_' + str(qsxt)
            ret = 1
            return (ret, comment, ref)
        if tp == 8 and self.__bear == 1 and tkdk < 0.0:
            comment = 'No Hold Bear_Market_TKDK_' + str(tkdk)
            ret = 1
            return (ret, comment, ref)

        if tp == 2 and self.__bear == 1 and yby < -0.02:
            if nday in self.__tradesignal:
                tups = self.__tradesignal[nday] 
                for t in tups: 
                    if code == t[0]:
                        comment = 'No Hold Bear_Market_YBY'
                        ret = 1
                        return (ret, comment, ref)
        if tp == 2 and self.__bear == 1 and gfbeili > 0 and gfscore > 2.0:
            comment = 'No Hold GeFeng_BeiLI'
            ret = 2 
            return (ret, comment, gfbeili)
        return (ret, comment, ref)

    def qSell(self, tup, nday, tp):
        code = tup[0]
        (day1, nouse) = self.getDays(code, nday)
        (day2, nouse) = self.getDays(code, day1)
        return self.__trade.qsell(tup, (day2, day1, nday))

    def forceDrop(self, tup, nday, tp, nxday=None):
        ret     = 0
        comment = ''
        ref     = -1
        code    = tup[0]
        # tp = [1,2] --- qs mtime
        # tp = [3,4] --- qs sell
        # tp = [5,6] --- 上证择时
        # tp = [7,8] --- qs择时,先做上证择时
        if tp == 1 or tp == 2:
            (ret, comment, ref) = self.mtime(code, nday, tp, nxday)
        if tp == 4:
            (ret, comment, ref) = self.qSell(tup, nday, tp)
        if tp == 5 or tp == 6:
            (ret, comment, ref) = self.sztime(nday, tp)
        if tp == 7 or tp == 8:
            if tp == 7:
                szret = self.sztime(nday, 5)
                if szret[0] == 1:
                    return szret
                else:
                    (ret, comment, ref) = self.mtime(code, nday, tp, nxday)
            if tp == 8:
                szret = self.sztime(nday, 6)
                if szret[0] == 1:
                    return szret
                else:
                    (ret, comment, ref) = self.mtime(code, nday, tp, nxday)
        return (ret, comment, ref)

    def triangleSelect(self, dirs, subdir, forcetp):
        (qsline, zuhe, ozuhe) = self.__trade.initZUHE(dirs, subdir)
        
        nday = self.__baseday
        self.updateBB(nday)
        (winn, loss) = self.updateStopWinLoss(forcetp)

        tzuhe = PrettyTable(['T日', '代码', '名称', '止盈价', '止损价'])
        tzuhe.float_format = '.4'
        tzuhe.align = 'l'
        for k in ozuhe:
            if k in qsline:
                key = qsline[k]
                tup = (k,)
                (ret, comment, ref) = self.forceDrop(tup, nday, forcetp + 1)
                if ret == 1:
                    print 'DEBUG:', nday, k, key[0], comment, 'Sell on OPEN' 
                    continue
                if ret == 2:
                    print 'DEBUG:', nday, k, key[0], comment, 'Sell on', ref 
                    continue
                pkey = k + '|' + self.__baseday + '|' + key[1]
                pred = self.__trade.pred(pkey)
                stopwin = pred * winn
                stoplos = pred * loss
                tzuhe.add_row([self.__baseday, k, key[0], stopwin, stoplos]) 
        print tzuhe

        tzuhe = PrettyTable(['T日', '代码', '名称', '得分', '收益率', '持有天数', '开仓价', '止盈价', '止损价', '手数'])
        tzuhe.float_format = '.4'
        tzuhe.align = 'l'
        nday = self.__baseday
        tups  = self.__tradesignal[nday] 
        ftups = []
        for t in tups:
            check = self.__trade.checkBuy(t, nday)
            if check is False:
                continue
            (flag, comment, ref) = self.forceDrop(t, nday, forcetp)
            if flag == 1:
                print 'DEBUG:', nday, comment, t[0], t[1], t[2]
                continue
            ftups.append(t)
        self.printNextDay(nday, ftups, tzuhe)
        print tzuhe

    def qushiClassiz(self, tups):
        buys  = []
        holds = []
        sells = []

        for t in tups:
            if t[5] == '1':
                buys.append(t)
            if t[5] == '0':
                holds.append(t)
            if t[5] == '-1':
                sells.append(t)
        return (buys, holds, sells)

    def qushiDump(self, buys, holds, sells):
        nday = self.__baseday
        f = open('./output/qushi/' + nday + '.qushi.csv', 'w')
        def dump(f, arr, act):
            for i in arr:
                tmp = i[1]
                out = i[0] + ',' + tmp + ',' + act
                f.write(out)
                f.write('\n')
        dump(f, buys, 'BUY')
        dump(f, holds, 'HOLD')
        dump(f, sells, 'SELL')
        f.close()

    def qushiSelect(self, dirs, subdir, forcetp):
        (zuhe, ozuhe) = self.__trade.initZUHE(dirs, subdir, forcetp)
        nday = self.__baseday
        tups  = self.__tradesignal[nday] 
        # FINAL OUTPUT
        (buys, holds, sells) = self.qushiClassiz(tups)
        self.qushiDump(buys, holds, sells)

    # NBS select
    def nbSelect(self, dirs, subdir, forcetp):
        (zuhe, ozuhe) = self.__trade.initZUHE(dirs, subdir, forcetp)
        nday = self.__baseday

        # 更新择时
        self.updateBB(nday)
        szbuy = self.sztime(nday, 5)
        self.__trade.upSZmtime(szbuy, self.__bear)

        (winn, loss) = self.updateStopWinLoss(forcetp)

        tup = (zuhe, ozuhe, winn, loss)
        self.__trade.select(tup, nday)

    # Kline select
    def klSelect(self, dirs, subdir, forcetp):
        (zuhe, ozuhe) = self.__trade.initZUHE(dirs, subdir, forcetp)
        nday = self.__baseday

        (yday, nxday) = self.getDays('ZS000001', nday)
        tup = (zuhe, ozuhe, yday)

        self.__trade.select(tup, nday)

    def select(self, dirs, subdir, forcetp, trade):
        if trade == 'triangle':
            self.triangleSelect(dirs, subdir, forcetp)
        if trade == 'QUSHI':
            self.qushiSelect(dirs, subdir, forcetp)
        if trade == 'nbs':
            self.nbSelect(dirs, subdir, forcetp)
        if trade == 'kline':
            self.klSelect(dirs, subdir, forcetp)

    # ------------------ MAIN MODULE ---------------------------------- ##############
    def mock(self):
        start = self.__startday
        end   = self.__baseday
        startcnt = self.__daymap[start]
        endcnt   = self.__daymap[end]

        retslog = []
        tdetail = None 
        numzuhe = self.__numzuhe 
        maxbuy  = self.__maxbuy 

        forcetp  = self.__forcetp 
        
        for i in range(startcnt, endcnt):
            nday  = self.__mapday[i] 
            yday  = self.__mapday[i - 1] 
            nxday = self.__mapday[i + 1]

            nzuhe = len(self.__zuhe)
            if len(self.__zuhe) < numzuhe:
                maxbuy = self.__maxbuy 

            # Update Bear or Bull
            self.updateBB(nday)

            # Update Trade
            szbuy = self.sztime(nday, 5)
            self.__trade.upSZmtime(szbuy, self.__bear)

            # Track
            tdetail = self.trackZH(nday, retslog)

            print 'DEBUG:', nday, 'CASH_TOTAL:', self.__cashtotal, 'CASH_USED:', self.__cashused

            # ------------ SELL ----------------------- #
            (sflag, self.__zuhe) = self.switchout(nday, yday, nxday, forcetp)
            if nzuhe == numzuhe and sflag > 0:
                print 'DEBUG:', nday, 'MC_STOP_ACT is DONE, NO MORE ACT', nzuhe 
                continue
            # ------------ BUY ------------------------ #
            if nday not in self.__tradesignal:
                continue
            tups = self.__tradesignal[nday] 
            tups = self.__trade.resortTrades(tups)
            nbuy = 0
            dropbuy = 0
            for t in tups:
                if len(self.__zuhe) == numzuhe:
                    break
                if nbuy == maxbuy:
                    print 'DEBUG:', nday, 'NO BUY', nbuy, maxbuy, nxday, t[0], t[1], t[2]
                    break
                if t[0][0:2] == 'ZS':
                    print 'DEBUG:', nday, 'NO BUY ZHISHU', t[0]
                    continue
                (flag, comment, ref) = self.forceDrop(t, nday, forcetp)
                if flag == 1:
                    print 'DEBUG:', nday, comment, t[0], t[1], t[2] 
                    dropbuy = dropbuy + 1
                    continue
                bp = self.buy(t, nxday, nday)
                if bp is not None and t[0] not in self.__holds:
                    self.__holds[t[0]] = 1
                    shares = self.distshares(bp, numzuhe, nday)
                    self.__zuhe.append((nday,t, bp, shares))
                    nbuy = nbuy + 1
                else:
                    if t[0] in self.__holds:
                        print 'DEBUG:', nday, 'Drop Holded', t[0], t[1], t[2], nxday
        tdetail = self.trackZH(end, retslog)
        self.printTable(retslog, tdetail, end, forcetp)
        print '...........FINISHED........'

    def calShares(self, bp, maxzuhe, nday):
        shares = 0
        left = maxzuhe - len(self.__zuhe)
        remains = (int)(self.__cashtotal - self.__cashused)
        if remains <= 0:
            print 'DEBUG:', nday, 'NOT_ENOUGH_CASH'
            return 0
        if left > 0:
            maxone = remains / (self.__cashbase / maxzuhe)
            if maxone <= 1:
                shares = (remains / (bp * 100)) * 100
            else:
                if maxone >= left:
                    shares = (remains / (bp * 100 * left)) * 100
                else:
                    shares = ((self.__cashbase / maxzuhe) / (bp * 100)) * 100
        return (int)(shares)

    def distshares(self, bp, maxzuhe, nday):
        shares = self.calShares(bp, maxzuhe, nday) 
        self.__cashused  = bp * shares + self.__cashused
        self.__cashtotal = self.__cashtotal - 0.0005 * bp * shares 

        return shares

    # ------------- PRINT INFO ---------------------#
    def printTable(self, retslog, tdetail, nday, forcetp):

        # 历史调仓记录
        (avgholds, total) = self.printSwitch(nday)

        # 当前持仓
        tups = []
        if nday in self.__tradesignal:
            tups = self.__tradesignal[nday] 
        print nday, ' 当前持仓数:', len(tdetail), ' 入选标的数:', len(tups), ' 卖出标的数:', 0
        zuhe = PrettyTable(['T日', '代码', '名称', '得分', '收益率', '持有天数', '开仓价', '止盈价', '止损价', '手数'])
        zuhe.float_format = '.4'
        zuhe.align = 'l'
        (curholds, curuseage, curtotal) = self.printZH(nday, tdetail, zuhe)

        # T + 1 day
        self.updateBB(nday)
        for t in tups:
            (flag, comment, ref) = self.forceDrop(t, nday, forcetp)
            if flag == 1:
                print '选股择时:', nday, comment, t[0], t[1], t[2] 

        self.printNextDay(nday, tups, zuhe)
        output = zuhe.get_string().encode('utf-8') 
        f = open(self.__btdir + '/' + self.__prefix + '.zuhe.csv', 'w')
        f.write(output + '\n')
        f.close()
        
        # 历史总收益
        avgholds = (avgholds + curholds) / (total + curtotal + 0.0)
        self.printTotalReturn(retslog, avgholds, curuseage) 

    def computeStats(self, retslog, ind):
        maxdrawdown = (0.0, None, None)
        baseroc = 10.0
        tdays   = None 
        maxloss = 0
        cnt = 0
        arrets = []
        for i in range(0, len(retslog)):
            ir = retslog[i]
            cnt = cnt + 1
            iroc = float(ir[ind])
            arrets.append(iroc)
            if iroc < maxloss:
                maxloss = iroc
            if tdays is None and iroc > baseroc:
                tdays = cnt
            for j in range(i+1, len(retslog)):
                jr   = retslog[j]
                jroc = float(jr[ind])
                if iroc != 0 and iroc > jroc:
                    dd = jroc - iroc
                    if dd < maxdrawdown[0]:
                        maxdrawdown = (dd, ir[0], jr[0])
        narr  = np.array(arrets)

        diff  = (narr[1:len(narr)] - narr[0:len(narr)-1]) / 100
        fenmu = diff.std() * math.sqrt(225)
        fenzi = narr[-1] * 225 / (len(retslog) * 100)
        sharp = (fenzi - 0.03) / fenmu
        return (maxdrawdown, maxloss, sharp, tdays)

    def computeFLStats(self, retslog, ind):
        maxdrawdown = (0.0, None, None)
        baseroc = 10.0
        tdays   = None 
        maxloss = 0
        cnt = 0
        arrets = []
        for i in range(0, len(retslog)):
            ir = retslog[i]
            cnt = cnt + 1
            iroc = float(ir[ind])
            arrets.append(iroc)
            if iroc < maxloss:
                maxloss = iroc
            if tdays is None and iroc > baseroc:
                tdays = cnt
            for j in range(i+1, len(retslog)):
                jr   = retslog[j]
                jroc = float(jr[ind])
                if iroc != 0 and iroc > jroc:
                    dd = 100 * (jroc - iroc) / iroc
                    if dd < maxdrawdown[0]:
                        maxdrawdown = (dd, ir[0], jr[0])
        narr  = np.array(arrets)
        diff  = (narr[1:len(narr)] - narr[0:len(narr)-1] + 0.0) / (narr[0:len(narr)-1])
        fenmu = diff.std() * math.sqrt(225)
        fenzi = retslog[-1][5] * 225 / (len(retslog) * 100)
    
        sharp = (fenzi - 0.03) / fenmu

        print diff.std()

        return (maxdrawdown, maxloss, sharp, tdays)

    def printStrategyStats(self, retslog, avgholds, useage):
        f = open(self.__btdir + '/' + self.__prefix + '.stats.csv', 'w')
        zuhe = PrettyTable(['开仓日', '平仓日', '收益率', '最大回撤', '最大亏损', \
                            '比值', 'Sharp', '达标周期', '平均持仓时间', '资金利用率', \
                            'SZ000001', 'HS300', '复利', '复利回撤', '复利sharp'])
        zuhe.float_format = '.4'
        zuhe.align = 'l'
        kc   = retslog[0][0]
        pc   = retslog[-1][0]
        roc  = retslog[-1][3]
        fuli = retslog[-1][5]

        # STATS---计算单利
        (maxdrawdown, maxloss, sharp, tdays) = self.computeStats(retslog, 3)
        dd = maxdrawdown[0]
        if dd == 0.0:
            rate = None 
        else:
            rate = abs(roc / dd)
        SZop = float(self.__opset['ZS000001|' + kc])
        SZcl = float(self.__clset['ZS000001|' + pc])
        SZ = 100 * (SZcl - SZop) / SZop
        HSop = float(self.__opset['ZS000300|' + kc])
        HScl = float(self.__clset['ZS000300|' + pc])
        HS = 100 * (HScl - HSop) / HSop

        # STATS---计算复利
        (fulimaxdd, fuliloss, fulisharp, ph4) = self.computeFLStats(retslog, 4)

        zuhe.add_row([kc, pc, roc, dd, maxloss, rate, sharp, tdays, avgholds, useage, SZ, HS, fuli, fulimaxdd[0], fulisharp])
        output = zuhe.get_string().encode('utf-8')
        f.write(output + '\n')
        f.close()

    def printTotalReturn(self, retslog, avgholds, curuseage):
        useage   = 0.0

        f = open(self.__btdir + '/' + self.__prefix + '.rets.csv', 'w')
        header = 'day,ret1,ret2,sz000001,sc399001,holds,cash,fuli'
        f.write(header + '\n')

        (yday, bday1) = self.getDays('ZS000001', self.__startday)
        (yday, bday2) = self.getDays('ZS399001', self.__startday)
        for r in retslog:
            SZop = float(self.__opset['ZS000001|' + bday1])
            SZcl = float(self.__clset['ZS000001|' + r[0]])
            SZ = (SZcl - SZop) / SZop 

            SCop = float(self.__opset['ZS399001|' + bday2])
            SCcl = float(self.__clset['ZS399001|' + r[0]])
            SC = (SCcl - SCop) / SCop 
            line = r[0] + ',' + str(r[2]) + ',' + str(r[3]) \
                + ',' + str(100 * SZ) + ',' + str(100 * SC) + ',' + str(r[1]) + ',' \
                + str(r[4]) + ',' + str(r[5])
            f.write(line + '\n')

            useage   = useage + r[1] / 10.0
        f.close()
       
        total  = len(retslog)
        useage = (useage + curuseage) / (total + 1.0)

        self.printStrategyStats(retslog, avgholds, useage)

    def printNextDay(self, nday, tups, zuhe):
        for t in tups:
            okey = t[0] + '|' + nday
            fter = self.__trade.filter(okey)
            if fter[0]:
                print 'DEBUG:','Drop Filter_' + fter[1], t[0], t[1], nday, okey
                continue
            nclose = float(self.__clset[t[0] + '|' + nday])
            pkey = t[0] + '|' + nday + '|' + t[5]
            tmp  = (t[3], t[4], self.__trade.pred(pkey) * 0.99, nclose * 0.99)
            tmin = "{:.4f}".format(self.maxTup(tmp))
            tmax = "{:.4f}".format(nclose * 1.03)
            if tmax < tmin:
                print 'DEBUG:','Drop Buy', t[0], t[1], tmin, tmax, nday
                continue
            price = '[' + str(tmin) + ' ' + str(tmax) + ']'

            smin = self.calShares(float(tmin), 10, nday) / 100
            smax = self.calShares(float(tmax), 10, nday) / 100
            shares = '[' + str(smin) + ' ' + str(smax) + ']'

            zuhe.add_row([nday, t[0], t[1], t[2], '--', '--', price, '--', '--', shares])

    def printZH(self, nday, tdetail, zuhe):
        curholds  = 0.0
        curuseage = 0.0
        for t in tdetail:
            inst    = t[2]
            daymap  = self.__instdaymap[t[2]]
            lastday = self.__lastdayk[inst]
            start  = daymap[t[1]]
            pday   = nday
            if nday not in daymap:
                end  = daymap[lastday]
                pday = lastday
            else:
                end = daymap[nday] 
            holds = end - start + 1

            pkey = t[2] + '|' + pday + '|' + t[9]
            pred = self.__trade.pred(pkey)

            stopwin = pred * self.__stopwin 
            stoplos = pred * self.__stoplos 
            tmp = [t[1], t[2], t[3], t[4], t[7], holds, t[5], stopwin, stoplos, t[-1] / 100] 
            zuhe.add_row(tmp)

            curholds = curholds + holds
        curuseage = len(tdetail) / 10.0
        return (curholds, curuseage, len(tdetail)) 

    def printSwitch(self, nday): 

        ftrans = open(self.__btdir + '/' + self.__prefix + '.trans.csv', 'w')
        ftrans.write('close_dt,long,open_dt,pnl,returns,symbol,duration\n')

        zuhe = PrettyTable([u'T日', u'卖出日', u'代码', u'名称', u'收益率', u'持有天数', u'开仓价', u'止盈价', u'止损价', u'手数'])
        zuhe.float_format = '.4'
        zuhe.align = 'l'
        total = 0
        win   = 0.0
        avgholds  = 0.0

        for s in self.__switch:
            roc = 100 * float(s[3])
            stopwin = '--'
            stoplos = '--'
            if roc < 0:
                stoplos = s[2]  
            else:
                win = win + 1
                stopwin = s[2]
            daymap = self.__instdaymap[s[0][1][0]]
            start  = daymap[s[0][0]]
            end    = daymap[s[4]]
            holds  = end - start + 1 
            tmp = [s[0][0], s[4], s[0][1][0], s[0][1][1], roc, holds, s[1], stopwin, stoplos, s[5] / 100] 
            zuhe.add_row(tmp)
            total = total + 1
            avgholds = avgholds + holds

            pnl = (float(s[2]) - float(s[1])) * 100 * (s[5] / 100)
            t_trans = (s[4], 'True', s[0][0], str(pnl), str(roc / 100), s[0][1][0], str(holds))
            ftrans.write(','.join(t_trans))
            ftrans.write('\n')
        ftrans.close()

        output = zuhe.get_string().encode('utf-8') 
        
        winrate = 0.0
        if total > 0:
            winrate = win / total 
        header = nday + u' 交易次数:' + str(total) + u' 胜率:' + str(winrate) 

        f = open(self.__btdir + '/' + self.__prefix + '.trades.csv', 'w')
        f.write(header.encode('utf-8') + '\n')
        f.write(output + '\n')
        f.close()

        return (avgholds, total)

    def maxTup(self, tup):
        maxs = 0
        for t in tup:
            if t == 'NULL':
                continue
            if float(t) > maxs:
                maxs = float(t)
        return maxs


def parseinst(codearr, bk='ALL'):
    out = []

    d = set()
    if bk == 'DEBUG':
        for line in open('./data/debug.csv'):
            code = line.strip()
            d.add(code)

    if bk == 'TMP':
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            code  = fname[2:8]
            out.append((fname,code))
        return out

    if bk == 'LINE':
        for c in codearr:
            tmp   = c.split('-')
            fname = tmp[-1]
            code  = fname[0:8]
            out.append((fname,code))
        return out

    for c in codearr:
        tmp   = c.split('-')
        fname = tmp[-1]

        fsize = fname.split('.')
        if len(fsize) > 2:
            continue
        code  = fname[0:8]
        f1 = code[0:2]
        f2 = code[2:5]
        if bk == 'TEST' and code[2:6] == '3001':
            out.append((fname,code))
        if bk == 'CYB' and f2 == '300':
            out.append((fname,code))
        if bk == 'ZB' and f2 == '600':
            out.append((fname,code))
        if bk == 'ALL':
            out.append((fname,code))
        if bk == 'BK' and f1 == 'BK':
            out.append((fname,code))
        if bk == 'DEBUG' and code in d:
            out.append((fname,code))
    shuffle(out)
    return out


def minVertDistance(arr, point):
    if len(arr) == 0:
        return None
    tmp  = np.array(arr)
    diff = (tmp - point) / point
    absdiff = np.abs(diff)
    index   = absdiff.argmin()
    return (index, np.min(absdiff), arr[index], diff[index]) 


# ret = 1, 压力
# ret = 0, 支撑
def positionScore(high, low, close):
    ret   = -1 
    score = 0.0 
    if low > 0.0 and close >= 0.0:
        ret = 1
        if high >= 0.0 and high < 0.03:
            score = close 
        if high < 0.0:
            score = close + abs(high)
    if high < 0.0 and close <= 0.0:
        ret = 0
        if low <= 0.0 and low > -0.03:
            score = abs(close)
        if low > 0.0:
            score = abs(close) - abs(low)
    return (ret, score)
#
