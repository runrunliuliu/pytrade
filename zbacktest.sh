#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

day0=`date +"%Y-%m-%d"`
echo $day0

trade='kline'
trade='triangle'

sday='2017-01-03'
eday='2017-08-14'
# eday=$day0
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

exit
sday='2006-01-04'
eday='2016-08-08'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2006-01-04'
eday='2006-12-29'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2007-01-04'
eday='2007-12-28'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2008-01-04'
eday='2008-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2009-01-05'
eday='2009-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2010-01-04'
eday='2010-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2011-01-04'
eday='2011-12-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2012-01-04'
eday='2012-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2013-01-04'
eday='2013-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2014-01-02'
eday='2014-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-01-05'
eday='2015-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2016-01-04'
eday='2016-09-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2010-01-04'
eday='2016-08-08'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2016-08-08'
eday='2016-09-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

exit
sday='2006-05-12'
eday='2007-05-11'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2008-11-14'
eday='2009-08-07'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2014-11-14'
eday='2015-06-12'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2007-11-02'
eday='2008-10-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2011-05-27'
eday='2011-12-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-06-19'
eday='2015-09-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2012-11-30'
eday='2014-10-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-02-17'
eday='2015-05-15'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-09-02'
eday='2015-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2016-02-05'
eday='2016-05-06'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2006-05-12'
eday='2016-05-06'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2011-05-20'
eday='2012-12-20'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t $trade 1>logs/$sday'_'$eday'.log' 2>&1 &
