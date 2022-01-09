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

g.BASE = g.cvars['pair'].split("/")[0]
g.QUOTE = g.cvars['pair'].split("/")[1]

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}

f = open("data/0_BTCUSD.json", )
g.dprep = json.load(f)

_index = []
_data = []

hold = []
bin_ary = {}
lastclose = 0
close = 0
idx=0

bits = 16
g.patsig = [0]*bits

o.sqlex(f"delete from vals")
for d in g.dprep['data']:
    close = d[4]
    hold.append(close)
    hold = hold[-(bits):]
    # print(hold)
    if idx > bits:
        for i in range(len(hold)-1,-1,-1): # * from 7 to 0 (inc)
            g.patsig[i] = 1 if hold[i] > hold[i-1] else 0
        bsig = ''.join(map(str,g.patsig)).zfill(bits)

        val = int(bsig, base=2)
        # print(hold)
        # print(g.patsig)
        sstr = str(bsig[:-1])
        sstr = f"{sstr}"
        print(F"{idx}\t{val}\t{bsig}\t{sstr}")
        bin_ary[bsig]=sstr
        # print("")

        o.sqlex(f"insert into vals (val, bin) values ({val},'{bsig}')")

    # _index.append(nidx)
    # _data.append(d)
    idx += 1
    lastclose = close
    if idx > 1000:
        break

o.sqlex(f"delete from rootperf")

for key in bin_ary:
    try:
        val = bin_ary[key]
        rs = o.sqlex(f"select count(val) as c from vals where bin like '{val}0' group by val order by c", ret="one")
        wentdown = rs[0]
        # print(rs)
        rs = o.sqlex(f"select count(val) as c from vals where bin like '{val}1' group by val order by c", ret="one")
        # print(rs)
        wentup = rs[0]
        ratio = o.truncate(wentup/wentdown,2)

        o.sqlex(f"insert into rootperf (root,perf) values ('{val}','{ratio}')")

        print(f"{bin_ary[key]}[0|1]",ratio)
    except:
        pass

saveperf = {}
rs = o.sqlex(f"select root,perf from rootperf", ret="all")
for r in rs:
    saveperf[r[0]] = r[1]
with open(f'data/perf_{bits}_{g.BASE}{g.QUOTE}.json', 'w') as outfile:
    json.dump(saveperf, outfile)




# print(json.dumps(saveperf))
# print(len(list(bin_ary.keys())))

# print(g.dprep['index'])

# g.tmp1['columns'] = g.dprep['columns']
# g.tmp1['index'] = _index
# g.tmp1['data'] = _data

# with open('data/5_SOUNDEX_BTCUSDT.json', 'w') as outfile:
#     json.dump(g.tmp1, outfile)
