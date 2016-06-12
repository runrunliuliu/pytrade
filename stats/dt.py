import collections
import bisect
import numpy as np
import pandas as pd
from pandas import DataFrame, read_csv


# dtboard
class DT(object):

    def __init__(self,db,ts,fname,match):
        self.__db = db
        self.__file = fname
        self.__ts  = ts
        self.__match = match

    def compute(self):
        df = pd.read_csv(self.__file,dtype={'code':np.str})
        buy = df['b11'] - df['b12'] \
            + df['b21'] - df['b22'] \
            + df['b31'] - df['b32'] \
            + df['b41'] - df['b42'] \
            + df['b51'] - df['b52']

        sell = df['s12'] - df['s11'] \
            + df['s22'] - df['s21'] \
            + df['s32'] - df['s31'] \
            + df['s42'] - df['s41'] \
            + df['s52'] - df['s51']

        df['rate'] = buy / sell
        df['test'] = 1 
        cols_to_keep = ['Date','code','rate', 'test']
        return df[cols_to_keep].sort_values('rate', ascending=True).drop_duplicates(subset=['Date','code']).sort_values('Date')
#
