# get indicators
import mysql.connector
from db.dbexport import dbexport
import collections
import bisect
from utils.utils import TimeUtils
from stats.pe import PE
from stats.dt import DT 
from stats.yd import YD 

timeutils = TimeUtils()
db = dbexport()

# match = set()
# match.add('SZ300315')
# pe = PE(db,timeutils,'data/finance.csv',match)
# pe.compute()

match = set()
match.add('SZ300315')

yd = YD(db,timeutils,'data/yidong.txt',match)
yddf = yd.compute()
yddf.to_csv('data/yd.csv.out', sep=',', encoding='utf-8',index=False)

exit()
dt = DT(db,timeutils,'data/dtboard.csv',match)
dtdf = dt.compute()

dtdf.to_csv('data/dtboard.csv.out', sep=',', encoding='utf-8',index=False)

# df.to_csv(self.__file + '.out', sep=',', encoding='utf-8',index=False)
#
