# coding:utf-8
from ml import ETL
import time
import datetime
import os


class CZSC(ETL):

    def __init__(self, index, codearr, div, dirs):
        super(CZSC, self).__init__(index, codearr, div, dirs)

        self.__peek = {}
        self.__vall = {}

        self.__bward = 50

        self.__filter = {}

        self.__url = 'http://api.quchaogu.com/chart/history?resolution=D&adjust=1&symbol='

    # run
    def run(self):
        self.loadPV()
        peek  = self.Filter(self.__peek)
        odir = './output/czsc/'
        self.dump(peek, odir, 'peek')
        
        vall  = self.Filter(self.__vall)
        self.dump(vall, odir, 'vall')

    def t2stamp(self, strTime):
        dt = datetime.datetime.strptime(strTime, "%Y-%m-%d")
        return time.mktime(dt.timetuple())

    # dump
    def dump(self, gdict, odir, tp):
        for code, val in gdict.iteritems():
            f = open(odir + '/' + tp + '_' + code + '.csv', 'w')
            for sday, days in val.iteritems():
                t1 = int(self.t2stamp(sday))
                t2 = int(self.t2stamp(days[-1]))
                f.write(code + ',' + str(t1) + ',' + str(t2) + ',' + sday + ',' + tp)
                f.write('\n')
            f.close()

    # 过滤拐点
    def Filter(self, gdlist):
        ret   = {}
        codes = self.getCodes()
        for c in codes:
            if c not in gdlist:
                continue
            gds = {}
            for p in gdlist[c]:
                zq = self.getZQ(c, p)
                if zq <= self.__bward + 1:
                    continue
                days = []
                for i in range(0, self.__bward + 2):
                    days.append(self.getDay(c, zq - i))
                gds[p] = days
            ret[c] = gds
        return ret

    # 加载顶拐点
    def loadPV(self): 
        dirs  = './data/czsc/'
        codes = self.getCodes()
        for c in codes:
            fname = dirs + c + '.csv'
            if not os.path.isfile(fname):
                continue
            cnt = 0
            peek = []
            vall = []
            for line in open(fname):
                if cnt == 0:
                    cnt = cnt + 1
                    continue
                arr = line.strip().split(',')
                flag = int(arr[1])
                if flag == 1:
                    peek.append(arr[0])
                if flag == 0:
                    vall.append(arr[0])
                cnt = cnt + 1
            self.__peek[c] = peek 
            self.__vall[c] = vall 
#
