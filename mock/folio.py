import pyfolio as pf
import pandas as pd
import datetime
import empyrical
from matplotlib.backends.backend_pdf import PdfPages


class folio(object):

    def __init__(self, start=None, end=None):
        strategy = self.initRets('./backtests/20060104_20160104.rets.csv', 'triangle', 'cash')
        self.__strategy = strategy.T.iloc[0]

        szzs = self.initRets('./data/dayk/ZS000001.csv', 'SZZS', 'Close')
        szzs = szzs[(szzs.index >= start) & (szzs.index <= end)]
        self.__szzs = szzs.T.iloc[0]

    def initRets(self, fname, symbol, attr):
        df = pd.read_csv(fname, index_col=0)
        df.index = pd.to_datetime(df.index)

        rets = df[[attr]].pct_change().dropna()

        rets.index = rets.index.tz_localize("UTC")
        rets.columns = [symbol]

        return rets

    def tearsheet(self):
        pp  = PdfPages('multipage.pdf')
        fig = pf.create_returns_tear_sheet(self.__strategy, benchmark_rets=self.__szzs, return_fig=True)
        fig.savefig(pp, format='pdf')
        pp.close()
