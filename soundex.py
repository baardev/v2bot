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
bits = 6
src = "data/2_BTCUSDT.json"
chart = "5m"
pair = "BTC/USDT"
try:
    opts, args = getopt.getopt(argv, "-hb:s:c:p:", ["help", "bits=","--src=","chart=","pair="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print(f"-b --bits <int> def={bits}")
        print(f"-c --chart <time> def='{chart}', '0m' for wss")
        print(f"-p --pair <base/quote> def='{pair}'")
        print(f"-s --src <srcfile> def='{src}'")
        sys.exit(0)

    if opt in ("-b", "--bits"):
        bits = int(arg)

    if opt in ("-s", "--src"):
        src = arg

    if opt in ("-c", "--chart"):
        chart = arg

    if opt in ("-p", "--pair"):
        pair = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()

g.BASE = pair.split("/")[0]
g.QUOTE = pair.split("/")[1]

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}

dst = f'data/perf_{bits}_{g.BASE}{g.QUOTE}_{chart}.json'

print(f"bits = {bits}, src = {src}, dst = {dst}")
o.waitfor()


f = open(src, )
g.dprep = json.load(f)

_index = []
_data = []

hold = []
bin_ary = {}
bin_ary_ct = {}
lastclose = 0
close = 0
idx=0
ct = 1

g.patsig = [0]*bits

try:
    data = g.dprep['data'] # * load a OHLC data file format
except:
    data = g.dprep # * load the streaming data


o.sqlex(f"delete from vals")
try:
    for d in data:
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
            print(f"{idx}\t{sstr}?")
            bin_ary[bsig]=sstr
            bin_ary_ct[bsig] = 1
            # print("")
            # o.sqlex(f"insert into vals (val, bin, bits, pair, chart, ct) values ({val},'{bsig}',{bits},'{ g.cvars['pair']}','5m',{ct})")
            cmd = f"insert into vals (val, bin) values ({val},'{bsig}')"
            o.sqlex(cmd)

        # _index.append(nidx)
        # _data.append(d)
        idx += 1
        lastclose = close
    # if idx > 1000:
    #     break

# o.sqlex(f"delete from rootperf")
except:
    pass
countdown = 2**(bits-1)
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

        o.sqlex(f"replace into rootperf (root,perf,bits,pair,chart) values ('{val}','{ratio}','{bits}','{pair}','{chart}')")

        print(f"{countdown}: {bin_ary[key]}[0|1]",ratio)
        countdown -= 1
    except:
        pass

saveperf = {}
rs = o.sqlex(f"select root,perf from rootperf where bits = '{bits}' and chart = '{chart}' and pair = '{pair}'", ret="all")
for r in rs:
    saveperf[r[0]] = r[1]
with open(dst, 'w') as outfile:
    json.dump(saveperf, outfile)




# print(json.dumps(saveperf))
# print(len(list(bin_ary.keys())))

# print(g.dprep['index'])

# g.tmp1['columns'] = g.dprep['columns']
# g.tmp1['index'] = _index
# g.tmp1['data'] = _data

# with open('data/5_SOUNDEX_BTCUSDT.json', 'w') as outfile:
#     json.dump(g.tmp1, outfile)
