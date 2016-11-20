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

        self.loadata(path + '/' + code + '.ft.csv') 
        # self.parse2libsvm(2, path + '/' + code + '.raw.csv')
        self.parse2libsvm(3, path + '/' + code + '.raw.csv')
        # self.parse2libsvm(4, path + '/' + code + '.raw.csv')

    def dumpft(self):
        f = open(self.__path + '/' + self.__code +  '.ft.dict', 'w')
        for i in range(0, len(self.__ftdict)):
            f.write(str(i+1) + ',' + self.__ftdict[i + 1]) 
            f.write('\n')
        f.close()

    def loadata(self, path):
        cnt = 0
        # store feature in dict
        for line in open(path):
            instance = None

            arr = line.strip().split(',')
            # filter by base_day
            if cnt > 0:
                day = dt.strptime(arr[0], "%Y-%m-%d")
                if day < self.__bday:
                    print 'DEBUG', 'Ignore record before', day, self.__bday
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
                instance = (arr[0], fts, ret)
                self.__instances.append(instance)
            cnt = cnt + 1

    def parse2libsvm(self, tp, filepath):
        f = open(filepath, 'w')
        d = open(filepath + '.debug', 'w')
        for item in self.__instances:
            fts = item[1]
            ret = item[2]
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
                # if minr <= -0.01:
                #     label = 0 
                #     debug = 0
                # if label == -1 and maxr >= 0.01:
                #     label = 1 
                #     debug = 1
                # if label == -1:
                #     label = 2
                #     debug = 2
                if minr <= -0.01 or ret[-8] <= -0.01 or ret[-7] <= -0.01 or ret[-6] <= -0.01:
                    label = 0 
                    debug = 0
                if label == -1 and (maxr >= 0.01 or ret[-8] >= 0.01 or ret[-7] >= 0.01 or ret[-6] >= 0.01):
                    label = 1 
                    debug = 1
                if label == -1:
                    label = 2
                    debug = 2
            if tp == 4:
                if ret[-6] <= -0.01:
                    label = 0
                elif ret[-6] >= 0.01:
                    label = 1
                else:
                    label = 2 
            # concat features
            out = ''
            for ft in fts:
                # if ft[0] < 4 or ft[0] > 11:
                #    continue
                out = out + ' ' + str(ft[0]) + ':' + ft[1] 
            
            d.write(item[0] + ',' + str(debug) + out + '\n')

            if label == -1:
                continue

            out = str(label) + out
            f.write(item[0] + ',' + out + '\n') 
        f.close()
        d.close()

#
