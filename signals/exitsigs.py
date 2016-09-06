# coding:utf-8


class ExitSignals(object):

    def __init__(self, mtime):
        self.__mtime = mtime

    # 临峰背离
    def LFpeekBeiLi(self, code, nday):
        bbkey = code + '|' + nday
        if bbkey in self.__mtime:
            lfbl   = float(self.__mtime[bbkey][23])
            lfblhi = float(self.__mtime[bbkey][24])
            lfblcl = float(self.__mtime[bbkey][25])

            print code, nday, lfbl, lfblhi, lfblcl 

#
