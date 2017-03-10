import signals
import os
from signals import XTsignal
from signals import zq 


class SZL(XTsignal):

    def __init__(self, dirs, nday):
        super(SZL, self).__init__(dirs, nday)
        self.loadSignals('dayk')
        self.__codes = self.getCodes()

        # Init ZhouQi
        self.__zq = zq.ZHOUQI(dirs, nday)

    # write Data
    def select(self, dirs):
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        output = dirs + '/' + self.getDay() + '.csv'
        f = open(output, 'w')
        for c in self.__codes:
            p1 = ['qs', 'szl']
            szl =  self.getNday(c, p1)
            p2 = ['qs', 'ohlc']
            ohlc = self.getNday(c, p2)
            if szl is not None and len(szl) > 0 and szl['dir'] == 1:
                np = szl['np']
                cl = ohlc[3] - np[0]
                lw = ohlc[2] - np[0]
                if lw < 0 and cl > 0:
                    print 'SZL: HC1', c, self.getName(c)
                if abs(lw / np[0]) < 0.005 and cl > 0:
                    print 'SZL: HC2', c, self.getName(c)
        f.close()
#
