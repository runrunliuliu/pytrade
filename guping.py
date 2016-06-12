# -*- coding: utf-8 -*-
import mysql.connector

db_user = 'hy'
db_pass = '123456'
db_url  = '192.168.100.101'

cnx_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="name", \
                                                       pool_size=10, \
                                                       autocommit=True, \
                                                       user=db_user, \
                                                       password=db_pass, \
                                                       host=db_url, \
                                                       database="opinion")

q = "SELECT DATE_FORMAT(ctime,'%Y%m%d'),DATE_FORMAT(ctime,'%h'),score,title,ctime FROM `guping` where title NOT LIKE '%直播%' order by ctime"
conn = cnx_pool.get_connection()
cursor = conn.cursor()
cursor.execute(q)
opinion = dict() 
count = dict()
for row in cursor.fetchall():
    if int(row[1]) < 10 and int(row[1]) > 0:
        k = str(row[0]) + '0'
        if k in opinion:
            v = opinion[k]
            v = v + row[2]
            opinion[k] = v
            count[k] = count[k] + 1
        else:
            opinion[k] = row[2]
            count[k] = 1
for k,v in opinion.iteritems():
    print str(k) + ',' + str(v / count[k])
