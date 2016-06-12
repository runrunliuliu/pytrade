# -*- coding: utf-8 -*-
import mysql.connector
from db.dbexport import dbexport
import collections
import bisect
from utils.utils import TimeUtils

timeutils = TimeUtils()
ex = dbexport()

db_user = 'hy'
db_pass = '123456'
db_url  = '192.168.100.101'

cnx_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="name", \
                                                       pool_size=10, \
                                                       autocommit=True, \
                                                       user=db_user, \
                                                       password=db_pass, \
                                                       host=db_url, \
                                                       database="stock")

dict1 = set()
conn = cnx_pool.get_connection()
cursor = conn.cursor()
q = 'SELECT stock_id,concept FROM `tb_stock_concept` where source = 2'
cursor.execute(q)
for row in cursor.fetchall():
    tmp = row[1].encode("utf8")
    if cmp(tmp,"银行") == 0:
        dict1.add(row[0])
    # dict1.add(row[0])
s = ','.join(str(d) for d in dict1)
q = "SELECT stock_code,stock_id,book_value_per_share,report_day FROM `tb_stock_financedata` where stock_id in (" + s + ") order by finance_day"
cursor.execute(q)
stock_val = dict()
for row in cursor.fetchall():
    code = ex.getStockID(row[1])
    if code not in stock_val:
        odict = collections.OrderedDict()
    else:
        odict = stock_val[code]
    odict[row[3]] = row[2]
    stock_val[code] = odict

output = dict()
for k,v in stock_val.iteritems():
    matchday = 0
    cnt      = 0
    for line in open('data/' + k + '.csv'):
        if cnt == 0:
            cnt = cnt + 1
            continue
        arr = line.strip().split(',')
        day  = arr[0]
        tday = int(timeutils.string_toTimestamp(day))
        # if tday < 1420102723:
        #     continue
        close = float(arr[-1])
        ind = bisect.bisect_left(v.keys(),tday)
        time = v.items()[ind - 1][0]
        ind  = float(v.items()[ind - 1][1])
        
        if ind - close > 0.0000001:
            matchday = matchday + 1
            if k not in output:
                trans = []
            else:
                trans = output[k]
            tmp = []
            tmp.append(k)
            tmp.append(tday)
            tmp.append(day)
            tmp.append(close)
            tmp.append(ind)
            tmp.append((ind - close) / ind)
            tmp.append(matchday)
            
            trans.append(','.join(str(t) for t in tmp))
            output[k] = trans
        else:
            matchday = 0
        cnt = cnt + 1
for k,v in output.iteritems():
    maxtf = 0
    tfdsc = ''
    maxds = 0
    dsdsc = ''
    for val in v:
        tmp = val.split(',')
        tf  = float(tmp[-2])
        mds = int(tmp[-1])
        if tf > maxtf:
            maxtf = tf
            tfdsc = val
        if mds > maxds:
            maxds = mds
            dsdsc = val
    print k,maxtf,tfdsc,v[-1]
    print k,maxds,dsdsc,v[-1]
#
