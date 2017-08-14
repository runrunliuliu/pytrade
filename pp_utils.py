# coding:utf-8
import sys
import os
import getopt
import multiprocessing as mp
from strategies import intraTrade
from utils.utils import TimeUtils
from utils.utils import FileUtils
from utils.utils import FakeTrade
from ml.czsc import CZSC
import datetime
from utils import utils
from events import macdseg
from events import month
from pyalgotrade.utils import instinfo


# 格式转换
def TransFormat(index, fncodearr, div, dirs):
    start = div[index][0]
    end   = div[index][1]
    for i in range(start,end + 1):
        fname = fncodearr[i][0]
        oname = fname.split('_')[0]
        period = fname.split('_')[1].split('.')[0]

        header = ('Date','Open','High','Low','Close','Volume','Adj Close')
        output = []
        output.append(header)

        odir = ''
        cnt  = 0
        for line in open(dirs + '/' + fname):
            if cnt == 0:
                cnt = cnt + 1
                continue
            day = ''
            tmp = line.strip().split(',')
            dt  = datetime.datetime.fromtimestamp(long(tmp[0]))
            if period == 'm':
                odir = 'monk'
                day  = dt.strftime('%Y-%m-%d')
            if period == 'w':
                odir = 'week'
                day  = dt.strftime('%Y-%m-%d')
            if period == '30':
                odir = '30mink'
                day  = dt.strftime('%Y-%m-%d-%H-%M')
            if period == '60':
                odir = '60mink'
                day  = dt.strftime('%Y-%m-%d-%H-%M')
            nline = (day, tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[4])
            output.append(nline)
            cnt = cnt + 1

        odir = './data/output/' + odir
        if not os.path.exists(odir):
            os.makedirs(odir)
        print 'D_TRANS:', odir, oname
        f = open(odir + '/' + oname, 'w')
        for v in output:
            out = ''
            for t in v:
                out = out + ',' + str(t)
            f.write(out[1:])
            f.write('\n')
        f.close()


# 获取最后行
def GetLastLine(index, fncodearr, div, dirs, odir):
    start = div[index][0]
    end   = div[index][1]
    for i in range(start,end + 1):
        fname = fncodearr[i][0]
        oname = fname.split('_')[0]
        line  = ''
        for line in open(dirs + '/' + fname):
            line = line.strip()
            continue
        f = open(odir + '/' + oname + '.csv', 'w')
        f.write(line)
        f.write('\n')
        f.close()


# CZSC训练集生产
def GenCZSC(index, fncodearr, div, dirs, odir):
    czsc = CZSC(index, fncodearr, div, dirs)
    czsc.run()


# MAIN
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"h:d:s:m:t:",["day="])
    except getopt.GetoptError:
        print 'test.py -d <time>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -t <time> -o <outputfile>'
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode  = arg
        elif opt in ("-d", "--mode"):
            day  = arg

    fs   = FileUtils('','','')

    bk   = 'ALL'
    dirs = './data/dayk/'
    if mode == 'trans':
        dirs = './data/tmp'
        bk   = 'TMP'
    if mode == 'line':
        bk   = 'LINE'
        dirs = './data/dayk/xingtai/'
        odir = './data/dayk/' + day
    if mode == 'czsc':
        odir = './data/czsc/' + day

    cores = 32
    codearr = fs.os_walk(dirs)
    fncodearr = utils.parseinst(codearr, bk=bk)
    div   = dict()
    block = len(fncodearr) / cores
    left  = len(fncodearr) % cores
    start = 0
    for x in range(cores):
        div[x] = (start,block * (x + 1) - 1)
        start  = start + block
    end = div[cores - 1][1] + left
    div[cores - 1] = (div[cores - 1][0],end)

    # Setup a list of processes that we want to run
    if mode == 'trans':
        processes = [mp.Process(target=TransFormat, args=(x,fncodearr,div, dirs)) for x in range(cores)]
    if mode == 'line':
        processes = [mp.Process(target=GetLastLine, args=(x,fncodearr,div, dirs, odir)) for x in range(cores)]
    if mode == 'czsc':
        processes = [mp.Process(target=GenCZSC, args=(x,fncodearr,div, dirs, odir)) for x in range(cores)]
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()

if __name__ == "__main__":
    main(sys.argv[1:])
# -*- coding: utf-8 -*-
