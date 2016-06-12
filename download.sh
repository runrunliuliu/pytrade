#!/bin/bash

day0=`date +"%Y-%m-%d"`
echo $day0

python dbaction.py -a fetchindex
python download.py $day0

scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/dayk/* ./data/dayk/
scp himalayas@139.129.99.51:/home/himalayas/apps2/qts/pytrade2/data/stockinfo.csv ./data/
