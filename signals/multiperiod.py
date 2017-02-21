import signals
from signals import XTsignal


class MultiPeriod(XTsignal):

    def __init__(self, dirs, nday):
        super(MultiPeriod, self).__init__(dirs, nday)
        self.loadSignals()

        self.__codes = self.getCodes()
        self.__sigs  = self.getSignals()

    def select(self):
        def getVal(json, k1, k2):
            ret = None
            if k1 in json:
                qs  = json[k1]['qs']
                ret = qs[k2]
            return ret
        week = self.__sigs[1]
        dayk = self.__sigs[2]
        mk60 = self.__sigs[3]
        mk30 = self.__sigs[4]
        for c in self.__codes:
            nqs_w = getVal(week, c, 'nqs')
            nqs_d = getVal(dayk, c, 'nqs')
            nqs_6 = getVal(mk60, c, 'nqs')
            nqs_3 = getVal(mk30, c, 'nqs')

            if (nqs_w != 1301 and nqs_w != 1302 and nqs_w != 2303 and nqs_w != 0) \
                    and (nqs_d == 1101 or nqs_d == 2102 or nqs_d == 2103) \
                    and (nqs_6 == 2102 or nqs_6 == 2103) \
                    and (nqs_3 == 2102 or nqs_3 == 2103):
                print c, self.getName(c), nqs_w, nqs_d, nqs_6, nqs_3
#
