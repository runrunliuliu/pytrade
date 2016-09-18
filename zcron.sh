#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

# download data
bash download.sh

day0=`date +"%Y-%m-%d"`
# day0='2016-08-09'
echo $day0

###--- DOWNLOAD DT_BOARD
rsync -uhavzm --stats --progress himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/dtboard.csv ./data/ 

###--- 计算龙虎榜
$py indicator.py

###--- TRAIN ---
$py pp_selstock.py -m 'train' -s 2016-08-01 -d $day0 -t triangle

nohup $py pp_selstock.py -m 'stock' -s 2016-08-01 -d $day0 -t triangle 1>logs/$day0.triangle.log 2>&1 &
nohup $py pp_selstock.py -m 'stock' -s 2016-08-01 -d $day0 -t QUSHI 1>logs/$day0.qushi.log 2>&1 &
nohup $py pp_selstock.py -m 'stock' -s 2016-08-01 -d $day0 -t nbs 1>logs/$day0.nbs.log 2>&1 &

scp data/dayk/* himalayas@192.168.200.11:/data/server/nfsclient/stock/dayk/ 1>upload.log 2>&1
