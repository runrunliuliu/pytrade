import json
from urlparse import urlparse
import re
import hashlib   
import MySQLdb


class dbimport:

    def __init__(self, db=1, uptime=0):
        if db == 1:
            db_user = 'hy'
            db_pass = '123456'
            db_url  = '192.168.100.101'
            dbname  = 'test'
            self.db = MySQLdb.connect(db_url,db_user,db_pass,dbname,charset='utf8')
            self.path = "data"
        if db == 2:
            db_user = 'hy'
            db_pass = '123456'
            db_url  = '192.168.200.30'
            dbname  = 'stock_misc'
            self.db = MySQLdb.connect(db_url,db_user,db_pass,dbname,charset='utf8')
        self.uptime = uptime

    def loadata(self,path):
        jout = []
        count = 0
        for line in open(path):
            try:
                jout.append(json.loads(line.strip()))    
                count = count + 1
            except:
                print >> sys.stderr,'load data: ',line.strip()
                continue
        return jout

    # Parse Feature List 
    def parseFT(self, path):
        def getflag(flag):
            out = dict()
            arr = flag.split(',')
            for kv in arr:
                (k, v) = kv.split(':')
                out[k] = v
            return out

        fname = dict()
        for line in open('output/fts/ZS000001.ft.score.csv'):
            arr = line.strip().split(',')
            fname[arr[0]] = (arr[1], arr[2])

        ftval = dict()
        for line in open('output/fts/ZS000001.test.csv.debug'):
            arr = line.strip().split(' ')
            ftval[arr[0]] = arr[1:]

        inday = dict()
        for line in open('output/fts/ZS000001.test.csv.index'):
            (ind, day) = line.strip().split(',')
            inday[day] = ind 

        jout  = []
        flags = dict()
        for line in open(path):
            out = {}
            (day, flag) = line.strip().split(' ')
            
            out['day'] = day
            fdict = getflag(flag)    
            if day in inday:
                ind = inday[day]
                if ind not in ftval:
                    continue
                for kv in ftval[ind]:
                    (k, v) = kv.split(':')
                    k = 'f' + k
                    if k in fdict and v != '1024201':
                        out['fid']    = fname[k][0]
                        out['fname']  = fname[k][1]
                        out['val']    = v
                        out['status'] = fdict[k]
                        out['uptime'] = str(self.uptime)
                        jout.append(json.dumps(out))
        return jout

    # Parse Dapan Baodie
    def parseDapan(self,path):
        jout  = []
        for line in open(path):
            out = {}
            arr = line.strip().split(',')
            out['day']     = arr[0]
            out['status']  = arr[1]
            out['predict'] = arr[2]
            out['prob']    = arr[3]
            out['pday']    = arr[5]
            out['uptime']  = str(self.uptime)
            jout.append(json.dumps(out))
        return jout

    def parseDT(self,path):
        texts = self.loadata(path)
        jout  = []
        for t in texts:
            jout.append(json.dumps(t))
        return jout

    def parseGP(self,path):
        texts = self.loadata(path)
        jout  = []
        for t in texts:
            out = {}
            url  = t['link']
            time = re.sub('[\\(\\)]+','',t['time'])
            host = urlparse(url).hostname            
            if host == 'blog.eastmoney.com':
                time = time + ":00"
            out['ctime'] = time
            out['author'] = t['author']
            out['link'] = t['link']
            out['score'] = str(t['score'])
            out['title'] = t['title']
            m2 = hashlib.md5()
            m2.update(t['link'])
            out['md5'] = m2.hexdigest()
            jout.append(json.dumps(out))
        return jout

    def import2db(self,table,action,data):
        cursor = self.db.cursor()
        if action == 'replace':
            for d in data:
                d = json.loads(d)
                sql = ''
                for k in d.keys():
                    sql = sql + "`" +  k + "`='" + d[k] + "',"
                sql = 'REPLACE INTO ' + table + ' SET ' +  sql
                sql = re.sub(',$',';',sql).encode("utf8")
                print sql
                cursor.execute(sql)
                self.db.commit()
# 
