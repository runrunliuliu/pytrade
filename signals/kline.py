# coding:utf-8
import signals
import os
from signals import XTsignal


class KLINE(XTsignal):

    def __init__(self, dirs, nday):
        super(KLINE, self).__init__(dirs, nday)
        self.loadSignals('dayk')
        self.__codes = self.getCodes()

    # write Data
    def select(self, name):
        p1 = ['qs', 'kline'] 
        for c in self.__codes:
            kline =  self.getNday(c, p1)
            if kline is None:
                continue
            for k in kline:
                if k['nm'] == name:
                    print c, self.getName(c), name
#
