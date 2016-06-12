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


def main(plot):
    fromMonth = 1 
    fromDay   = 1
    toMonth   = 2
    toDay     = 24
    start_time = datetime.datetime(1990,fromMonth,fromDay,00,00)
    end_time   = datetime.datetime(2017,toMonth,toDay,00,00)
    barFilter  = csvfeed.CHINAEquitiesRTH(start_time,end_time)
    baseinfo = instinfo.InstrumentInfo('data/stockinfo.csv')

    dirpath = './data/dayk/'
    fs = FileUtils('','','')
    codearr = fs.os_walk(dirpath)
    fncodearr = parseinst(codearr,'ALL') 
    feed = yahoofeed.Feed()
    
    instfiles = fncodearr 
    # instfiles = [("SH600007.csv","SH600007"),("SZ002333.csv","SZ002333")]
    # instfiles = [("SZ000629.csv","SZ000629")]
    # instfiles = [("SZ300315.csv","SZ300315")]
    # instfiles = [("SZ300294.csv","SZ300294")]
    # instfiles = [("SH603003.csv","SH603003")]
    # instfiles = [("SH600326.csv","SH600326")]
    # instfiles = [("SZ000540.csv","SZ000540")]
    # instfiles = [("SZ300346.csv","SZ300346")]
    # instfiles = [("SZ300358.csv","SZ300358")]
    # instfiles = [("SZ000677.csv","SZ000677")]
    # instfiles = [("SH600069.csv","SH600069")]
    # instfiles = [("SH600737.csv","SH600737")]
    # instfiles = [("SH601328.csv","SH601328")]
    # instfiles = [("SH600395.csv","SH600395")]
    # instfiles = [("SH600666.csv","SH600666")]
    # instfiles = [("SH600502.csv","SH600502")]
    # instfiles = [("SH600383.csv","SH600383")]
    # instfiles = [("SH600706.csv","SH600706")]
    # instfiles = [("SH601766.csv","SH601766")]
    # instfiles = [("SZ000403.csv","SZ000403")]
    # instfiles = [("SZ300007.csv","SZ300007")]
    # instfiles = [("SZ000001.csv","SZ000001")]
    # instfiles = [("SZ300098.csv","SZ300098")]
    # instfiles = [("SH600243.csv","SH600243")]
    instfiles = [("ZS000001.csv","ZS000001")]
    # instfiles = [("ZS399006.csv","ZS399006")]
    insts  = [] 

    path = None
    for ele in instfiles:
        inst  = ele[1]
        fname = ele[0] 
        market = marketsession.CHASE()
        feed.setBarFilter(barFilter)

        path = dirpath + fname

        feed.addBarsFromCSV(inst, path,market=market)
        insts.append(inst)

    predicate = macdseg.MacdSeg(feed, baseinfo)

    eventProfiler = eventprofiler.Profiler(predicate, 1, 1)
    eventProfiler.run(feed, 2, True)

    # baseday  = '2016-04-21'
    # startday = '2016-01-27'
    # ft = utils.FakeTrade(codearr, dirpath, startday, baseday)
    # ft.tradeInfo()
    dump = utils.DumpFeature(predicate, instfiles, dirpath) 
    dump.ToDump()


if __name__ == "__main__":
    main(True)
