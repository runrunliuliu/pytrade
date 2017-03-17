#!/bin/bash

day0=`date +"%Y-%m-%d"`
echo $day0

python dbaction.py -a fetchindex
python download.py $day0
sleep 10
python download.py $day0

# scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/dayk/* ./data/dayk/
rsync -uhavzm --stats --progress himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/dayk.tar.gz .
tar -zxvf dayk.tar.gz

# scp multiple period data
mkdir -p data/tmp/
rsync -uhavzm --stats --progress himalayas@192.168.200.20:/home/himalayas/kline/kline.tar.gz data/tmp/
tar -zxvf data/tmp/kline.tar.gz -C data/tmp/
rm -f data/tmp/kline.tar.gz

python pp_utils.py -m trans
cp -r data/output/* data/

# scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/15mink/* ./data/15mink/
# scp himalayas@139.129.99.51:/home/himalayas/apps/web_dev/cron/app/stock_minning/output/test2.txt ./output/fts/
scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/stockinfo.csv ./data/
