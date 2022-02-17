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
import traceback
from pprint import pprint
import numpy

def running_mean(x, N):
    """ x == an array of data. N == number of samples per average """
    try:
        cumsum = numpy.cumsum(numpy.insert(x, 0, 0))
        return (cumsum[N:] - cumsum[:-N]) / float(N)
    except Exception as e:
        print(repr(e))
        pass









def strint(v):
    if type(v) == int:
        return f"{v}"
    if type(v) == float:
        return f"{v}"
    return f"'{v}'"

def sum_digits(digits):
    return sum(c << i for i, c in enumerate(digits))

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
bits = 6
src = "data/2_BTCUSDT.json"
chart = "1m"
filter = 0
pair = g.cvars['pair']
ncount = False
version = 5
autoyes = False
try:
    opts, args = getopt.getopt(argv, "-hb:s:c:p:n:f:yP:", ["help", "bits=","--src=","chart=","pair=","ncount=","filter=","autoyes"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print(f"-c --chart <time> def='{chart}', '0m' for wss")
        print(f"-b --bits <int> def={bits}")
        print(f"-p --pair <base/quote> def='{pair}'")
        print(f"-s --src <srcfile> def='{src}'")
        print(f"-n --ncount <int>")

        print(f"-f --filter <filter val> def=0")
        print(f"-y autoyes")
        sys.exit(0)

    if opt in ("-b", "--bits"):
        bits = int(arg)

    if opt in ("-s", "--src"):
        src = arg

    if opt in ("-c", "--chart"):
        chart = arg

    if opt in ("-p", "--pair"):
        pair = arg

    if opt in ("-n", "--ncount"):
        ncount = int(arg)

    if opt in ("-f", "--filter"):
        filter = int(arg)

    if opt in ("-y", "--autoyes"):
        autoyes = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

# os.system(f"./check_data.py -s {src}")

g.dbc, g.cursor = o.getdbconn(dictionary = True)

g.BASE = pair.split("/")[0]
g.QUOTE = pair.split("/")[1]

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}

dst = f'data/perf{version}_{bits}_{g.BASE}{g.QUOTE}_{chart}_{filter}f.json'

print(f"bits = {bits}, src = {src}, dst = {dst}")

if autoyes:
    o.waitfor("Enter to run")


f = open(src, )
g.dprep = json.load(f)

_index = []
_data = []

hold = []
bin_ary = {}
# delta_ary = {}
bin_ary_ct = {}
bin_delta_ct = {}
lastclose = 0
close = 0
idx=0
ct = 1
MA = 3
g.patsig = [0]*bits

# try:
#     data = g.dprep['data'] # * load a OHLC data file format
# except:
#     data = g.dprep # * load the streaming data

if not ncount:
    data = g.dprep['data'] # * load a OHLC data file formats
else:
    data = g.dprep['data'][-(ncount):] # * load a OHLC data file formats


# * 'data' now holds all the OHLV entries from the data file
'''
    [
        1643155200000,
        36958.32,
        37000.0,
        36947.97,
        36958.33,
        31.43343,
        "BTC/USDT",
        "binance"
    ]
'''

# print(json.dumps(data, indent=4))

# exit()
# * now get entries from the stream table

if False:
    cmd = "SELECT * from stream where closed = true"
    rs = o.sqlex(cmd,dictionary=True)

    '''
    {'base_asset_vol': 33.8822403,
     'chart_interval': '1m',
     'close': 44550.2109375,
     'close_time': 1644447179999,
     'closed': 1,
     'dtime': datetime.datetime(2022, 2, 9, 19, 53),
     'first_trade_id': 1252437373,
     'high': 44572.91015625,
     'id': 377537,
     'ignored': 0.0,
     'last_trade_id': 1252438008,
     'low': 44572.91015625,
     'open': 44524.2890625,
     'quote_asset_vol': 1509303.75,
     'start_time': 1644447120000,
     'symbol': 'BTCUSDT',
     'taker_buy_base_asset_vol': 31.25189018,
     'taker_buy_quote_asset_vol': 1392179.125,
     'trades': 636,
     'tstamp': 1644447180002}
    '''

    # * add new data to old data
    for r in rs:
        data.append([
        r['tstamp'],
        o.toPrec('price',r['open']),
        o.toPrec('price',r['high']),
        o.toPrec('price',r['low']),
        o.toPrec('price',r['close']),
        r['quote_asset_vol'],
        f"{g.BASE}/{g.QUOTE}",
        "binance",
        ])


    '''
        [
            1643155200000,
            36958.32,
            37000.0,
            36947.97,
            36958.33,
            31.43343,
            "BTC/USDT",
            "binance"
        ]
    '''

o.sqlex(f"delete from vals{version}")
o.sqlex(f"ALTER TABLE vals{version} AUTO_INCREMENT = 1")
g.cursor.execute("SET AUTOCOMMIT = 1")


with open(f"/tmp/_tmppb{version}.csv","w") as outfile:
    for d in data:
        if len(d) > 1:
            timestamp =  datetime.fromtimestamp(int(d[0])/1000)
            # exit()
            close = d[4]
            hold.append(close)
            hold = hold[-(bits+1):]
            if idx > bits+1:                                            # * are there enough vits to sample?
                for i in range(bits):                                   # * loop through last <n> values
                    g.patsig[i] = hold[i]       # * assign 1s and 0s
                print("BEF:", g.patsig)

                fclose = hold[0]
                lclose = hold[-1]
                cdelta = lclose - fclose
                g.patsig = o.normalize_list(g.patsig)
                print("NOR:", g.patsig)

                # val = [-30.45, -2.65, 56.61, 47.13, 47.95, 30.45, 2.65, -28.31, -47.13, -95.89]
                # * MA mean
                pmean = g.patsig
                # pmean = running_mean(g.patsig, 3)
                print("MAM:", pmean)

                # * mirmalize
                xx = [round(float(i)*10) for i in pmean]
                s1 = sum(xx[:-int(bits/2)])
                if xx[0]>100000:
                    print(f"s1:{s1}\nxx:{xx}\npmean:{pmean}\ng.patsig:{g.patsig}\n")
                s2 = sum(xx[int(bits/2):])
                str = f"0,{s1},{s2},{s2-s1},{int(cdelta)}\n"
                ostr = f"0,{s1:<6},{s2:<6},{s2-s1:<6},{int(cdelta):<10} {xx}\n"
                print(ostr)
                if xx[0]<100000:
                    outfile.write(str)
                print("------------------")
            idx += 1


cmd=f"""
LOAD DATA LOCAL INFILE '/tmp/_tmppb{version}.csv' 
INTO TABLE vals{version} 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 0 ROWS;
"""
o.sqlex(cmd)

exit()
# * creates the vals<n> table - every instance of every pattern
"""
+----+------+------+------+------+
| id | s1   | s2   | sd   | cd   |
+----+------+------+------+------+
|  1 |    2 |  -15 |  -17 | -111 |
|  2 |   -2 |   -9 |   -7 |  -58 |
|  3 |   -1 |   -4 |   -3 |  -67 |
|  4 |   -8 |    3 |   11 |   61 |
|  5 |   -8 |   10 |   18 |   27 |
|  6 |   -1 |    7 |    8 |  -22 |
|  7 |    0 |    2 |    2 |   43 |
|  8 |   -1 |    7 |    8 |   15 |
|  9 |    9 |    0 |   -9 |   26 |
| 10 |   -2 |    0 |    2 |   74 |
+----+------+------+------+------+

"""

print("")
countdown = len(bin_ary)
cmd = f"delete from rootperf{version} where chart = '{chart}' and pair = '{pair}' and bits = '{bits}'"
o.sqlex(cmd)

ary = {}

cmd = f"""
SELECT 
     s1,s2,sd,cd
FROM vals{version}  
WHERE bin_val like '%0' 
GROUP BY dec_val 
ORDER BY dec_val
"""
rs = o.sqlex(cmd,ret="all")

# print(json.dumps(rs, indent=4))
# exit()

for r in rs:
    ary[r['bin_val']] = {
        'count':r['cnt'],
        'vffd':r['vffd'],
        'pffd':r['pffd']
    }

cmd = f"""
SELECT 
    bin_val, 
    dec_val, 
    count(dec_val) as cnt, 
    avg(vffd) as vffd, 
    avg(pffd) as pffd 
FROM vals{version}  
WHERE bin_val like '%1' 
GROUP BY dec_val 
ORDER BY dec_val
"""
# print(cmd)
rs = o.sqlex(cmd,ret="all")
for r in rs:
    ary[r['bin_val']] = {
        'count':r['cnt'],
        'vffd':r['vffd'],
        'pffd':r['pffd']
    }

# print(json.dumps(bin_ary, indent=4))
# print(json.dumps(ary, indent=4))
# exit()

# * now we have an array 'ary' that looks like:
"""
{
    "111110": {
        "count": 1,
        "vffd": 53.77999877929688,
        "pffd": 0.14578756690025
    }

    ...
"""

keyList=sorted(bin_ary.keys())

for i,key in enumerate(keyList):
    nexti = i + 1
    k = keyList[i]
    if i < len(keyList)-1:
        nk = keyList[nexti]
        try:
            # * get data for all down-count entries
            down_count_tot = ary[k]['count']
            down_pffd = ary[k]['pffd']
            down_vffd = ary[k]['vffd']

            # * get data for all up-count entries
            up_count_tot = ary[nk]['count']
            up_pffd = ary[nk]['pffd']
            up_vffd = ary[nk]['vffd']

            if up_count_tot > down_count_tot:
                ratio = o.truncate((up_count_tot/down_count_tot)-1,2)
            else:
                ratio = o.truncate((down_count_tot/up_count_tot)-1,2)*-1

            # print(f'>>>>>>>   {delta} = {up_countd} + {down_countd}')
            sum_pffd = up_pffd + down_pffd
            sum_vffd = up_vffd + down_vffd
            # dratio = ratio

            cmd = f"""
                REPLACE INTO rootperf{version} (
                    root,
                    hex,
                    dex,
                    perf,
                    ups,
                    dns,
                    bits,
                    pair,
                    chart, 
                    vffd, 
                    pffd
                ) 
                VALUES (
                    '{key}',
                    '{'%X' % int(key, 2)}',
                    {int(key, 2)},
                    {ratio},
                    {up_count_tot},
                    {down_count_tot},
                    {bits},
                    '{pair}',
                    '{chart}', 
                    {sum_vffd}, 
                    {sum_pffd}
                )
            """
            # print("++++",cmd)
            o.sqlex(cmd)

            # print(f"[{countdown}]\t{hex}\t{bin_ary[key]}?\t{ratio}\t({up_count}/{down_count})")
            if countdown % 1000 == 0:
                print(f"Updating database: [{countdown}]",end="\r")
            countdown -= 1
        except Exception as e:
            print(f"exception at {countdown}")
            print(json.dumps(bin_ary,indent=4))
            traceback.print_exc()
            exit()

 #4.80s user {version}.{version}5s system 7% cpu 1:46.85

o.sqlex(f"commit")#!/usr/bin/python -W ignore

# * final rootfer4 looks like:
"""
+--------+----------+------+-------+------+------+------+----------+-------+-------+-----------------+---------------+
| root   | hex      | dex  | perf  | ups  | dns  | bits | pair     | chart | delta | vffd            | pffd          |
+--------+----------+------+-------+------+------+------+----------+-------+-------+-----------------+---------------+
| 000000 | 00000000 |    0 |  0.10 |   21 |   19 |    6 | BTC/USDT | 1m    |  NULL | -346.3673706055 | -0.9385835528 |
| 000001 | 00000001 |    1 |  0.04 |   22 |   21 |    6 | BTC/USDT | 1m    |  NULL | -231.0209503174 | -0.6279247403 |
| 000010 | 00000002 |    2 | -0.04 |   21 |   22 |    6 | BTC/USDT | 1m    |  NULL | -254.3363647461 | -0.6929709315 |
| 000011 | 00000003 |    3 | -0.61 |   13 |   21 |    6 | BTC/USDT | 1m    |  NULL | -125.8342819214 | -0.3414843380 |
| 000100 | 00000004 |    4 |  0.46 |   19 |   13 |    6 | BTC/USDT | 1m    |  NULL | -276.8584594727 | -0.7536992431 |
| 000101 | 00000005 |    5 | -0.26 |   15 |   19 |    6 | BTC/USDT | 1m    |  NULL |  -85.9800033569 | -0.2346013188 |
| 000110 | 00000006 |    6 |  0.19 |   18 |   15 |    6 | BTC/USDT | 1m    |  NULL | -180.3773345947 | -0.4882960320 |
| 000111 | 00000007 |    7 | -0.38 |   13 |   18 |    6 | BTC/USDT | 1m    |  NULL |    0.4822219610 |  0.0028027210 |
| 001000 | 00000008 |    8 | -0.18 |   11 |   13 |    6 | BTC/USDT | 1m    |  NULL | -237.6353912354 | -0.6475957632 |
| 001001 | 00000009 |    9 |  0.63 |   18 |   11 |    6 | BTC/USDT | 1m    |  NULL |  -43.4872703552 | -0.1178812906 |
+--------+----------+------+-------+------+------+------+----------+-------+-------+-----------------+---------------+
"""


# * now make loadable JSON object
# fary = [
#     [0,'root'],
#     [1,'hex'],
#     [2,'dec'],
#     [3,'perf'],
#     [4,'ups'],
#     [5,'dns'],
#     [6,'bits'],
#     [7,'pair'],
#     [8,'chart'],
#     [9,'delta']
#     [10,'vffd']
#     [11,'pffd']
# ]


saveperf = {}
cmd = f"select * from rootperf{version} where bits = '{bits}' and chart = '{chart}' and pair = '{pair}'"
# print(cmd)

saveperf = o.sqlex(cmd, ret="all")
# for r in rs:
#     saveperf[r[0]] = {"perf":r[1], 'delta':r[2]}

with open(dst, 'w') as outfile:
    json.dump(saveperf, outfile)

print(f"Output file: {dst}")

if autoyes:
    o.waitfor("See Results?")
print("")
print(f"RESULTS from {len(data)} samples \n---------------------------------------")

sary = []
vary = []

cmd = f"""
SELECT * 
FROM rootperf{version} 
WHERE bits = '{bits}' AND pair = '{pair}' AND chart = '{chart}' 
ORDER BY pffd
"""
# print(cmd)
rs = o.sqlex(cmd, ret="all")




# * make table output

df = pd.DataFrame(rs)
print(df)
dfcsv = df.to_csv()
csvfile = f'_tmp_{bits}_{g.BASE}{g.QUOTE}_{chart}.csv'
with open(csvfile, 'w') as outfile:
    outfile.write(dfcsv)
print(f"CSV file saved as: {csvfile}")

