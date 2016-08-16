import MySQLdb


class dbexport:

    def __init__(self):

        db_user = 'hy'
        db_pass = '123456'
        db_url  = '192.168.200.30'
        dbname = 'stock'

        # db_user = 'stock'
        # db_pass = '4r10nc8z2jg42al10'
        # db_url  = 'rdsnfvbb2j2m7bz.mysql.rds.aliyuncs.com'
        # dbname  = 'stock'

        self.conn = MySQLdb.connect(db_url,db_user,db_pass,dbname,charset='utf8')

        self.__dict = dict()
        self.__id_stock = dict()
        q = 'select stock_id,stock_code from tb_stock_code_map'
        cursor = self.conn.cursor()
        cursor.execute(q)
        for row in cursor.fetchall():
            self.__dict[row[1]] = row[0]
            self.__id_stock[row[0]] = row[1]

        self.__id_index = dict()
        q = 'select index_id,index_code from tb_index_code_map'
        sindex = {'000300', '000016', '399006', '399001', '399106'}
        cursor = self.conn.cursor()
        cursor.execute(q)
        for row in cursor.fetchall():
            if row[1] in sindex:
                self.__id_index[row[0]] = row[1]

        self.path = "data"

    def getStockID(self,ids):
        return self.__id_stock[ids]

    def fetchStockID(self):
        for k,v in self.__dict.iteritems():
            print k + '\t' + str(v)

    def fetchfinance(self):
        cursor = self.conn.cursor()
        f = open(self.path + '/finance.csv', 'w')
        query = 'SELECT stock_code,stock_id,earning_per_Share,finance_day FROM `tb_stock_financedata`'
        cursor.execute(query)
        f.write('code,id,eps,day')
        f.write('\n')
        for row in cursor.fetchall():
            out = []
            for i in range(0,len(row)):
                out.append(row[i])
            f.write(','.join(str(o) for o in out))
            f.write('\n')
        f.close()

    def fetchdtboard(self):
        cursor = self.conn.cursor()
        f = open(self.path + '/dtboard.csv', 'w')
        query = 'select group_concat(day,",", head,",", code,",", name,",", prate,",", crate,",", price,",", vol,",", b10,",", b11,",", b12,",", b20,",", b21,",", b22,",", b30,",", b31,",", b32,",", b40,",", b41,",", b42,",", b50,",", b51,",", b52,",", s10,",", s11,",", s12,",", s20,",", s21,",", s22,",", s30,",", s31,",", s32,",", s40,",", s41,",", s42,",", s50,",", s51,",",s52) FROM `tb_dtboard_raw` where day > "2009-12-31" group by day,head,code'
        cursor.execute(query)
        f.write('Date,head,code,name,prate,crate,price,vol,b10,b11,b12,b20,b21,b22,b30,b31,b32,b40,b41,b42,b50,b51,b52,s10,s11,s12,s20,s21,s22,s30,s31,s32,s40,s41,s42,s50,s51,s52')
        f.write('\n')
        for row in cursor.fetchall():
            f.write(row[0].encode('utf8'))
            f.write('\n')
        f.close()

    def fetchyidong(self):
        cursor = self.conn.cursor()
        query  = ''
        cursor.execute(query)
        for row in cursor.fetchall():
            print row[0]

    def fetchIndex(self):
        # get all index day-k data
        for k,v in self.__id_index.iteritems():
            query = 'select from_unixtime(timestamp, \'%Y-%m-%d\'),open,high,low,close,volume from tb_stock_index_day_data where timestamp > 978353440 and index_id = ' + str(k)
            cursor  = self.conn.cursor()
            cursor.execute(query)
            if cursor.rowcount == 0:
                continue
            f = open(self.path + '/dayk/ZS%s.csv' % v, 'w')
            f.write('Date,Open,High,Low,Close,Volume,Adj Close')
            f.write('\n')
            for row in cursor.fetchall():
                out = []
                out.append(row[0])
                for i in range(1,5):
                    out.append(row[i] / 100.0)
                out.append(row[5])
                out.append(row[4] / 100.0)
                f.write(','.join(str(o) for o in out))
                f.write('\n')
            f.close()

    def fetchAll(self):
        # get all day-k data
        for k,v in self.__dict.iteritems():
            # query = 'select from_unixtime(timestamp, \'%Y-%m-%d\'),open,high,low,close,volume from tb_stock_day_fuquan_data where timestamp > 1262325337 and stock_id = ' + str(v)
            query = 'select from_unixtime(timestamp, \'%Y-%m-%d\'),open,high,low,close,volume from tb_stock_day_fuquan_data where timestamp > 978353440 and stock_id = ' + str(v)
            cursor  = self.conn.cursor()
            cursor.execute(query)
            if cursor.rowcount == 0:
                continue
            f = open(self.path + '/dayk/%s.csv' % k, 'w')
            f.write('Date,Open,High,Low,Close,Volume,Adj Close')
            f.write('\n')
            for row in cursor.fetchall():
                out = []
                out.append(row[0])
                for i in range(1,5):
                    out.append(row[i] / 100.0)
                out.append(row[5])
                out.append(row[4] / 100.0)
                f.write(','.join(str(o) for o in out))
                f.write('\n')

            f.close()

        # get dtboard data
        # self.fetchdtboard()

    def fetchStockInfo(self):
        cursor  = self.conn.cursor()
        query = 'SELECT stock_id, sw_level3 FROM `tb_stock_industry`'
        cursor.execute(query)
        for row in cursor.fetchall():
            print str(row[0])[1:], row[1]

    # change timestamp to yyyy-mm-dd
    def fetchStock(self,iid):

        sid = self.__dict[iid]
        f = open(self.path + '/%s.csv' % iid, 'w')
        query = 'select from_unixtime(timestamp, \'%Y-%m-%d\'),open,high,low,close,volume from tb_stock_day_fuquan_data where stock_id = ' + str(sid)
        conn   = self.cnx_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        f.write('Date,Open,High,Low,Close,Volume,Adj Close')
        f.write('\n')
        for row in cursor.fetchall():
            out = []
            out.append(row[0])
            for i in range(1,5):
                out.append(row[i] / 100.0)
            out.append(row[5])
            out.append(row[4] / 100.0)
            f.write(','.join(str(o) for o in out))
            f.write('\n')

        f.close()
