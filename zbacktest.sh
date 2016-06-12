#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

day0=`date +"%Y-%m-%d"`
echo $day0

sday='2006-05-12'
eday='2007-05-11'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2008-11-14'
eday='2009-08-07'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2014-11-14'
eday='2015-06-12'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2007-11-02'
eday='2008-10-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2011-05-27'
eday='2011-12-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-06-19'
eday='2015-09-30'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2012-11-30'
eday='2014-10-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-02-17'
eday='2015-05-15'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2015-09-02'
eday='2015-12-31'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2016-02-05'
eday='2016-05-06'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2006-05-12'
eday='2016-05-06'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &

sday='2011-05-20'
eday='2012-12-20'
nohup $py pp_selstock.py -m 'mock' -s $sday -d $eday -t triangle 1>logs/$sday'_'$eday'.log' 2>&1 &
