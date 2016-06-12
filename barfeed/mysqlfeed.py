# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade.barfeed import dbfeed
from pyalgotrade.barfeed import membf
from pyalgotrade import bar
from pyalgotrade import dataseries
from pyalgotrade.utils import dt

from mysql_api import mysql_api
        
def normalize_instrument(instrument):
    return instrument.upper()
    
    
class Database(dbfeed.Database):
    def __init__(self, conf = dict({'host':'192.168.100.101','db':'stock','user':'hy','passwd':'123456'})):
        
        super(Database,self).__init__()
        self.mysql = mysql_api(host = conf['host'],db = conf['db'], user = conf['user'], passwd = conf['passwd'])
        self.__instrumentIds = {}
        
        # form dictionary for looking up stock_id in database for query purpose
        sid = self.mysql.get_latest_stock_list()
        code = self.mysql.get_latest_stock_code()
        for SID,CODE in zip(sid,code):
            self.__instrumentIds[normalize_instrument(CODE)] = SID

    def __getInstrumentID(self,instrument):
        return self.__instrumentIds.get(instrument,None)
        
    def getBars(self,instrument,frequency,timezone=None,fromDateTime=None,toDateTime=None):
        instrument = normalize_instrument(instrument)
        instrumentId = self.__getInstrumentID(instrument)
        
        args = [instrumentId]
        # write column and table name
        if frequency is bar.Frequency.DAY:
            sql = self.__get_day_bar_sql()
        elif frequency is bar.Frequency.MINUTE:
            min_table_id = self.__get_minute_table_id()
            sql = self.__get_minute_bar_sql(min_table_id)    
        
        # write where condition
        if fromDateTime is not None:
            sql +=' and timestamp >= %d'
            args.append(dt.datetime_to_timestamp(fromDateTime))
        if toDateTime is not None:
            sql +=' and timestamp <= %d'
            args.append(dt.datetime_to_timestamp(toDateTime))
            
        # write order
        sql +=' order by timestamp'
            
        # substitute parameters
        sql = sql%tuple(args)
        
        ret = []
        result = self.mysql.fetch(sql)
        for row in result:
            dateTime = dt.timestamp_to_datetime(row[0])
            if timezone:
                dateTime = dt.localize(dateTime,timezone)
            if frequency is bar.Frequency.MINUTE:
                o,c = self.__split(row[1])
                h,l = self.__split(row[2])
                v = row[3]
            else:
                o,h,l,c,v = row[1],row[2],row[3],row[4],row[5]
                ret.append(bar.BasicBar(dateTime,o,h,l,c,v,c,frequency))
        return ret
        
    
    def __get_day_bar_sql(self):
        return 'select timestamp,open,high,low,close,volume from tb_stock_day_fuquan_data where stock_id = %d '
    def __get_minute_table_id(self,instrumentId):
        return 'select minute_table_index from tb_stock_code_map where stock_id = %d'%instrumentId
    def __get_minute_bar_sql(self,min_table_id):
        return 'select timestamp,open_close,high_low,volume from tb_stock_minute_data_'+str(min_table_id)+' where stock_id = %d '
    def __split(self,num1_num2):
        num1 = num1_num2 >> 16
        num2 = num1_num2 & 0xFFFF
        return num1,num2
        
'''       
    def __get_table(self,freq)   
       
    def __get_col_names(self,col_names):
       assert type(col_names) is list
       sql=' '
       for col_name in col_names:
           sql += col_name + ','
       return sql
'''       
       
       
class Feed(membf.BarFeed):
    def __init__(self, frequency, maxLen=dataseries.DEFAULT_MAX_LEN, DBconf = dict({'host':'192.168.100.101','db':'stock','user':'hy','passwd':'123456'})):
        membf.BarFeed.__init__(self, frequency, maxLen)
        self.__db = Database(DBconf)

    def barsHaveAdjClose(self):
        return True

    def getDatabase(self):
        return self.__db

    def loadBars(self, instrument, timezone=None, fromDateTime=None, toDateTime=None):
        bars = self.__db.getBars(instrument, self.getFrequency(), timezone, fromDateTime, toDateTime)
        self.addBarsFromSequence(instrument, bars)
