import collections
import bisect
import numpy as np


class PE(object):

    def __init__(self,db,ts,fname,match):
        self.__db = db
        self.__file = fname
        self.__ts  = ts
        self.__match = match

    def compute(self):
        stock_val = dict()
        cnt = 0
        for line in open(self.__file):
            if cnt == 0:
                cnt = cnt + 1
                continue
            row = line.strip().split(',')
            code = self.__db.getStockID(int(row[1]))
            if code not in stock_val:
                odict = collections.OrderedDict()
            else:
                odict = stock_val[code]
            odict[int(row[3])] = float(row[2])
            stock_val[code] = odict
            cnt = cnt + 1
        for k,v in stock_val.iteritems():
            if k not in self.__match:
                continue
            cnt = 0
            na = np.array(v.keys())
            print na
            print v
            for line in open('data/' + k + '.csv'):
                if cnt == 0:
                    cnt = cnt + 1
                    continue
                arr = line.strip().split(',')
                day  = arr[0]
                tday = int(self.__ts.string_toTimestamp(day))
                close = float(arr[-1])
                idx   = np.where(na < tday)
                match = na[idx]
                val  = float(v[match[0]][1])
                print tday,v.items()[match[0]][0]
                # print day,k,val,close
