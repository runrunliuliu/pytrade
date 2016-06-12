#!/bin/bash
source ~/.bashrc
py=`which python`
echo $py

PROG=`basename $0`
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # GNU enhanced getopt is available
    ARGS=`getopt --name "$PROG" --long help,mode:,verbose --options hm:v -- "$@"`
else
    # Original getopt is available (no long option names, no whitespace, no sorting)
    ARGS=`getopt hm:v "$@"`
fi
if [ $? -ne 0 ]; then
    echo "$PROG: usage error (use -h for help)" >&2
    exit 2
fi
eval set -- $ARGS
while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help)     HELP=yes;;
        -m | --mode)     MODE="$2"; shift;;
        -v | --verbose)  VERBOSE=yes;;
        --)              shift; break;; # end of options
    esac
    shift
done
if [ $# -gt 0 ]; then
    # Remaining parameters can be processed
    for ARG in "$@"; do
        echo "$PROG: argument: $ARG"
    done
fi

echo "$PROG: verbose: $VERBOSE"
echo "$PROG: mode: $MODE"
echo "$PROG: help: $HELP"

#----------------- Init Date --------------------------#
dir=`pwd`
day0=`date +"%Y%m%d"`
hour0=`date +"%H"`
if date -v 1d > /dev/null 2>&1; then
    day1=`date -v-1d +"%Y%m%d"`
    hour1=`date -v-1H +"%H"`
else
    day1=`date -d"-1 day" +"%Y%m%d"`
    hour1=`date -d"-1 hour" +"%H"`
fi
echo $day1
stamp=`date +%s`
echo $day0,$day1,$hour0,$hour1

nowdone=$dir/done
mkdir -p $nowdone

if [[ 'x'$MODE == 'xguping' ]];then
    gupingdone=$dir/../crawler/market_mood/sentiment/output/done
    if [ -e $nowdone/$day0"."$hour0".guping.done" ];then
        echo $nowdone/$day0"."$hour0 guping load to db has been done
    else
        if [ -e $gupingdone/$day0"."$hour1".guping.done" ];then
            echo $gupingdone/$day0"."$hour1 guping load to db is start 
            $py dbaction.py -i ../crawler/market_mood/sentiment/output/tmp/$day0.out  -d opinion -t guping -a replace
            touch $nowdone/$day0"."$hour0".guping.done" 
            echo $gupingdone/$day0"."$hour1 guping load to db is done 
        else
            echo $gupingdone/$day0"."$hour1 guping is not generated 
        fi
    fi
fi

if [[ 'x'$MODE == 'xgubaeast' ]];then
    predone=$dir/../textmine/output/done
    don=$dir/output/done
    mkdir -p $don
    if [ -e $don/$MODE".$day0.done" ];then
        echo $don/$MODE".$day0.done" load to db has been done
    else
        if [ -e $don/$MODE".$day0.process" ];then
            echo $MODE is process.........
            exit 0
        fi
        if [ -e $don/$MODE".$day0.done" ];then
            echo $MODE is done.........
            exit 0
        fi
        touch $don/$MODE".$day0.process"
        if [ -e $predone/"gubastats.$day0.done" ];then
            echo $predone/gubastats $day0 load to db is start 
            $py dbaction.py -t gubaeast -a replace -d opinion -i ../textmine/output/gubastats
            touch $don/$MODE".$day0.done" 
            echo  $don/$MODE".$day0.done" is done 
            rm -f $don/$MODE".$day0.process"
        else
            echo  $predone/gubastats.$day0.done is not generated 
            rm -f $don/$MODE".$day0.process"
        fi
    fi
fi

if [[ 'x'$MODE == 'xdt' ]];then
    predone=$dir/../textmine/output/done
    don=$dir/output/done
    mkdir -p $don
    if [ -e $don/$MODE"_$day0.done" ];then
        echo $don/$MODE"_$day0.done" load to db has been done
    else
        if [ -e $don/$MODE"_$day0.process" ];then
            echo $MODE is process.........
            exit 0
        fi
        if [ -e $don/$MODE"_$day0.done" ];then
            echo $MODE is done.........
            exit 0
        fi
        touch $don/$MODE"_$day0.process"
        if [ -e $predone/"dt_$day0.done" ];then
            echo $predone/dt_$day0 load to db is start 
            $py dbaction.py -t tb_dtboard_raw -a replace -d stock -i ../textmine/output/tmp/$day0"_dtparse.out"
            if(($?==0));then
                touch $don/$MODE"_$day0.done" 
                echo  $don/$MODE"_$day0.done" is done 
            fi
            rm -f $don/$MODE"_$day0.process"
        else
            echo  $predone/dt_$day0.done is not generated 
            rm -f $don/$MODE"_$day0.process"
        fi
    fi
fi
