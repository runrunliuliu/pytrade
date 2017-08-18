#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

mkdir -p backtests 
mkdir -p data
mkdir -p output
mkdir -p logs
mkdir -p output/nbs/
mkdir -p output/kline/
mkdir -p output/fts/
mkdir -p output/dapan/

# download data
# bash download.sh
timestamp=`date +%s`
day=`date +"%Y-%m-%d"`
dayH=`date +"%Y-%m-%d-%H"`
HOUR=`date +"%H"`
# day0='2016-08-09'
echo $day, $timestamp

###--- DOWNLOAD DT_BOARD
scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/15mink/* ./data/15mink/
scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/dayk/ZS000001.* ./data/dayk/
scp himalayas@139.129.99.51:/home/himalayas/apps/web_dev/cron/app/stock_minning/output/test2.txt ./output/fts/

if [ $HOUR == "15" ];then
    $py plotdapan.py -p 'day'
    $py plotdapan.py -p '15min'
    $py gbdt.py -m predict -n 1 >output/dapan/$dayH".log"
else
    $py gbdt.py -m predict -n 1 >output/dapan/$dayH".log"
fi

python dbaction.py -t tb_dapan_bd_day_list -a replace -d 3 -i output/fts/ZS000001.test.pred.csv -m $timestamp 
python dbaction.py -t tb_dapan_bd_day_feature_list -a replace -d 3 -i output/fts/ZS000001.ft.flag -m $timestamp

