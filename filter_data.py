#!/usr/bin/env python

import websocket
import json
from pprint import pprint
import lib_v2_globals as g
import pandas as pd
import toml
import os, sys, getopt
from decimal import *
import datetime
from datetime import timedelta, datetime

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
limit = 50
g.pair = g.cvars['pair']
src = "data/BTCUSDT_5m.json"
chart = "5m"
try:
    opts, args = getopt.getopt(argv, "-hl:p:s:c:", ["help", "limit=", "pair=","src=","chart="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-p, --pair")
        print(f"-s --src <srcfile> def='{src}'")
        print(f"-c --chart <time> def='{chart}', '0m' for wss")
        print("-l --limit <int> def=50")
        sys.exit(0)

    if opt in ("-l", "--limit"):
        limit = int(arg)

    if opt in ("-p", "--pair"):
        g.pair = arg

    if opt in ("-s", "--src"):
        src = arg

    if opt in ("-c", "--chart"):
        chart = arg


# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.BASE = g.pair.split("/")[0]
g.QUOTE = g.pair.split("/")[1]

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}


# f = open(f"data/0_{g.BASE}{g.QUOTE}.json", )
f = open(src, )
g.dprep = json.load(f)

# columns
# index
# data


_index = []
_data = []
lastclose = 0
close = 0
idx=0
nidx=0
cum = 0
for d in g.dprep['data']:
    try:
        close = float(d[4])
        if idx==0:
            lastclose = close
        # print(close,lastclose)
        cum += (close-lastclose)

        if abs(cum) > limit:
            # print(nidx,idx,cum)
            _index.append(nidx)
            _data.append(d)
            cum = 0
            nidx += 1
        idx += 1

        lastclose = close
    except:
        pass
# print(g.dprep['index'])

g.tmp1['columns'] = g.dprep['columns']
g.tmp1['index'] = _index
g.tmp1['data'] = _data

fn = f'data/x_FILTERED_{limit}_{g.BASE}{g.QUOTE}_{chart}.json'
with open(fn, 'w') as outfile:
    json.dump(g.tmp1, outfile)

print(f"Save to file: {fn}")
