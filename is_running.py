#!/usr/bin/env python
import lib_v2_ohlc as o
import os

if o.checkIfProcessRunning('/home/jw/store/src/jmcap/v2bot/b_wss.py'):
    print('Already running... exiting')
    exit(1)
else:
    exit(0)

