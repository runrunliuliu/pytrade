# coding:utf-8


class ExitSignals(object):

    def __init__(self, mtime, insbdaymap, lasbdayk):
        self.__mtime       = mtime
        self.__insbdaymap  = insbdaymap 
        self.__lasbdayk    = lasbdayk

    def setOHLC(self, op, hi, lw, cl):
        self.__op = op
        self.__hi = hi
        self.__lw = lw
        self.__cl = cl

    # 临峰背离
    def LFpeekBeiLi(self, code, nday, nxhi, nxcl):
        ret = 0
        bbkey = code + '|' + nday
        if bbkey in self.__mtime:
            lfbl   = float(self.__mtime[bbkey][22])
            lfblhi = float(self.__mtime[bbkey][23])
            lfblcl = float(self.__mtime[bbkey][24])

            if lfbl == 2.0:
                if nxhi > lfblhi and nxcl < lfblcl:
                    ret = 1
            if lfbl == 1.0:
                if nxcl < lfblcl:
                    ret = 1
        return ret
    
    # WS MA5
    def WSma5(self, code, nday):
        ret = -1 
        bbkey = code + '|' + nday
        if bbkey in self.__mtime:
            wsma5 = int(self.__mtime[bbkey][4])
            ret   = wsma5 
        return ret

    # GF背离下一个交易日是否保留
    def GFBL(self, code, nday, nxcl):
        ret = 0 
        bbkey = code + '|' + nday
        if bbkey in self.__mtime:
            price = int(self.__mtime[bbkey][6])
            if price > 0 and price < nxcl: 
                ret = 1
        return ret 

    # 持仓时间
    def HoldTime(self, code, bday, nday):
        daymap  = self.__insbdaymap[code]
        lasbday = self.__lasbdayk[code]
        start  = daymap[bday]
        if nday not in daymap:
            end  = daymap[lasbday]
        else:
            end = daymap[nday] 
        holds = end - start + 1
        return holds

    # 跳空低开
    def tkdk(self, code, nday, nxday):
        ret = 0
        nkey = code + '|' + nday
        skey = code + '|' + nxday

        nop = float(self.__op[nkey])
        ncl = float(self.__cl[nkey])
        
        sop = float(self.__op[skey])

        print nday, nxday, code, nop, ncl, sop

        if (ncl - nop) / nop < -0.04 and (sop - ncl) / ncl < -0.025:
            ret = 1
        if ncl < nop and (sop - ncl) / ncl < -0.04:
            ret = 1
        return ret

    # 巨阴破位
    def JYPW(self, code, nday, nxday, price):
        ret = 0
        nkey = code + '|' + nday
        skey = code + '|' + nxday

        ncl = float(self.__cl[nkey])
        sop = float(self.__op[skey])
        scl = float(self.__cl[skey])
        
        if sop > price and scl < price and (scl - ncl) / ncl < -0.08:
            ret = 1
        return ret
#
