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

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
limit = 50
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
g.BASE = g.cvars['pair'].split("/")[0]
g.QUOTE = g.cvars['pair'].split("/")[1]

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
lastclose = 0
close = 0
idx=0
nidx=0
cum = 0
for d in g.dprep['data']:
    close = d[4]
    if idx==0:
        lastclose = close
    cum += (close-lastclose)

    if abs(cum) > limit:
        print(nidx,idx,cum)
        _index.append(nidx)
        _data.append(d)
        cum = 0
        nidx += 1
    idx += 1

    lastclose = close
# print(g.dprep['index'])

g.tmp1['columns'] = g.dprep['columns']
g.tmp1['index'] = _index
g.tmp1['data'] = _data

fn = f'data/x_FILTERED_{limit}_{g.BASE}{g.QUOTE}.json'
with open(fn, 'w') as outfile:
    json.dump(g.tmp1, outfile)

print(f"Save to file: {fn}")
