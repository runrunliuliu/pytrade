# -*- coding: utf-8 -*-
import re
import sys
from prettytable import PrettyTable


zuhe = PrettyTable(['开仓日', '平仓日', '收益率', '最大回撤', '最大亏损', \
                    '比值', 'Sharp', '达标周期', '平均持仓时间', '资金利用率', \
                    'SZ000001', 'HS300', '复利', '复利回撤', '复利sharp'])
zuhe.align = 'l'

cnt = 1
for line in sys.stdin:
    arr = []
    line = line.strip()
    if '+' in line:
        continue
    if cnt % 2 == 1:
        cnt = cnt + 1
        continue
    tmp  = line.split('|')
    for i in range(1, len(tmp) - 1):
        t = tmp[i]
        t = re.sub('\s','',t)
        arr.append(t)
    cnt = cnt + 1
    zuhe.add_row(arr)
print zuhe
