#!/bin/bash
cd /home/jw/src/jmcap/v2bot

pkill v2.py
pkill tbot_listen.py

rm nohup.out > /dev/null 2>&1

nohup ./v2.py > logs/running_v2.log 2>&1 &
nohup ./tbot_listen.py > logs/running_listen.log 2>&1 &
