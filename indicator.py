# get indicators
from db.dbexport import dbexport
import collections
import bisect
from utils.utils import TimeUtils
from stats.pe import PE
from stats.dt import DT 
from stats.yd import YD 

timeutils = TimeUtils()
db = dbexport()

match = set()

dt = DT(db,timeutils,'data/dtboard.csv',match)
dtdf = dt.compute()

dtdf.to_csv('data/dtboard.csv.out', sep=',', encoding='utf-8',index=False)

#
