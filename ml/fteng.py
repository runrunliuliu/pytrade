# coding:utf-8
import datetime
import numpy as np
from datetime import datetime as dt


class FTeng(object):

    def __init__(self, path, code, startday):

        self.__bday      = dt.strptime(startday, "%Y-%m-%d")
        self.__ftdict    = dict()
        self.__instances = []
        self.__path      = path
        self.__code      = code

        self.__trange = self.loadrange('./ml/trange.conf')

        self.loadata(path + '/' + code + '.ft.csv', ['zd', 'ss', 'xj'], False) 
        # self.parse2libsvm(2, path + '/' + code + '.raw.csv')
        # self.parse2libsvm(3, path + '/' + code + '.raw.csv')
        self.parse2libsvm(4, path + '/' + code + '.raw.csv')

    def dumpft(self):
        f = open(self.__path + '/' + self.__code +  '.ft.dict', 'w')
        for i in range(0, len(self.__ftdict)):
            f.write(str(i+1) + ',' + self.__ftdict[i + 1]) 
            f.write('\n')
        f.close()

    def loadrange(self, path):
        trange = dict()
        for line in open(path):
            arr = line.strip().split(',')
            tmp = []
            if arr[2] in trange:
                tmp = trange[arr[2]]
            tmp.append(arr)
            trange[arr[2]] = tmp
        return trange

    def loadata(self, path, rflag, gl):
        cnt = 0
        # store feature in dict
        for line in open(path):
            weight   = 1.0
            instance = None

            arr = line.strip().split(',')
            # filter by base_day
            if cnt > 0:
                day = dt.strptime(arr[0], "%Y-%m-%d")
                if day < self.__bday:
                    print 'DEBUG', 'Ignore record before', day, self.__bday
                    continue
                rangein = 0
                qujian  = ''
                for r in rflag:
                    if r in self.__trange:
                        for t in self.__trange[r]:
                            bday = dt.strptime(t[0], "%Y-%m-%d")
                            sday = dt.strptime(t[1], "%Y-%m-%d")
                            if day >= bday and day <= sday:
                                rangein = 1
                                qujian  = r
                                break
                    if rangein == 1:
                        break
                if rangein == 1:
                    if qujian == 'zd':
                        weight = 1.0
                    if qujian == 'xj':
                        weight = 1.0

                if len(rflag) > 0 and rangein == 0:
                    if gl is True:
                        print 'DEBUG', 'Ignore record outof', r, day, bday, sday 
                        continue
            fts  = []
            ret  = []
            nret = 8 
            for i in range(0, len(arr)):
                if cnt == 0:
                    self.__ftdict[i + 1] = arr[i]
                else:
                    if i > 0 and i < (len(arr) - nret):
                        fts.append((i+1, arr[i]))
                    if i >= (len(arr) - nret):
                        ret.append(float(arr[i]))
            if cnt > 0:
                instance = (arr[0], fts, ret, weight)
                self.__instances.append(instance)
            cnt = cnt + 1

    def parse2libsvm(self, tp, filepath):
        f = open(filepath, 'w')
        d = open(filepath + '.debug', 'w')
        w = open(filepath + '.weight', 'w')
        for item in self.__instances:
            fts    = item[1]
            ret    = item[2]
            weight = item[3]
            # 未来3日存在1-暴涨%1, 0-暴跌-%1
            debug = -1
            label = -1 
            if tp == 1:
                tmp  = ret[-3:len(ret)]
                minr = np.min(tmp)
                maxr = np.max(tmp)
                if minr <= -0.01:
                    label = 0 
                if label == -1 and maxr >= 0.01:
                    label = 1 
            if tp == 2:
                tmp = ret[-8]
                if tmp <= -0.01:
                    label = 0 
                if tmp >= 0.01:
                    label = 1
            if tp == 3:
                tmp  = ret[-3:len(ret)]
                minr = np.min(tmp)
                maxr = np.max(tmp)
                if minr <= -0.01 or ret[-8] <= -0.01 or ret[-7] <= -0.01 or ret[-6] <= -0.01:
                    label = 0 
                if label == -1 and (maxr > 0.01 or ret[-8] > 0.01 or ret[-7] > 0.01 or ret[-6] > 0.01):
                    label = 1 
                if label == -1:
                    label = 2
            if tp == 4:
                tmp  = ret[-3:len(ret)]
                minr = np.min(tmp)
                maxr = np.max(tmp)
                # if (minr <= -0.01 or ret[-8] <= -0.01 or ret[-7] <= -0.01 or ret[-6] <= -0.01) and maxr <= 0.02 and ret[-8] <= 0.02 and ret[-7] <= 0.02 and ret[-6] <= 0.02:
                # if minr <= -0.01 or ret[-8] <= -0.01 or ret[-7] <= -0.01 or ret[-6] <= -0.01:
                if minr <= -0.01:
                    label = 0
                else:
                    label = 1
                # elif ret[-3] >= 0.01:
                #     label = 1
                # else:
                #     label = 2 
            # concat features

            # Predict Target Set
            tmp  = ret[-3:len(ret)]
            minr = np.min(tmp)
            maxr = np.max(tmp)
            if minr <= -0.01 or ret[-8] <= -0.01 or ret[-7] <= -0.01 or ret[-6] <= -0.01:
                debug = 0
            if debug == -1 and (maxr >= 0.01 or ret[-8] >= 0.01 or ret[-7] >= 0.01 or ret[-6] >= 0.01):
                debug = 1
            if debug == -1:
                debug = 2
            # Predict Target Set END
            
            # Test
            # if ret[-3] <= -0.01: 
            #     debug = 0
            # else: 
            #     debug = 1 

            out = ''
            for ft in fts:
                # if ft[0] not in {4,28,18,19,20,36,37,38,42,43,48,49}: 
                # if ft[0] not in {42,43,46,47,48,49,28,34,35,36,38,50}: 
                #     continue
                # if ft[0] in {}:
                # if ft[0] in {48,45,37,44,33}:
                # 比较好的特征删选
                # if ft[0] in {48,45,37,44,33,10,43,17,39,47}:
                # if ft[0] in {45,37,44,33,10,43,17,39,47}:
                # if ft[0] in {44,47,45,17}:
                if ft[0] in {}:
                    continue
                out = out + ' ' + str(ft[0]) + ':' + ft[1] 
            
            d.write(item[0] + ',' + str(debug) + out + '\n')

            if label == -1:
                continue

            out = str(label) + out
            f.write(item[0] + ',' + out + '\n') 
            w.write(item[0] + ',' + str(weight) + '\n')

        f.close()
        d.close()
        w.close()

#
