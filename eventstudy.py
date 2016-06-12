from pyalgotrade import eventprofiler
from pyalgotrade.technical import stats
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
from utils.utils import TimeUtils
from utils.utils import FileUtils
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.barfeed import indfeed
from pyalgotrade import marketsession
from events import buyOnGap 
from events import shrinkVolRise 
from events import noRiseInPeriod 
from events import timeHit 
from events import qszt 
from events import chaodie 
from events import yidong 
from events import macdseg 
from pyalgotrade.plots import hist
import datetime
from pyalgotrade.barfeed import csvfeed
import numpy as np
import pandas
from collections import Counter
from bokeh.charts import Bar
from utils import utils
from pyalgotrade.utils import instinfo 


def main(plot):
    fromMonth = 1 
    fromDay   = 1
    toMonth   = 2
    toDay     = 24
    start_time = datetime.datetime(2010,fromMonth,fromDay,00,00)
    end_time   = datetime.datetime(2017,toMonth,toDay,00,00)
    barFilter  = csvfeed.CHINAEquitiesRTH(start_time,end_time)
    
    baseinfo = instinfo.InstrumentInfo('data/stockinfo.csv')

    fs = FileUtils('','','')
    codearr = fs.os_walk("./data/dayk")
    fncodearr = utils.parseinst(codearr,'ALL') 
    feed = yahoofeed.Feed()
    
    instfiles = fncodearr 
    # instfiles = [("SH601038.csv","601038"),("SZ002724.csv","002724")]
    # instfiles = [("SH603288.csv","SH603288"),("SZ002079.csv","SZ002079")]
    # instfiles = [("SZ002079.csv","SZ002079")]
    # instfiles = [("SH600298.csv","SH600298")]
    # instfiles = [("SH601288.csv","601288")]
    # instfiles = [("SZ000677.csv","000677")]
    # instfiles = [("SZ002333.csv","SZ002333")]
    # instfiles = [("SZ300369.csv","300369")]
    # instfiles = [("SH601388.csv","601388")]
    # instfiles = [("SZ000001.csv","SZ000001")]
    # instfiles = [("SZ300301.csv","300301")]
    # instfiles = [("SH600257.csv","600257")]
    insts = [] 
    for ele in instfiles:
        inst  = ele[1]
        fname = ele[0] 
        market = marketsession.CHASE()
        feed.setBarFilter(barFilter)
        
        print 'load:', fname
        feed.addBarsFromCSV(inst, "./data/dayk/" + fname,market=market)
        insts.append(inst)

    # predicate = buyOnGap.BuyOnGap(feed)
    # predicate = shrinkVolRise.ShrinkVolRise(feed)
    # predicate = noRiseInPeriod.NoRiseInPeriod(feed)
    # predicate = timeHit.TimeHit(feed,ts)
    # predicate = qszt.QingShiZT(feed)
    # predicate = chaodie.ChaoDie(feed, ts)
    # predicate = yidong.YiDong(feed, ts)
    predicate = macdseg.MacdSeg(feed, baseinfo)

    eventProfiler = eventprofiler.Profiler(predicate, 1, 20)
    eventProfiler.run(feed, 1, True)

    predicate.tradeInfo()

    results = eventProfiler.getResults()
    print "%d events found" % (results.getEventCount())
    eventprofiler.printStats(results, 1.00)

    # predicate.getDaySum()

if __name__ == "__main__":
    main(True)
