import json
from urlparse import urlparse
import re
import hashlib   
import MySQLdb


class dbimport:

    def __init__(self,dbname):
        db_user = 'hy'
        db_pass = '123456'
        db_url  = '192.168.100.101'
        self.db = MySQLdb.connect(db_url,db_user,db_pass,dbname,charset='utf8')
        self.path = "data"

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
