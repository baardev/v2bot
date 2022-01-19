#!/bin/bash -x 
ps -ef |grep tbot_listen.py|awk '{print "kill "$2}' | sh -  
nohup ./tbot_listen.py &
