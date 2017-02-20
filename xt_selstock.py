# coding:utf-8
import sys
import getopt
from signals.multiperiod import MultiPeriod 


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

    sel = MultiPeriod(dirs, nday)
    sel.select()

if __name__ == "__main__":
    main(sys.argv[1:])
