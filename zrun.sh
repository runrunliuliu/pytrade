#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

day0=`date +"%Y-%m-%d"`
echo $day0

$py pp_selstock.py -m 'train' -s 2016-05-06 -d $day0 -t triangle
$py pp_selstock.py -m 'stock' -s 2016-05-06 -d $day0 -t triangle

scp data/dayk/* himalayas@192.168.200.11:/data/server/nfsclient/stock/dayk/
