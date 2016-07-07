#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

day0=`date +"%Y-%m-%d"`
echo $day0

###--- DOWNLOAD DT_BOARD
scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/dtboard.csv ./data/ 

###--- 计算龙虎榜
$py indicator.py

###--- TRAIN ---
$py pp_selstock.py -m 'train' -s 2016-05-06 -d $day0 -t triangle
$py pp_selstock.py -m 'stock' -s 2016-05-06 -d $day0 -t triangle
$py pp_selstock.py -m 'stock' -s 2016-05-06 -d $day0 -t QUSHI

scp data/dayk/* himalayas@192.168.200.11:/data/server/nfsclient/stock/dayk/ 1>upload.log 2>&1
