# -*- coding: utf-8 -*-
import sys
from pyalgotrade import strategy
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import ma
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.utils import stats
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.tools import utils 
from pyalgotrade.tools import parallel 
from pyalgotrade import plotterBokeh
from strategies import dtstrategy 
from strategies import shrinkVol 
from strategies import mlstrategy 
from utils.utils import TimeUtils
from utils.utils import FileUtils
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from prettytable import PrettyTable
from pyalgotrade import marketsession
import datetime
from pyalgotrade.barfeed import csvfeed


def parseinst(codearr):
    out = []
    for c in codearr:
        tmp   = c.split('-')
        fname = tmp[-1]
        code  = fname[2:8]
        out.append((fname,code))
    return out


def run_strategy(plot):

    fromMonth = 1 
    fromDay   = 1
    toMonth   = 1 
    toDay     = 1 
    start_time = datetime.datetime(2001,fromMonth,fromDay,00,00)
    end_time   = datetime.datetime(2012,toMonth,toDay,00,00)
    barFilter  = csvfeed.CHINAEquitiesRTH(start_time,end_time)

    ts = TimeUtils()
    ind_dt = './data/dtboard.csv.out'

    fs = FileUtils('','','')
    codearr = fs.os_walk("./data/dayk")
    fncodearr = parseinst(codearr) 
    
    feed = yahoofeed.Feed()
    
    instfiles = fncodearr 
    # instfiles = [("SH601038.csv","601038"),("SZ002724.csv","002724")]
    # instfiles = [("SZ000803.csv","000803")]
    # instfiles = [("SZ000977.csv","000977")]
    instfiles = [("SH600279.csv","600279")]
    # instfiles = [("SZ300100.csv","300100")]
    # instfiles = [("SH600209.csv","600209"),("SZ000803.csv","000803")]
    # instfiles = [("SH603099.csv","603099")]
    # instfiles = [("SZ000819.csv","000819")]
    insts = [] 
    for ele in instfiles:
        inst  = ele[1]
        fname = ele[0] 
        market = marketsession.CHASE()
        feed.setBarFilter(barFilter)
        feed.addBarsFromCSV(inst, "./data/dayk/" + fname,market=market)
        insts.append(inst)

    # Evaluate the strategy with the feed.
    # st = dtstrategy.DtStrategy(feed,insts,ind_dt,ts)
    # st = shrinkVol.ShrinkVol(feed,insts,ind_dt,ts)
    st = mlstrategy.MLStrategy(feed,insts,ind_dt,ts)

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

    # profits = tradesAnalyzer.getAll()
    trets   = tradesAnalyzer.getAllReturns()
    tcnt    = tradesAnalyzer.getCount()
    profits = tradesAnalyzer.getProfits()

    preturns = tradesAnalyzer.getPositiveReturns()
    num_wins = len(preturns)
    nreturns = tradesAnalyzer.getNegativeReturns()
    num_loss = len(nreturns)
    tavg  = 0
    if tcnt > 0:
        tavg = trets.mean()

    t = PrettyTable(['Name', 'Value'])
    t.float_format = '.4'
    t.add_row(['组合收益',st.getResult()])
    t.add_row(['夏普率', sharp])
    t.add_row(['收益率', rets])
    t.add_row(['最大回撤', ddowns])
    t.add_row(['总交易次数', tcnt])
    t.add_row(['平均收益率', tavg])
    t.add_row(['获胜概率', num_wins / (num_wins + num_loss + 0.00001) ])
    
    t.add_row(['组合收益均值',profits.mean()])
    t.add_row(['收益方差',profits.std()])
    t.add_row(['最大收益',profits.max()])
    t.add_row(['最小收益',profits.min()])

    pmean = 0
    pstd  = 0
    pmin  = 0
    pmax  = 0
    if len(preturns) > 0:
        pmean = preturns.mean()
        pstd  = preturns.std()
        pmin  = preturns.min()
        pmax  = preturns.max()

    t.add_row(['正收益率均值',pmean])
    t.add_row(['正收益方差',pstd])
    t.add_row(['最大收益',pmax])
    t.add_row(['最小收益',pmin])

    nmean = 0
    nstd  = 0
    nmin  = 0
    nmax  = 0
    if len(nreturns) > 0:
        nmean = nreturns.mean()
        nstd  = nreturns.std()
        nmin  = nreturns.min()
        nmax  = nreturns.max()
    t.add_row(['亏损均值',nmean])
    t.add_row(['亏损方差',nstd])
    t.add_row(['最大亏损',nmin])
    t.add_row(['最小亏损',nmax])

    t.align = 'l'
    print t
    # print "%.2f,%.2f,%.2f,%d,%.2f" % (sharp,rets,ddowns,tcnt,tavg)

    if plot:
        plt.plot()
        plt.show()

run_strategy(False)
