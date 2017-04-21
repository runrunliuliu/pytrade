# coding:utf-8


class ETL(object):

    def __init__(self, index, codearr, div, dirs):
        self.__opset = {}
        self.__clset = {}
        self.__hiset = {}
        self.__lwset = {}

        self.__dayzq = {}
        self.__zqday = {}
        self.__codes = []

        start = div[index][0]
        end   = div[index][1]
        for i in range(start,end + 1):
            fname = codearr[i][0]
            fsize = fname.split('.')
            if len(fsize) > 2:
                continue
            code  = fname[0:8]
            self.loadDayK(dirs, code)
            self.__codes.append(code)

    # 获取Process代码集合
    def getCodes(self):
        return self.__codes

    # 获取序列号
    def getZQ(self, code, day):
        return self.__dayzq[code + '|' + day]

    def getDay(self, code, zq):
        return self.__dayzq[code + '|' + str(zq)]

    # 加载日K线
    def loadDayK(self, dirs, code):
        cnt = 0
        fname = dirs + '/' + code + '.csv'
        for line in open(fname):
            if cnt == 0:
                cnt = cnt + 1
                continue
            tmp = line.strip().split(',')
            day = tmp[0]
            op  = tmp[1]
            hi  = tmp[2]
            lw  = tmp[3]
            cl  = tmp[4]
            self.__opset[code + '|' + day] = float(op)
            self.__clset[code + '|' + day] = float(cl) 
            self.__hiset[code + '|' + day] = float(hi)
            self.__lwset[code + '|' + day] = float(lw)

            self.__dayzq[code + '|' + day]      = cnt 
            self.__dayzq[code + '|' + str(cnt)] = day 
            cnt = cnt + 1
