# coding:utf-8
import sys
import getopt
from signals.multiperiod import MultiPeriod 
from signals.szl import SZL
from signals.kline import KLINE
from signals.zq import ZHOUQI


def select(dirs, nday):
    pass


def main(argv):
    nday = ''
    code = 'ZS000001'
    try:
        opts, args = getopt.getopt(argv,"h:d:c:m:t:",["day="])
    except getopt.GetoptError:
        print 'test.py -d <time>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -t <time> -o <outputfile>'
            sys.exit()
        elif opt in ("-d", "--day"):
            nday = arg
        elif opt in ("-c", "--code"):
            code = arg
    dirs = './data/'

    # output = './output/select/xt/mp/'
    # sel = MultiPeriod(dirs, nday)
    # sel.select(output)

    # output = './output/xt/mp/'
    # sel.dumpFT(output)

    sel = KLINE(dirs, nday)
    sel.select('NZX')

    sel = ZHOUQI(dirs, nday)
    pairs = [(1, 4, 200), (2, 4, 100), (3, 4, 100), (4, 3, 500)]
    for p in pairs:
        arr = sel.select(p[0], p[1], p[2])
        for sl in arr:
            print 'T+' + str(p[0]), sl[0], sl[1], sl[2]
    sel.get(code)

    output = './output/select/xt/szl/'
    sel = SZL(dirs, nday)
    sel.select(output)

if __name__ == "__main__":
    main(sys.argv[1:])
