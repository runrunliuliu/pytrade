import signals
import os
from signals import XTsignal


class MultiPeriod(XTsignal):

    def __init__(self, dirs, nday):
        super(MultiPeriod, self).__init__(dirs, nday)
        self.loadSignals()

        self.__codes = self.getCodes()
        self.__sigs  = self.getSignals()

    def getVal(self, json, k1, k2):
        ret = 1024201
        if k1 in json:
            qs  = json[k1]['qs']
            ret = qs[k2]
        return ret

    # Dump Feature Data
    def dumpFT(self, dirs):

        if not os.path.exists(dirs):
            os.makedirs(dirs)
        output = dirs + '/' + self.getDay() + '.csv'

        f = open(output, 'w')
        week = self.__sigs[1]
        dayk = self.__sigs[2]
        mk60 = self.__sigs[3]
        mk30 = self.__sigs[4]
        f.write('code,week,day,60min,30min\n')
        for c in self.__codes:
            nqs_w = self.getVal(week, c, 'nqs')
            nqs_d = self.getVal(dayk, c, 'nqs')
            nqs_6 = self.getVal(mk60, c, 'nqs')
            nqs_3 = self.getVal(mk30, c, 'nqs')
            o = c + ',' + str(nqs_w) + ',' + str(nqs_d) + ',' \
                + str(nqs_6) + ',' + str(nqs_3)
            f.write(o + '\n')
        f.close()

    def loadPrevData(self, dirs):
        pcodes = dict()
        pday   = self.getPrevDay()
        infile = dirs + '/' + pday + '.csv'
        if os.path.isfile(infile):
            for line in open(infile):
                arr = line.split(',')
                pcodes[arr[0]] = 1
        return pcodes

    def select(self, dirs):
        # write Data
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        output = dirs + '/' + self.getDay() + '.csv'
        f = open(output, 'w')

        # load data
        pdata = self.loadPrevData(dirs)
        newdata = []

        week = self.__sigs[1]
        dayk = self.__sigs[2]
        mk60 = self.__sigs[3]
        mk30 = self.__sigs[4]
        for c in self.__codes:
            nqs_w = self.getVal(week, c, 'nqs')
            nqs_d = self.getVal(dayk, c, 'nqs')
            nqs_6 = self.getVal(mk60, c, 'nqs')
            nqs_3 = self.getVal(mk30, c, 'nqs')

            if (nqs_w != 1301 and nqs_w != 1302 and nqs_w != 2303 and nqs_w != 0) \
                    and (nqs_d == 1101 or nqs_d == 2102 or nqs_d == 2103) \
                    and (nqs_6 == 2102 or nqs_6 == 2103) \
                    and (nqs_3 == 2102 or nqs_3 == 2103):
                o = c + ',' + self.getName(c) + ',' + str(nqs_w) + ',' \
                    + str(nqs_d) + ',' + str(nqs_6) + ',' + str(nqs_3)
                f.write(o + '\n')
                if c not in pdata:
                    newdata.append(o)
        f.close()
        for k in newdata:
            print k
#
