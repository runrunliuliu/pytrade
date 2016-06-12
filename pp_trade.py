import multiprocessing as mp
from pyalgotrade import strategy
from pyalgotrade import plotterBokeh
from pyalgotrade.tools import yahoofinance
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.feed import csvfeed
from pyalgotrade.stratanalyzer import sharpe
from strategies import intraTrade
from utils.utils import TimeUtils
from utils.utils import FileUtils
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import trades
from prettytable import PrettyTable
from pyalgotrade import bar 
from pyalgotrade import marketsession


def parseinst(codearr):
    out = []
    for c in codearr:
        tmp = c.split('-')
        fname = tmp[-1] 
        code  = fname[2:8]
        out.append((fname,code))
    return out


def runstrategy(index,fncodearr,div,plot):

    start = div[index][0]
    end   = div[index][1]

    for i in range(start,end + 1):
        inst  = fncodearr[i][1]
        fname = fncodearr[i][0] 

        inst  = '601688'
        fname = 'SH601688.csv'
        inst  = '300027'
        fname = 'SZ300027.csv'
        inst  = '000001'
        fname = 'SZ000001.csv.sample'

        ts = TimeUtils()
        ind_dt = './data/dtboard.csv.out'

        market = marketsession.FTSE()
        instrument = inst 
        feed = yahoofeed.Feed(frequency=bar.Frequency.MINUTE)
        feed.addBarsFromCSV(instrument, "./data/mink/" + fname, market=market)

        st = intraTrade.IntraTrade(feed,instrument,ind_dt,ts)

        retAnalyzer = returns.Returns()
        st.attachAnalyzer(retAnalyzer)

        sharpeRatioAnalyzer = sharpe.SharpeRatio()
        st.attachAnalyzer(sharpeRatioAnalyzer)

        drawDownAnalyzer = drawdown.DrawDown()
        st.attachAnalyzer(drawDownAnalyzer)

        tradesAnalyzer = trades.Trades()
        st.attachAnalyzer(tradesAnalyzer)

        if plot:
            plt = plotterBokeh.StrategyPlotter(st, True, True, True)

        st.run()

        sharp = sharpeRatioAnalyzer.getSharpeRatio(0.05)
        rets  = retAnalyzer.getCumulativeReturns()[-1] * 100
        ddowns = drawDownAnalyzer.getMaxDrawDown() * 100

        trets   = tradesAnalyzer.getAllReturns()
        tcnt    = tradesAnalyzer.getCount()
        preturns = tradesAnalyzer.getPositiveReturns()
        nreturns = tradesAnalyzer.getNegativeReturns()

        tavg  = 0
        if tcnt > 0:
            tavg = trets.mean()
       
        if len(nreturns) > 0:
            loss = nreturns.min() * 100
            print loss
        print "%s,%.2f,%.2f,%.2f,%d,%.2f,%d,%d" % (instrument,sharp,rets,ddowns,tcnt,tavg,len(preturns),len(nreturns))

        if plot:
            plt.plot()
            plt.show()

        exit()


def main(plot):

    fs = FileUtils('','','')
    print "code,sharp,returns,drawdown,tcnt,tavg"

    codearr = fs.os_walk("./data/mink")
    fncodearr = parseinst(codearr) 

    div   = dict()
    block = len(fncodearr) / 10
    left  = len(fncodearr) % 10
    start = 0
    for x in range(10):
        div[x] = (start,block * (x + 1) - 1) 
        start  = start + block
    end = div[9][1] + left
    div[9] = (div[9][0],end)

    # Setup a list of processes that we want to run
    processes = [mp.Process(target=runstrategy, args=(x,fncodearr,div,plot)) for x in range(1)]
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()

if __name__ == "__main__":
    main(False)
    # main(True)
# -*- coding: utf-8 -*-
