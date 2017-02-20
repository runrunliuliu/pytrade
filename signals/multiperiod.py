import signals
from signals import XTsignal


class MultiPeriod(XTsignal):

    def __init__(self, dirs, nday):
        super(MultiPeriod, self).__init__(dirs, nday)
        self.loadSignals()

        self.__codes = self.getCodes() 
        self.__sigs  = self.getSignals()

    def select(self):
        monk = self.__sigs[0]
        week = self.__sigs[1]
        dayk = self.__sigs[2]
        for c in self.__codes:
            if c in monk:
                qs = monk[c]['qs']
                print c, 'month', qs['nqs']
            if c in dayk:
                qs = dayk[c]['qs']
                print c, 'day', qs['nqs']
#
