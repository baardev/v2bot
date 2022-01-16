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
autoyes = False
try:
    opts, args = getopt.getopt(argv, "-hb:s:c:p:n:f:v:y", ["help", "bits=","--src=","chart=","pair=","ncount=","filter=","version=","autoyes"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print(f"-b --bits <int> def={bits}")
        print(f"-c --chart <time> def='{chart}', '0m' for wss")
        print(f"-f --filter <filter val> def=0")
        print(f"-p --pair <base/quote> def='{pair}'")
        print(f"-s --src <srcfile> def='{src}'")
        print(f"-v --version <perfbits version> def={version}'")
        print(f"-n --ncount <int>")
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

    if opt in ("-v", "--version"):
        version= int(arg)

    if opt in ("-y", "--autoyes"):
        autoyes = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

os.system(f"./check_data.py -s {src}")

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()

g.BASE = pair.split("/")[0]
g.QUOTE = pair.split("/")[1]

g.last_close = 0
g.gcounter = 0
g.recover = 0
g.tmp1 = {'columns':[], 'index':[], 'data': []}

dst = f'data/perf_{bits}_{g.BASE}{g.QUOTE}_{chart}_{filter}f.json'

print(f"bits = {bits}, src = {src}, dst = {dst}")

if autoyes:
    o.waitfor("Enter to run")


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

# try:
#     data = g.dprep['data'] # * load a OHLC data file format
# except:
#     data = g.dprep # * load the streaming data

if not ncount:
    data = g.dprep['data'] # * load a OHLC data file formats
else:
    data = g.dprep['data'][-(ncount):] # * load a OHLC data file formats

o.sqlex(f"delete from vals")
o.sqlex(f"ALTER TABLE vals AUTO_INCREMENT = 1")
g.cursor.execute("SET AUTOCOMMIT = 0")

# if version == 1:
#     try:
#         for d in data:
#             close = d[4]
#             hold.append(close)
#             hold = hold[-(bits):]
#             # print(hold)
#             if idx > bits:
#                 for i in range(len(hold)-1,-1,-1): # * from 7 to 0 (inc)
#                     g.patsig[i] = 1 if hold[i] > hold[i-1] else 0
#                 bsig = ''.join(map(str,g.patsig)).zfill(bits)
#
#                 val = int(bsig, base=2)
#                 sstr = str(bsig[:-1])
#                 sstr = f"{sstr}"
#                 print(f"Analyzing patterns in record: [{idx}]\t{sstr}?", end="\r")
#                 bin_ary[bsig]=sstr
#                 bin_ary_ct[bsig] = 1
#                 hexv= '%08X' % int(bsig, 2)
#                 cmd = f"insert into vals (val, bin) values ({val},'{bsig}')"
#                 o.sqlex(cmd)
#             idx += 1
#             lastclose = close
#     except Exception as e:
#         print(e)
#         pass

if version == 2:
    for d in data:
        # print(d)
        try:
            timestamp =  datetime.fromtimestamp(int(d[0])/1000)
            # exit()
            close = d[4]
            hold.append(close)
            hold = hold[-(bits+1):]

            if idx > bits+1:
                for i in range(bits):
                   g.patsig[i] = 1 if hold[i+1] > hold[i] else 0

                bsig = ''.join(map(str,g.patsig)).zfill(bits)
                val = int(bsig, base=2)
                sstr = str(bsig[:-1])
                sstr = f"{sstr}"
                print(f"Analyzing patterns in record: [{idx}]\t{sstr}?", end="\r")
                bin_ary[bsig]=sstr
                bin_ary_ct[bsig] = 1
                hexv= '%08X' % int(bsig, 2)
                cmd = f"insert into vals (val, bin) values ({val},'{bsig}')"
                o.sqlex(cmd)
            idx += 1
            lastclose = close
        except Exception as e:
            print("\n")
            print(e)
            pass


print("")
countdown = len(bin_ary)
cmd = f"delete from rootperf where chart = '{chart}' and pair = '{pair}' and bits = '{bits}'"
o.sqlex(cmd)

for key in bin_ary:
    try:
        val = bin_ary[key]
        hex = '%X' % int(val, 2)
        dex = int(hex, 16)
        dnct = o.sqlex(f"select count(val) as c from vals where bin like '{val}0' group by val order by c", ret="one")[0]
        upct = o.sqlex(f"select count(val) as c from vals where bin like '{val}1' group by val order by c", ret="one")[0]

        # print(upct,dnct)
        if upct > dnct:
            ratio = o.truncate((upct/dnct)-1,2)
        else:
            ratio = o.truncate((dnct/upct)-1,2)*-1

        cmd = f"replace into rootperf (root,hex,dex,perf,ups,dns,bits,pair,chart) values ('{val}','{hex}',{dex},{ratio},{upct},{dnct},{bits},'{pair}','{chart}')"
        o.sqlex(cmd)

        # print(f"[{countdown}]\t{hex}\t{bin_ary[key]}?\t{ratio}\t({upct}/{dnct})")
        print(f"Updating database: [{countdown}]",end="\r")
        countdown -= 1
    except Exception as e:
        # print(e)
        pass

 #4.80s user 3.35s system 7% cpu 1:46.85

o.sqlex(f"commit")
saveperf = {}
cmd = f"select root,perf from rootperf where bits = '{bits}' and chart = '{chart}' and pair = '{pair}'"
rs = o.sqlex(cmd, ret="all")
for r in rs:
    saveperf[r[0]] = r[1]
with open(dst, 'w') as outfile:
    json.dump(saveperf, outfile)
print(f"Output file: {dst}")

if autoyes:
    o.waitfor("See Results?")

print("")
print(f"RESULTS from {len(data)} samples \n---------------------------------------")

sary = []
vary = []
fary = [
    [0,'Pattern'],
    [1,'Hex'],
    [2,'Dex'],
    [3,'perf'],
    [4,'up'],
    [5,'dn'],
    [6,'res'],
    [7,'pair'],
    [8,'ch']
]

cmd = f"select * from rootperf where bits = '{bits}' and pair = '{pair}' and chart = '{chart}' order by perf"
print(cmd)
rs = o.sqlex(cmd, ret="all")

# * make table output
sstr = "Line,"
vstr = ""

for i in range(len(fary)):
    sstr += f"{fary[i][1].strip():>10}"
c=0
for r in rs:
    vstr += f"{c},"
    for i in range(len(fary)):
        vstr += f"{str(r[fary[i][0]]).strip():>10}"
    vstr += "\n"
    c += 1

    # print(sstr)
print(f"{sstr}\n")
print(f"{vstr}\n")

if autoyes:
    o.waitfor("See CSV Results?")
# * make CSV output
sstr = "Line,"
vstr = ""
for i in range(len(fary)):
    sstr += f"{fary[i][1].strip()},"
c=0
for r in rs:
    vstr += f"{c},"
    for i in range(len(fary)):
        vstr += f"{strint(r[fary[i][0]]).strip()},"
    # h = r[fary[1][0]].strip()
    # vstr += f"{int(h,16)}"
    vstr += "\n"
    c += 1
    # print(sstr)
print(f"{sstr}\n")
print(f"{vstr}\n")

csvfile = f'_tmp_{bits}_{g.BASE}{g.QUOTE}_{chart}.csv'
with open(csvfile, 'w') as outfile:
    outfile.write(f"{sstr}\n")
    outfile.write(f"{vstr}\n")
outfile.close()

print(f"CSV file saved as: {csvfile}")
# print(f"{c_root[1]:>10}{c_hex[1]:>5}{c_perf[1]:>5}{c_ups[1]:>6}{c_dns[1]:>10}{c_bits[1]:>6}{c_pair[1]:>10}{c_chart[1]:>4}")
# for r in rs:
#     print(f"{r[c_root[0]]:>10}?{r[c_hex[0]]:>5}{r[c_perf[0]]:>5}{r[c_ups[0]]:>6}{r[c_dns[0]]:>6}{r[c_bits[0]]:>10}{r[c_pair[0]]:>10}{r[c_chart[0]]:>4}")

# print(json.dumps(saveperf))
# print(len(list(bin_ary.keys())))

# print(g.dprep['index'])

# g.tmp1['columns'] = g.dprep['columns']
# g.tmp1['index'] = _index
# g.tmp1['data'] = _data

# with open('data/5_SOUNDEX_BTCUSDT.json', 'w') as outfile:
#     json.dump(g.tmp1, outfile)
