import multiprocessing as mp
from pyalgotrade import strategy
from pyalgotrade import plotterBokeh
from pyalgotrade.tools import yahoofinance
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.feed import csvfeed
from pyalgotrade.stratanalyzer import sharpe
from strategies import dtstrategy 
from utils.utils import TimeUtils
from utils.utils import FileUtils
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import trades
import MySQLdb


def parseinst(codearr):
    out = []
    for c in codearr:
        tmp = c.split('-')
        fname = tmp[-1] 
        code  = fname[2:8]
        out.append((fname,code))
    return out


def getMinK(i):

    (conn,sdict,id_stock) = init()
    i = i + 1

    query  = 'SELECT DISTINCT(stock_id) from tb_stock_minute_data_' + str(i)
    print query
    cursor = conn.cursor()
    cursor.execute(query)
    for row in cursor.fetchall():
        v = row[0]
        k = id_stock[v] 
        query = 'select from_unixtime(timestamp, \'%Y-%m-%d %H:%i:%s\'), ' + \
                'open_close,high_low,volume,amount from tb_stock_minute_data_' + str(i) + \
                ' where timestamp > 1262325337 and stock_id = ' + str(v)

        cursor  = conn.cursor()
        cursor.execute(query)
        if cursor.rowcount == 0:
            continue
        f = open('./data/mink/%s.csv' % k, 'w')
        f.write('Date,Open,High,Low,Close,Volume,Adj Close')
        f.write('\n')
        for row in cursor.fetchall():
            out = []
            out.append(row[0])
            opens = row[1] >> 16
            close = row[1] & 0x0000ffff
            
            high  = row[2] >> 16
            low   = row[2] & 0x0000ffff

            out.append(opens / 100.0)
            out.append(high / 100.0)
            out.append(low / 100.0)
            out.append(close / 100.0)
            out.append(row[3])
            out.append(close / 100.0)
            f.write(','.join(str(o) for o in out))
            f.write('\n')

        f.close()


def dbconnect():
    db_user = 'hy'
    db_pass = '123456'
    db_url  = '192.168.100.101'
    dbname = 'stock'

    conn = MySQLdb.connect(db_url,db_user,db_pass,dbname,charset='utf8')

    return conn


def init():

    conn = dbconnect()
    __dict = dict()
    __id_stock = dict()
    q = 'select stock_id,stock_code from tb_stock_code_map'
    cursor = conn.cursor()
    cursor.execute(q)
    for row in cursor.fetchall():
        __dict[row[1]]     = row[0]
        __id_stock[row[0]] = row[1]

    return(conn,__dict,__id_stock)


def main(plot):

    # Setup a list of processes that we want to run
    processes = [mp.Process(target=getMinK, args=(x,)) for x in range(40)]
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()

if __name__ == "__main__":
    main(False)
# -*- coding: utf-8 -*-
