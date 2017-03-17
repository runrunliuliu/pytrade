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

        self.__zq = dict()

    def timeseq(self, zq, fday):
        fbret = dict(); pmret = dict(); gnret = dict()
        zq1 = zq[0]
        if zq1 is not None:
            for i in range(0, fday + 1):
                fbm = []; pom = []; gann = []
                for p in ['AF', 'BF', 'CF', 'DF', 'EF']:
                    if p not in zq1:
                        continue
                    nextd = zq1[p] + i
                    if nextd in self.__fbsq:
                        fbm.append(nextd)
                    if nextd in self.__power:
                        pom.append(nextd)
                    if nextd in self.__gann:
                        gann.append(nextd)
                if len(fbm) > 0:
                    fbret[i] = fbm
                if len(pom) > 0:
                    pmret[i] = pom
                if len(gann) > 0:
                    gnret[i] = gann

        return (fbret, pmret, gnret)

    # 江恩比率
    def gannratio(self, zq, fday):
        ret = dict()
        if zq is not None:
            for i in range(0, fday + 1):
                m = []
                if 'DF' in zq and 'CD' in zq:
                    df = zq['DF'] + i
                    cd = zq['CD']
                    if df % cd == 0 or cd % df == 0:
                        m.append((df, cd))
                if 'EF' in zq and 'CE' in zq:
                    ef = zq['EF'] + i 
                    ce = zq['CE']
                    if ef % ce == 0 or ce % ef == 0:
                        m.append((ef, ce))
                if m > 0:
                    ret[i] = m
        return (ret, )

    # 谐波
    def harmonic(self, zq, fday):
        ret = dict()
        if zq is not None:
            for i in range(0, fday + 1):
                m = []
                if 'DE' in zq and 'EF' in zq:
                    de = zq['DE']
                    ef = zq['EF'] + i
                    if de % ef == 0 or ef % de == 0:
                        m.append((de, ef))
                if 'CE' in zq and 'DF' in zq:
                    ce = zq['CE']
                    df = zq['DF'] + i
                    if ce % df == 0 or df % ce == 0:
                        m.append((ce, df)) 
                if m > 0:
                    ret[i] = m
        return (ret, )

    # 共振
    def resonance(self, code, day):
        p1  = ['qs', 'zq', 'zq1'] 
        zq1 =  self.getJSON(code, p1, day)
        p2  = ['qs', 'zq', 'zq2'] 
        zq2 = self.getJSON(code, p2, day)

        p3 = ['score']
        score = self.getJSON(code, p3, day)
       
        timesq = self.timeseq((zq1, zq2), 5)
        gannsq = self.gannratio(zq1, 5)
        harmsq = self.harmonic(zq1, 5)

        sq  = timesq + gannsq + harmsq 
        day = 5
        gz  = dict()
        for s in sq:
            if len(s) == 0:
                continue
            for i in range(0, day + 1):
                tmp1 = []
                if i in s:
                    tmp1 = s[i]
                tmp2 = []
                if i in gz:
                    tmp2 = gz[i]
                tmp2 = tmp2 + tmp1
                if len(tmp2) > 0:
                    gz[i] = tmp2
        return (gz, score)
   
    # 获取
    def get(self, code):
        gz = self.__zq[code]
        print code, self.getName(code), gz

    # 初始化周期
    def initZQ(self):
        day = self.getDay()
        for c in self.__codes:
            gz = self.resonance(c, day)
            self.__zq[c] = gz

    # 获取特定周期点
    def getSpecial(self, fday, time, score):
        ret = []
        for c in self.__codes:
            gz = self.__zq[c]
            if fday in gz[0] and gz[1] > score and 0 not in gz[0]:
                for t in gz[0][fday]: 
                    if isinstance(t, int) and t >= time:
                        ret.append((c, self.getName(c), gz))
        return ret

    # write Data
    def select(self, fday, rtime, score):
        ret = []
        p1  = ['macd']
        for c in self.__codes:
            hist   = 0
            macd = self.getNday(c, p1)
            if macd is not None and len(macd) > 0:
                hist   = macd['hist']

            gz = self.__zq[c]
            if fday in gz[0] and len(gz[0][fday]) >= rtime \
                    and gz[1] > score and 0 not in gz[0] and hist > 0:
                ret.append((c, self.getName(c), gz))
        return ret
#
