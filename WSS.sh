#!/bin/bash


process="./b_wss.py"
makerun="/home/jw/store/src/jmcap/v2bot/start_wss.sh"

if ps ax | grep -v grep | grep $process > /dev/null
then
    exit
else
    $makerun &
fi

exit
