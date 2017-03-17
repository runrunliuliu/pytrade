# coding:utf-8
import signals
import os
from signals import XTsignal
from signals import zq


class KLINE(XTsignal):

    def __init__(self, dirs, nday):
        super(KLINE, self).__init__(dirs, nday)
        self.loadSignals('dayk')
        self.__codes = self.getCodes()
        self.__zq    = zq.ZHOUQI(dirs, nday)

    def fwMax(self, zq, start, total):
        m = -1
        for i in range(start, total + 1):
            if i in zq and len(zq[i]) > m:
                m = len(zq[i])
        return m

    # write Data
    def select(self, name):
        p1 = ['qs', 'kline'] 
        for c in self.__codes:
            kline =  self.getNday(c, p1)
            if kline is None:
                continue
            for k in kline:
                if k['nm'] in name:
                    nzq = self.__zq.resonance(c, self.getDay())
                    print c, self.getName(c), k['nm'], nzq[0]
