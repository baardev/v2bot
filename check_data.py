#!/usr/bin/python -W ignore

import websocket
import json
from pprint import pprint
import lib_v2_globals as g
import lib_v2_ohlc as o
import pandas as pd
import toml
import os, sys, getopt
from decimal import *
import datetime
from datetime import timedelta, datetime

def strint(v):
    if type(v) == int:
        return f"{v}"
    if type(v) == float:
        return f"{v}"
    return f"'{v}'"

def sum_digits(digits):
    return sum(c << i for i, c in enumerate(digits))

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
bits = 6
src = "data/2_BTCUSDT.json"
chart = "5m"
filter = 0
pair = "BTC/USDT"
ncount = False
version = 2
try:
    opts, args = getopt.getopt(argv, "-hs:", ["help","--src="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print(f"-s --src <srcfile> def='{src}'")
        sys.exit(0)

    if opt in ("-s", "--src"):
        src = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()

f = open(src, )
g.dprep = json.load(f)
data = g.dprep['data'] # * load a OHLC data file formats

for i in range(len(g.dprep['data'])-1):
    try:
        ts = g.dprep['data'][i][0]
        timestamp =  datetime.fromtimestamp(int(ts)/1000)
    except Exception as e:
        print("FOUND ERROR IN DATA ---------------------------------------")
        print(e)
        print("REECORD IN ERROR: -----------------------------------------")
        print(g.dprep['data'][i])
        print("FIXING...")
        g.dprep['data'][i][0] = g.dprep['data'][i][0].strip("\x00")
        g.dprep['data'][i][0] = g.dprep['data'][i][0].strip("\u0000")
        print("UPDATED RECORD: -------------------------------------------")
        print(g.dprep['data'][i])
        print("-----------------------------------------------------------")

with open(src, 'w') as f:
    json.dump(g.dprep, f)
f.close()