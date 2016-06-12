# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import sys


def swap(df, col, index):
    b = df.pop(col)
    df.insert(index, col, b)
    return df

enday = sys.argv[1]

# 股票代码和名称
# data = ts.get_industry_classified()
# df = data.ix[:,0:3]
# df.index.name = 'number'
# df.columns = ['code', 'name', 'c_name']
# df = df.sort_index()
# df.to_csv('data/stockinfo.csv', encoding='utf8')
# data = ts.get_h_data('399001', index=True, start='2010-01-01', end=enday)
# df = data.ix[:,0:5]
# df.index.name = 'Date'
# df['Adj Close'] = df.close
# df.columns = ['Open', 'High', 'Close', 'Low', 'Volume', 'Adj Close']
# df = swap(df, 'Low', 2)
# df = df.sort_index()
# df.to_csv('data/dayk/ZS399001.csv')

data = ts.get_h_data('000001', index=True, start='1997-01-01', end=enday)
df = data.ix[:,0:5]
df.index.name = 'Date'
df['Adj Close'] = df.close
df.columns = ['Open', 'High', 'Close', 'Low', 'Volume', 'Adj Close']
df = swap(df, 'Low', 2)
df = df.sort_index()
df.to_csv('data/dayk/ZS000001.csv')


# 创业板
# data = ts.get_h_data('399006', index=True, start='2010-05-01', end=enday)
# df = data.ix[:,0:5]
# df.index.name = 'Date'
# df['Adj Close'] = df.close
# df.columns = ['Open', 'High', 'Close', 'Low', 'Volume', 'Adj Close']
# df = swap(df, 'Low', 2)
# df = df.sort_index()
# df.to_csv('data/dayk/ZS399006.csv')

# 深综指数 
# data = ts.get_h_data('399106', index=True, start='2010-05-01', end=enday)
# df = data.ix[:,0:5]
# df.index.name = 'Date'
# df['Adj Close'] = df.close
# df.columns = ['Open', 'High', 'Close', 'Low', 'Volume', 'Adj Close']
# df = swap(df, 'Low', 2)
# df = df.sort_index()
# df.to_csv('data/dayk/ZS399106.csv')


# data = ts.get_hist_data('sh', ktype='30',start='2012-01-01', end='2016-03-20')
# df = data.ix[:,0:5]
# df.index.name = 'Date'
# df['Adj Close'] = df.close
# df.columns = ['Open', 'High', 'Close', 'Low', 'Volume', 'Adj Close']
# df = df.sort_index()
# df.to_csv('data/30mink/ZS000001.csv')
#
