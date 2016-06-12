#!/bin/bash

cd /Users/liu/apps/pyalgotrade/ 
cat files.txt | xargs rm -rf
python setup.py install --record files.txt
