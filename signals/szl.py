import signals
import os
from signals import XTsignal


class SZL(XTsignal):

    def __init__(self, dirs, nday):
        super(SZL, self).__init__(dirs, nday)
        self.loadSignals('dayk')

        self.__codes = self.getCodes()
        self.__sigs  = self.getSignals()

    def select(self, dirs):
        # write Data
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        output = dirs + '/' + self.getDay() + '.csv'
        f = open(output, 'w')

        dayk = self.__sigs[2]
        for c in self.__codes:
            if c not in dayk:
                continue
            szl  = dayk[c]['qs']['szl']
            ohlc = dayk[c]['qs']['ohlc']
            if len(szl) > 0 and szl['dir'] == 1:
                np = szl['np']
                cl = ohlc[3] - np[0]
                lw = ohlc[2] - np[0]
                if lw < 0 and cl > 0:
                    print 'SZL: HC1', c, self.getName(c)
                if abs(lw / np[0]) < 0.005 and cl > 0:
                    print 'SZL: HC2', c, self.getName(c)
        f.close()
#
