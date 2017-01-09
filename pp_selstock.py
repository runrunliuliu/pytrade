import sys
import getopt
import json
import threading
from conf import log
import multiprocessing as mp
from multiprocessing import Process, Queue
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
from prettytable import PrettyTable
from pyalgotrade import bar 
from pyalgotrade import marketsession
import datetime
from utils import utils
from mock import folio 
from events import macdseg 
from pyalgotrade import eventprofiler
from pyalgotrade.utils import instinfo 
from mock.triangle import triangle 
from mock.qushi import qushi
from mock.nbs import NBS 
from mock.kline import KLINE 
from mock.select import select 
import logging
import logging.config
import logging.handlers
import logutils
from logutils.queue import QueueHandler, QueueListener


def logger_thread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def runstrategy(index,fncodearr,div, dirpath, freq, q):

    start = div[index][0]
    end   = div[index][1]

    for i in range(start,end + 1):
        inst  = fncodearr[i][1]
        fname = fncodearr[i][0] 

        fromMonth = 1 
        fromDay   = 1
        toMonth   = 2
        toDay     = 24
        start_time = datetime.datetime(1990,fromMonth,fromDay,00,00)
        end_time   = datetime.datetime(2017,toMonth,toDay,00,00)
        barFilter  = csvfeed.CHINAEquitiesRTH(start_time,end_time)

        baseinfo = instinfo.InstrumentInfo('data/stockinfo.csv')
        instfiles = [fncodearr[i]] 
        feed = yahoofeed.Feed(frequency=freq)

        path = None
        market = marketsession.CHASE()
        feed.setBarFilter(barFilter)
        path = dirpath + fname

        feed.addBarsFromCSV(inst, path,market=market)

        predicate = macdseg.MacdSeg(feed, baseinfo, q)

        eventProfiler = eventprofiler.Profiler(predicate, 1, 1)
        eventProfiler.run(feed, 2, True)

        dump = utils.DumpFeature(predicate, instfiles, dirpath)
        dump.ToDump()


def main(argv):
    startday = '2016-01-27'
    baseday  = '2016-04-15'
    mode     = 'full'
    trade    = ''
    period   = 'day'
    try:
        opts, args = getopt.getopt(argv,"h:d:s:m:t:p:",["day="])
    except getopt.GetoptError:
        print 'test.py -d <time>'
        sys.exit(2)
    if len(opts) < 4:
        print 'main.py -s <startday> -d <endday> -m <mode:full|mock> -t <trade>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -t <time> -o <outputfile>'
            sys.exit()
        elif opt in ("-d", "--dday"):
            baseday  = arg
        elif opt in ("-s", "--sday"):
            startday = arg
        elif opt in ("-m", "--mode"):
            mode     = arg
        elif opt in ("-t", "--trade"):
            trade    = arg
        elif opt in ("-p", "--period"):
            period   = arg

    fs   = FileUtils('','','')

    freq = bar.Frequency.DAY
    dirs = './data/dayk/'
    if period == 'week':
        dirs = './data/week/'
        freq = bar.Frequency.WEEK
    if period == 'month':
        dirs = './data/monk/'
        freq = bar.Frequency.MONTH

    # LOG CONFIGURE
    q = Queue()
    logging.config.dictConfig(log.d)

    cores = 32
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
        processes = [mp.Process(target=runstrategy, args=(x,fncodearr,div, dirs, freq, q)) for x in range(cores)]
        
        # Run processes
        for p in processes:
            p.start()

        lp = threading.Thread(target=logger_thread, args=(q,))
        lp.daemon = True
        lp.start()

        # Exit the completed processes
        for p in processes:
            p.join()

        q.put(None)

    if mode == 'full' or mode == 'mock':
        strat   = None
        if trade == 'triangle':
            forcetp = 7
            strat = triangle(startday, baseday, codearr, dirs, forcetp)
        if trade == 'nbs':
            forcetp = 9 
            strat = NBS(startday, baseday, codearr, dirs, forcetp)
        if trade == 'kline':
            forcetp = 11 
            strat = KLINE(startday, baseday, codearr, dirs, forcetp)
        ft = utils.FakeTrade(codearr, dirs, startday, baseday, strat, forcetp)
        ft.mock()
        pf = folio.folio(startday, baseday)
        pf.tearsheet()
        pf.tearTrans()

    if mode == 'stock':
        subdir  = ''
        strat   = None
        forcetp = -1 
        if trade == 'triangle':
            forcetp = 7
            subdir = 'triangle'
            strat = triangle(startday, baseday, codearr, dirs, forcetp)
        if trade == 'QUSHI':
            subdir = 'qushi'
            strat = qushi(startday, baseday, codearr, dirs, forcetp)
        if trade == 'nbs':
            forcetp = 9 
            subdir = 'nbs'
            strat = NBS(startday, baseday, codearr, dirs, forcetp)
        if trade == 'kline':
            forcetp = 11 
            subdir = 'kline'
            strat = KLINE(startday, baseday, codearr, dirs, forcetp)
        ft = utils.FakeTrade(codearr, dirs, startday, baseday, strat, forcetp)
        ft.select(dirs, subdir, forcetp, trade)

if __name__ == "__main__":
    main(sys.argv[1:])
# -*- coding: utf-8 -*-
