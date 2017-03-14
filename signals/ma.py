# coding:utf-8
import signals
import os
from signals import XTsignal
from signals import zq


class MA(XTsignal):

    def __init__(self, dirs, nday):
        super(MA, self).__init__(dirs, nday)
        self.loadSignals('dayk')
        self.__codes = self.getCodes()
        self.__zq    = zq.ZHOUQI(dirs, nday)

    def fwMax(self, zq, start, total):
        m = -1
        for i in range(start, total + 1):
            if i in zq and zq[i] > m:
                m = zq[i]
        return m

    # write Data
    def select(self, name, score):
        bbuy = []
        xbuy = []
        p1 = ['ma'] 
        p2 = ['macd']
        for c in self.__codes:
            above  = 0
            bull   = 0
            mas = self.getNday(c, p1)
            if mas is not None and len(mas) > 0:
                above = mas['abv']
                bull  = mas['bull']

            hist   = 0
            qshist = 0
            macd = self.getNday(c, p2)
            if macd is not None and len(macd) > 0:
                hist   = macd['hist']
                qshist = macd['qs']

            nzq = self.__zq.resonance(c, self.getDay())

            if bull > score and hist > 0 and qshist == 1 and \
                    ((0 in nzq[0] and 1 not in nzq[0]) or \
                     (1 in nzq[0] and 0 not in nzq[0])) and \
                    self.fwMax(nzq, 0, 5) > 2:
                bbuy.append((c, self.getName(c), name, mas, nzq[0]))
            if bull <= 0 and hist > 0 and (0 not in nzq[0] and 1 not in nzq[0]) \
                    and above > 0 and self.fwMax(nzq, 0, 5) > 2:
                xbuy.append((c, self.getName(c), name, mas, nzq[0]))

        def dump(arr, tag):
            for m in arr:
                print tag, m[0], m[1], m[2], m[3], m[4]

        dump(bbuy, '多头')
        dump(xbuy, '蓄势')
#
