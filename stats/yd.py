import collections
import bisect
import numpy as np
import pandas as pd
from pandas import DataFrame, read_csv


class YD(object):

    def __init__(self,db,ts,fname,match):
        self.__db = db
        self.__file = fname
        self.__ts  = ts
        self.__match = match

    def compute(self):
        df = pd.read_csv(self.__file, sep="\t", dtype={'code':np.str})
        df['period'] = ( df.minute / 1445 )
        df.period = df.period.astype(int)
        gb = df.groupby(['Date', 'code', 'period'])
        mk = gb.agg({'percentage':[np.min,np.max]})
        mk = mk.reset_index()
        mk['Date'] = pd.to_datetime(mk['Date'],format="%Y%m%d")
        ncol = [''.join(t) for t in mk.columns]
        mk.columns = ncol 
        return mk
#
