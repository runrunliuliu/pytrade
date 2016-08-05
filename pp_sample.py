import sys
import getopt
import multiprocessing as mp
from pyalgotrade import strategy
from pyalgotrade import plotterBokeh
from pyalgotrade.tools import yahoofinance
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.barfeed import csvfeed
from pyalgotrade.stratanalyzer import sharpe
from strategies import intraTrade
from utils.utils import TimeUtils
from utils.utils import FileUtils
from utils.utils import FakeTrade 
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import trades
from pyalgotrade.tools import resample 
from prettytable import PrettyTable
from pyalgotrade import bar 
from pyalgotrade import marketsession
import datetime
from utils import utils
from events import macdseg 
from pyalgotrade import eventprofiler
from pyalgotrade.utils import instinfo 
from mock.triangle import triangle 
from mock.qushi import qushi
from mock.select import select 


def runstrategy(index,fncodearr,div):

    start = div[index][0]
    end   = div[index][1]

    for i in range(start,end + 1):
        inst  = fncodearr[i][1]
        fname = fncodearr[i][0] 

        print 'load:', inst, fname

        fromMonth = 1 
        fromDay   = 1
        toMonth   = 2
        toDay     = 24
        start_time = datetime.datetime(1990,fromMonth,fromDay,00,00)
        end_time   = datetime.datetime(2017,toMonth,toDay,00,00)
        barFilter  = csvfeed.CHINAEquitiesRTH(start_time,end_time)

        dirpath = './data/dayk/'
        feed = yahoofeed.Feed()

        path = None
        market = marketsession.CHASE()
        feed.setBarFilter(barFilter)
        path = dirpath + fname

        feed.addBarsFromCSV(inst, path,market=market)

        # MergeTo MONK
        frequency = bar.Frequency.MONTH
        resample.resample_to_csv(feed, frequency, './data/monk/' + inst + '.csv')
        
        # MergeTo DayK
        # frequency = bar.Frequency.WEEK
        # resample.resample_to_csv(feed, frequency, './data/week/' + inst + '.csv')


def main(argv):
    mode     = 'full'
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
            mode = arg

    fs   = FileUtils('','','')
    dirs = './data/dayk'
    cores = 4 
    codearr = fs.os_walk(dirs)

    if mode == 'full' or mode == 'train':
        fncodearr = utils.parseinst(codearr, bk='ALL') 
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
        processes = [mp.Process(target=runstrategy, args=(x,fncodearr,div)) for x in range(cores)]
        
        # Run processes
        for p in processes:
            p.start()
        
        # Exit the completed processes
        for p in processes:
            p.join()

if __name__ == "__main__":
    main(sys.argv[1:])
# -*- coding: utf-8 -*-
