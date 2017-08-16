import sys
import getopt
import threading
from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from utils.utils import TimeUtils
from utils.utils import FileUtils
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.barfeed import indfeed
from pyalgotrade.plots import candle
from pyalgotrade import marketsession
from events import macdseg
from pyalgotrade.plots import hist
import datetime
from pyalgotrade.barfeed import csvfeed
import numpy as np
import pandas
from collections import Counter
from bokeh.charts import Bar
import pandas as pd
from utils import utils
from pyalgotrade.utils import instinfo
from mock.triangle import triangle
from pyalgotrade import bar
from conf import log
import multiprocessing as mp
from multiprocessing import Process, Queue
import logging
import logging.config
import logging.handlers
import logutils
from logutils.queue import QueueHandler, QueueListener


def parseinst(codearr, bk='ALL'):
    out = []
    for c in codearr:
        tmp   = c.split('-')
        fname = tmp[-1]
        code  = fname[2:8]
        f2 = code[0:3]
        if bk == 'CYB' and f2 == '300':
            out.append((fname,code))
        if bk == 'ZB' and f2 == '600':
            out.append((fname,code))
        if bk == 'ALL':
            out.append((fname,code))

    return out


def logger_thread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def main(plot, argv):

    # Get Parameters
    period = 'day'
    try:
        opts, args = getopt.getopt(argv,"h:p:",["day="])
    except getopt.GetoptError:
        print 'test.py -d <time>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -t <time> -o <outputfile>'
            sys.exit()
        elif opt in ("-p", "--period"):
            period = arg

    # Train Data
    # fromMonth = 1 
    # fromDay   = 1
    # toMonth   = 12
    # toDay     = 24
    # start_time = datetime.datetime(2001,fromMonth,fromDay,00,00)
    # end_time   = datetime.datetime(2019,toMonth,toDay,00,00)

    fromMonth = 9
    fromDay   = 1
    toMonth   = 12
    toDay     = 24
    start_time = datetime.datetime(2015,fromMonth,fromDay,00,00)
    end_time   = datetime.datetime(2019,toMonth,toDay,00,00)

    barFilter  = csvfeed.CHINAEquitiesRTH(start_time,end_time)
    baseinfo = instinfo.InstrumentInfo('data/stockinfo.csv')

    freq = bar.Frequency.DAY
    dirpath = './data/dayk/'
    if period == 'week':
        dirpath = './data/week/'
        freq = bar.Frequency.WEEK
    if period == 'month':
        dirpath = './data/monk/'
        freq = bar.Frequency.MONTH
    if period == '15min':
        dirpath = './data/15mink/'
        freq = bar.Frequency.MIN15
    if period == '30min':
        dirpath = './data/30mink/'
        freq = bar.Frequency.MIN30

    fs = FileUtils('','','')
    codearr = fs.os_walk(dirpath)
    fncodearr = parseinst(codearr,'ALL')
    feed = yahoofeed.Feed(frequency=freq)

    instfiles = fncodearr
    instfiles = [("ZS000001.csv","ZS000001")]
    insts  = []

    # LOG CONFIGURE
    q = Queue()
    logging.config.dictConfig(log.d)

    path = None
    for ele in instfiles:
        inst  = ele[1]
        fname = ele[0]
        market = marketsession.CHASE()
        feed.setBarFilter(barFilter)

        path = dirpath + fname

        feed.addBarsFromCSV(inst, path,market=market)
        insts.append(inst)

    lp = threading.Thread(target=logger_thread, args=(q,))
    lp.daemon = True
    lp.start()

    predicate = macdseg.MacdSeg(feed, baseinfo, q)

    eventProfiler = eventprofiler.Profiler(predicate, 1, 1)
    eventProfiler.run(feed, 2, True)

    dump = utils.DumpFeature(predicate, instfiles, dirpath, period)
    dump.ToDump()

    q.put(None)

if __name__ == "__main__":
    main(True, sys.argv[1:])
