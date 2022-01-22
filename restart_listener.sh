#!/bin/bash -x 
rm nohup.out
ps -ef |grep tbot_listen.py|awk '{print "kill "$2}' | sh -  
nohup ./tbot_listen.py &
ps -ef |grep tbot_listen
tail nohup.out
