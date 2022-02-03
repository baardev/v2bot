#!/usr/bin/python -W ignore
import time

%matplotlib notebook

import matplotlib

matplotlib.use("Qt5agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import lib_v2_listener as kb

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
import traceback
import lib_panzoom as c


def strint(v):
    if type(v) == int:
        return f"{v}"
    if type(v) == float:
        return f"{v}"
    return f"'{v}'"

def sum_digits(digits):
    return sum(c << i for i, c in enumerate(digits))

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

src = "data/BTCUSDT_1m_0f.json"
pair = "BTC/USDT"
bits = 6
chart = "1m"

# print(f"CHECKING: [{src}]")
# os.system(f"./check_data.py -s {src}")

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()

g.BASE = pair.split("/")[0]
g.QUOTE = pair.split("/")[1]

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}

version = 4
autoyes = False
ncount = 100

dst = f'data/perf{version}_{bits}_{g.BASE}{g.QUOTE}_{chart}_{filter}f.json'

print(f"bits = {bits}, src = {src}, dst = {dst}")

if autoyes:
    o.waitfor("Enter to run")



f = open(src, )
g.dprep = json.load(f)


# try:
#     data = g.dprep['data'] # * load a OHLC data file format
# except:
#     data = g.dprep # * load the streaming data

if not ncount:
    data = g.dprep['data'] # * load a OHLC data file formats
else:
    data = g.dprep['data'][-(ncount):] # * load a OHLC data file formats

o.sqlex(f"delete from vals{version}")
o.sqlex(f"ALTER TABLE vals{version} AUTO_INCREMENT = 1")
g.cursor.execute("SET AUTOCOMMIT = 1")

idx = 0

fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 8), dpi=80)

outfile = open(f"/tmp/_tmppb{version}.csv","w")

_index = []
_data = []

hold = []
bin_ary = {}
idx = 0
autoyes = True
g.patsig = [0] * bits

plt.ion()

ax1.plot(hold, label='Binance', color='g')

while True:
    for d in data:
        # print(d,  datetime.fromtimestamp(int(d[0])/1000))
        if len(d) > 1:
            usecolor = "olive"
            try:
                close = d[4]
                hold.append(close)
                hold = hold[-(bits+1):]                                     # * get last <n> closing vales
                if idx > bits+1:                                            # * are there enough vits to sample?
                    for i in range(bits):                                   # * loop through last <n> values
                        g.patsig[i] = 1 if hold[i+1] > hold[i] else 0       # * assign 1s and 0s

                    delta = hold[len(hold)-1] - hold[len(hold)-2]           # * get delta of last value
                    bsig = ''.join(map(str,g.patsig)).zfill(bits)           # * make a binary number from the values
                    val = int(bsig, base=2)                                 # * convert it to an int
                    bin_str = f"bin_{str(bsig[:-1])}"                              # * gate the <n-1> bits as a string to preserve leading 0s

                    fclose = hold[0]
                    lclose = hold[-1]
                    els = {
                        'bin_str':bin_str,
                        'delta':delta,
                        'fclose':fclose,
                        'lclose':lclose,
                        'count': 1
                    }

                    bin_ary[bsig]=els                                      # * add to array as a key


                    fig.canvas.draw()
                    fig.flush_events()
                    time.sleep((0.1)
                    print(hold)
                    # print(f'0,{val},"{bsig}", {delta}, {fclose}, {lclose}\n')           # * save dec value, bin value. and delta value to CSV file
                idx += 1
            except Exception as e:
                pass
plt.show()
