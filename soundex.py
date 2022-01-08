#!/usr/bin/env python

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


def sum_digits(digits):
    return sum(c << i for i, c in enumerate(digits))

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
limit = 12000
try:
    opts, args = getopt.getopt(argv, "-hl:", ["help", "limit="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-l --limit <int> def=50")
        sys.exit(0)

    if opt in ("-l", "--limit"):
        limit = int(arg)
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()
o.sqlex(f"delete from vals")

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}


f = open("data/0_BTCUSD.json", )
g.dprep = json.load(f)

# columns
# index
# data


_index = []
_data = []

hold = []
lastclose = 0
close = 0
idx=0
for d in g.dprep['data']:
    close = d[4]
    hold.append(close)
    hold = hold[-8:]
    # print(hold)
    if idx > 8:
        for i in range(len(hold)-1,-1,-1):
            g.patsig[i] = 1 if hold[i-1] > hold[i] else 0
        bsig = ''.join(map(str,g.patsig)).zfill(8)
        # print(g.patsig)
        val = int(bsig, base=2)
        print(idx,val,bsig)
        o.sqlex(f"insert into vals (val, bin) values ({val},'{bsig}')")
        # print("")
    # if idx > 8:
    #     pidx = idx - 8
    #
    #     if close > lastclose:
    #         flag = 1
    #     else:
    #         flag = 0
    #
    #     g.patsig[pidx]=flag
    #
    #     print(pidx,idx,lastclose,close, flag, g.patsig)




    # _index.append(nidx)
    # _data.append(d)



    idx += 1

    lastclose = close
# print(g.dprep['index'])

# g.tmp1['columns'] = g.dprep['columns']
# g.tmp1['index'] = _index
# g.tmp1['data'] = _data

# with open('data/5_SOUNDEX_BTCUSDT.json', 'w') as outfile:
#     json.dump(g.tmp1, outfile)
