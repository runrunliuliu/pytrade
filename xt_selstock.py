# coding:utf-8
import sys
import getopt
from signals.multiperiod import MultiPeriod 
from signals.szl import SZL


def main(argv):
    nday = ''
    try:
        opts, args = getopt.getopt(argv,"h:d:s:m:t:",["day="])
    except getopt.GetoptError:
        print 'test.py -d <time>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -t <time> -o <outputfile>'
            sys.exit()
        elif opt in ("-d", "--day"):
            nday = arg
    dirs = './data/'

    output = './output/select/xt/mp/'
    sel = MultiPeriod(dirs, nday)
    sel.select(output)

    output = './output/xt/mp/'
    sel.dumpFT(output)

    output = './output/select/xt/szl/'
    sel = SZL(dirs, nday)
    sel.select(output)

if __name__ == "__main__":
    main(sys.argv[1:])
