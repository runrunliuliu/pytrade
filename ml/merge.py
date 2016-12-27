# coding:utf-8
from collections import OrderedDict
from datetime import datetime as dt
import re


class Merge(object):

    def __init__(self, inst, base, output, ts):

        self.__ts = ts 
        self.__basedir = base
        self.__header  = ''

        self.__min15k  = OrderedDict()
        self.__ft15k   = OrderedDict()
        self.__ft15k_d = '1024201,1024201,1024201,1024201,1024201,1024201,1024201,1024201,1024201,1024201'

        self.__ftdayk = OrderedDict()

        self.__output = output
        self.__inst   = inst

        self.__op_d = dict()
        self.__hi_d = dict()
        self.__lw_d = dict()
        self.__cl_d = dict()

        self.__dtzq = dict()
        self.__dind = []
       
        self.__ft2hd_d = dict()
        for line in open('./conf/header.conf'):
            nline = line.strip()
            if nline.startswith('#'):
                print 'DEBUG', nline
                continue
            arr = nline.split(',')
            self.__ft2hd_d[arr[1]] = arr[0]

    def loadBaseDayK(self, dpath):
        linenum = 0
        dzq = 0 
        for line in open(self.__basedir + '/' + dpath):
            if linenum == 0:
                linenum = linenum + 1
                continue
            arr = line.strip().split(',')
            day = arr[0]
            op = float(arr[1])
            hi = float(arr[2])
            lw = float(arr[3])
            cl = float(arr[4])

            self.__op_d[day] = op
            self.__hi_d[day] = hi
            self.__lw_d[day] = lw 
            self.__cl_d[day] = cl 

            dzq = dzq + 1
            self.__dtzq[day] = dzq
            self.__dind.append(day)

    # LOAD 15min Data
    def loadMin15k(self, dpath):
        pday    = None
        linenum = 0
        for line in open(self.__basedir + '/' + dpath):
            if linenum == 0:
                linenum = linenum + 1
                continue
            arr = line.strip().split(',')
            day = arr[0]
            kdj   = int(arr[1])
            macd  = int(arr[2])
            macd2 = arr[8]
            macd3 = arr[9]
            macd4 = arr[10]
            macd5 = arr[11]
            macd6 = arr[12]
            macd7 = arr[13]

            tup = (kdj, macd, macd2, macd3, macd4, macd5, macd6, macd7)
            tmp = []
            if pday is not None:
                if pday == day:
                    tmp = self.__min15k[day] 
                tmp.append(tup)
            else:
                tmp = [tup]
            self.__min15k[day] = tmp 
            pday    = day 
            linenum = linenum + 1

    def parseMin15k(self):
        head = 'kdj1,kdj2,macd1,macd2,' + \
            'macd3,macd4,macd5,macd6,macd7,macd8' 

        for k,v in self.__min15k.iteritems():
            cnt     = 1 
            kdj     = '0,0' 
            macd    = '1024201,0'
            # macd  = '0,0'
            kdj_do  = 0
            macd_do = 0
            # macd2   = '0,0,0,0,0,0'
            macd2   = '1024201,1024201,1024201,1024201,1024201,1024201'
            for item in v:
                if item[0] == 1 and kdj_do == 0:
                    kdj    = str(cnt) + ',' + str(item[0])
                    kdj_do = 1
                if item[1] > 0 and macd_do == 0:
                    macd    = str(cnt) + ',' + str(item[1])
                    macd_do = 1

                    macd2   = item[2] + ',' + item[3] + ',' + item[4] + \
                        ',' + item[5] + ',' + str(self.getBRet(item[6], 1)[0]) + \
                        ',' + item[7]

                cnt = cnt + 1
            self.__ft15k[k] = kdj + ',' + macd + ',' + macd2

        self.__header = head 

    def loadDayk(self, dpath):
        def int2bit(val, cnt):
            tmp = []
            for i in range(1, cnt + 1):
                if val == i:
                    tmp.append('1')
                else:
                    tmp.append('0')
            return tmp

        header = 'sxy1,sxy2,sxy3,sxy4,sxy5,sxy6,' \
            + 'zdf1,zdf2,zdf3,zdf4,zdf5,zdf6,zdf7,' \
            + 'td1,td2,td3'
        linenum = 0
        for line in open(self.__basedir + '/' + dpath):
            if linenum == 0:
                linenum = linenum + 1
                continue
            arr = line.strip().split(',')
            day = arr[0]
            sxy  = int(arr[3])
            zdf  = int(arr[4])

            sxy_bit = ','.join(int2bit(sxy, 6))
            zdf_bit = ','.join(int2bit(zdf, 7))
            
            td  = '0,0,0'
            td1 = int(arr[5])
            if td1 != 1024:
                td = str(td1) + ',' + str(arr[6]) + ',' + str(arr[7])
                
            self.__ftdayk[day] = sxy_bit + ',' + zdf_bit + ',' + td

        self.__header = self.__header + ',' + header

    # 前向受益
    def getFRet(self, day):
        ret  = []
        fret = 5
        nind = self.__dtzq[day]
        for i in range(0, fret):
            if (nind + i) >= len(self.__dind):
                ret.append('0.0')
            else:
                r = (self.__cl_d[self.__dind[nind + i]] - self.__cl_d[day] ) / self.__cl_d[day]
                r = "{:.4f}".format(r)
                ret.append(r)
        return ret

    # 前向非累积受益
    def getFOneDayRet(self, day):
        ret  = []
        fret = 3 
        nind = self.__dtzq[day]
        for i in range(0, fret):
            if (nind + 1) >= len(self.__dind):
                ret.append('0.0')
            else:
                ncl = self.__cl_d[self.__dind[nind - 1]]
                fcl = self.__cl_d[self.__dind[nind]]
                r = (fcl - ncl) / ncl 
                r = "{:.4f}".format(r)
                ret.append(r)
            nind = nind + 1
        return ret

    # 后向受益
    def getBRet(self, day, back):
        ret  = []
        nind = self.__dtzq[day]
        for i in range(-1 * back, 0):
            if (nind + i) < 0:
                ret.append('NULL')
            else:
                yop = self.__cl_d[self.__dind[nind + i - 1]] 
                ncl = self.__cl_d[day]
                r = (ncl - yop ) / yop 
                r = "{:.4f}".format(r)
                ret.append(r)
        return ret

    # Feature from LW
    def loadFT3(self, fname):
        cnt     = 0
        header  = ''
        ft3dict = dict()
        ftleng  = 0
        for line in open(self.__output + '/' + fname):
            if cnt == 0:
                header = line.strip()[4:]
            else:
                arr  = line.strip().split(',')
                day  = dt.strptime(arr[0], "%Y%m%d")
                sday = day.strftime('%Y-%m-%d')
                fts = []
                for i in range(1, len(arr)):
                    if "%" in arr[i]:
                        tmp = "{:.4f}".format(float(arr[i][:-1]) / 100.0)
                        fts.append(tmp)
                    else:
                        fts.append(arr[i])
                ft3dict[sday] = fts
                ftleng = len(fts)
            cnt = cnt + 1
        return(header, ft3dict, ftleng)

    # Feature from LW
    def loadFT2(self, fname):
        cnt     = 0
        header  = ''
        ft2dict = dict()
        for line in open(self.__output + '/' + fname):
            if cnt == 0:
                header = line.strip()[5:]
            else:
                arr  = line.strip().split(',')

                day  = dt.strptime(arr[0], "%Y%m%d")
                sday = day.strftime('%Y-%m-%d')
                fts = []

                for i in range(1, len(arr)):
                    if "%" in arr[i]:
                        tmp = "{:.4f}".format(float(arr[i][:-1]) / 100.0)
                        fts.append(tmp)
                    elif len(arr[i]) == 0:
                        fts.append('1024201')
                    else:
                        fts.append(arr[i])
                
                # Feature Handles
                for k in range(0, len(fts)):
                    if k == 19 and int(fts[18]) <= 2:
                        fts[k]     = '1024201'
                        fts[k - 1] = '1024201'
                ft2dict[sday] = fts
            cnt = cnt + 1
        return(header, ft2dict)

    def transFT2(self, fname):
        f    = open(self.__output + '/' + self.__inst + '.ft3.csv', 'w')
        fday = open(self.__output + '/' + self.__inst + '.actday.csv', 'w')
        path = self.__output + '/'  + fname
        # Get Header Index
        hd_index = dict()
        for line in open(path):
            arr = line.strip().split(',')
            for i in range(0, len(arr)):
                hd_index[i] = arr[i]
            break
        cnt  = 0
        headers = []
        for line in open(path):
            arr = line.strip().split(',')
            fts = []
            for i in range(0, len(arr)):
                if hd_index[i] not in self.__ft2hd_d:
                    continue
                if cnt == 0:
                    headers.append(self.__ft2hd_d[arr[i]])
                else:
                    # special handling 急涨急跌
                    # desname = self.__ft2hd_d[hd_index[i]]
                    # if desname == 'jjdmin' and self.__ts.comparedt(arr[0], '20160301', '%Y%m%d'):
                    #     arr[i] = ''

                    if len(arr[i]) == 0:
                        # special handling
                        if i == len(arr) - 1:
                            continue
                        arr[i] = '1024201'
                    else:
                        if hd_index[i].decode('utf8') == u'上证涨跌幅' and float(arr[i]) <= -0.01:
                            fday.write(arr[0] + ',' + arr[i] + '\n')
                    fts.append(arr[i])
            if cnt == 0:
                f.write(','.join(headers))
            nline = ','.join(fts)
            f.write(nline + '\n')
            cnt = cnt + 1
        f.close()
        fday.close()

    def combFeatures(self):

        self.loadBaseDayK('dayk/' + self.__inst + '.csv')

        self.loadMin15k('15mink/qcg/' + self.__inst + '.ft.csv')
        self.parseMin15k()

        self.loadDayk('dayk/qcg/' + self.__inst + '.ft.csv')

        self.transFT2('test2.txt')

        # (ft2header, ft2dict) = self.loadFT2(self.__inst + '.ft2.csv')
        (ft2header, ft2dict, ft2len) = self.loadFT3(self.__inst + '.ft3.csv')

        self.__header = 'day,' + self.__header + ',' + ft2header + ',ret1,ret2,ret3,ret4,ret5,ret6,ret7,ret8'

        f = open(self.__output + '/' + self.__inst + '.ft.csv', 'w')
        f.write(self.__header + '\n')
        for k, v in self.__ftdayk.iteritems():
            ft15k = self.__ft15k_d
            if k in self.__ft15k:
                ft15k = self.__ft15k[k]

            # Get FT2
            ft2 = []
            for i in range(0, ft2len):
                ft2.append('1024201')
            if k in ft2dict:
                ft2 = ft2dict[k]
            ft2flat = ','.join(ft2)

            # GET Day Index
            fret1 = ','.join(self.getFRet(k))
            fret2 = ','.join(self.getFOneDayRet(k))
            f.write(k + ',' + ft15k + ',' + v + ',' + ft2flat + ',' + fret1 + ',' + fret2) 
            # f.write(k + ',' + ft15k + ',' + v + ',' + fret1 + ',' + fret2) 
            f.write('\n')
        f.close()
#
