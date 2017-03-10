# coding:utf-8
import signals
import os
from signals import XTsignal


class ZHOUQI(XTsignal):

    def __init__(self, dirs, nday):
        super(ZHOUQI, self).__init__(dirs, nday)
        self.loadSignals('dayk')

        self.__codes = self.getCodes()
        self.__fbsq  = {5, 8, 13, 21, 34, 55, 89, 144}
        self.__power = {49, 64, 81, 121, 144}
        self.__gann  = {45, 90, 120, 180}

    def timeseq(self, zq, fday):
        fbret = dict(); pmret = dict(); gnret = dict()
        zq1 = zq[0]
        if zq1 is not None:
            for i in range(1, fday + 1):
                fbm = 0; pom = 0; gann = 0
                for p in ['AF', 'BF', 'CF', 'DF', 'EF']:
                    if p not in zq1:
                        continue
                    nextd = zq1[p] + i
                    if nextd in self.__fbsq:
                        fbm = fbm + 1
                    if nextd in self.__power:
                        pom = pom + 1 
                    if nextd in self.__gann:
                        gann = gann + 1
                if fbm > 0:
                    fbret[i] = fbm
                if pom > 0:
                    pmret[i] = pom
                if gann > 0:
                    gnret[i] = gann

        return (fbret, pmret, gnret)

    # 江恩比率
    def gannratio(self, zq, fday):
        ret = dict()
        if zq is not None:
            for i in range(1, fday + 1):
                m = 0
                if 'DF' in zq and 'CD' in zq:
                    df = zq['DF'] + i
                    cd = zq['CD']
                    if df % cd == 0 or cd % df == 0:
                        m = m + 1
                if 'EF' in zq and 'CE' in zq:
                    ef = zq['EF'] + i 
                    ce = zq['CE']
                    if ef % ce == 0 or ce % ef == 0:
                        m = m + 1
                if m > 0:
                    ret[i] = m
        return (ret, )

    # 谐波
    def harmonic(self, zq, fday):
        ret = dict()
        if zq is not None:
            for i in range(1, fday + 1):
                m = 0
                if 'DE' in zq and 'EF' in zq:
                    de = zq['DE']
                    ef = zq['EF'] + i
                    if de % ef == 0 or ef % de == 0:
                        m = m + 1
                if 'CE' in zq and 'DF' in zq:
                    ce = zq['CE']
                    df = zq['DF'] + i
                    if ce % df == 0 or df % ce == 0:
                        m = m + 1
                if m > 0:
                    ret[i] = m
        return (ret, )

    # 共振
    def resonance(self, code):
        p1  = ['qs', 'zq', 'zq1'] 
        zq1 =  self.getNday(code, p1)
        p2  = ['qs', 'zq', 'zq2'] 
        zq2 = self.getNday(code, p2)

        p3 = ['score']
        score = self.getNday(code, p3)
       
        timesq = self.timeseq((zq1, zq2), 5)
        gannsq = self.gannratio(zq1, 5)
        harmsq = self.harmonic(zq1, 5)

        sq  = timesq + gannsq + harmsq 
        day = 5
        gz  = dict()
        for s in sq:
            if len(s) == 0:
                continue
            for i in range(1, day + 1):
                tmp1 = 0
                if i in s:
                    tmp1 = s[i] 
                tmp2 = 0
                if i in gz:
                    tmp2 = gz[i]
                tmp2 = tmp2 + tmp1
                if tmp2 > 0:
                    gz[i] = tmp2
        return (gz, score)
   
    # 获取
    def get(self, code):
        gz = self.resonance(code)
        print code, self.getName(code), gz

    # write Data
    def select(self, fday, rtime, score):
        ret = []
        for c in self.__codes:
            gz = self.resonance(c)
            if fday in gz[0] and gz[0][fday] >= rtime and gz[1] > score:
                ret.append((c, self.getName(c), gz))
        return ret
#
