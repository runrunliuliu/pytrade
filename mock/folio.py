import pyfolio as pf
import pandas as pd
import datetime
import empyrical
from matplotlib.backends.backend_pdf import PdfPages
from pyfolio import round_trips


class folio(object):

    def __init__(self, start=None, end=None):
        strategy = self.initRets('./backtests/20060104_20160104.rets.csv', 'triangle', 'cash')
        self.__strategy = strategy.T.iloc[0]

        szzs = self.initRets('./data/dayk/ZS000001.csv', 'SZZS', 'Close')
        szzs = szzs[(szzs.index >= start) & (szzs.index <= end)]

        hs300 = self.initRets('./data/dayk/ZS000300.csv', 'HS300', 'Close')
        hs300 = hs300[(hs300.index >= start) & (hs300.index <= end)]

        self.__base = hs300.T.iloc[0]

        self.__trans = self.initTrans('./backtests/20060104_20160104.trans.csv')

    def initRets(self, fname, symbol, attr):
        df = pd.read_csv(fname, index_col=0)
        df.index = pd.to_datetime(df.index)

        rets = df[[attr]].pct_change().dropna()

        rets.index = rets.index.tz_localize("UTC")
        rets.columns = [symbol]

        return rets

    def initTrans(self, fname):
        df = pd.read_csv(fname)
        df.open_dt  = pd.to_datetime(df.open_dt)
        df.close_dt = pd.to_datetime(df.close_dt)
        return df

    def tearTrans(self):
        pp  = PdfPages('./backtests/transpage.pdf')
        fig = pf.create_transactions_tear_sheet(self.__trans, return_fig=True)
        fig.savefig(pp, format='pdf')
        pp.close()

    def tearsheet(self):
        pp  = PdfPages('./backtests/multipage.pdf')
        fig = pf.create_returns_tear_sheet(self.__strategy, benchmark_rets=self.__base, return_fig=True)
        fig.savefig(pp, format='pdf')
        pp.close()
