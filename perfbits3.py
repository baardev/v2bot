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
version = 3
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

os.system(f"./check_data.py -s {src}")

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()

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

g.patsig = [0]*bits

# try:
#     data = g.dprep['data'] # * load a OHLC data file format
# except:
#     data = g.dprep # * load the streaming data

if not ncount:
    data = g.dprep['data'] # * load a OHLC data file formats
else:
    data = g.dprep['data'][-(ncount):] # * load a OHLC data file formats

o.sqlex(f"delete from vals3")
o.sqlex(f"ALTER TABLE vals3 AUTO_INCREMENT = 1")
g.cursor.execute("SET AUTOCOMMIT = 1")

with open("/tmp/_tmppb3.csv","w") as outfile:
    for d in data:
        if len(d) > 1:
            try:
                timestamp =  datetime.fromtimestamp(int(d[0])/1000)
                # exit()
                close = d[4]
                hold.append(close)
                hold = hold[-(bits+1):]
                if idx > bits+1:                                            # * are there enough vits to sample?
                    for i in range(bits):                                   # * loop through last <n> values
                        g.patsig[i] = 1 if hold[i+1] > hold[i] else 0       # * assign 1s and 0s

                    delta = hold[len(hold)-1] - hold[len(hold)-2]           # * get delta of last value

                    bsig = ''.join(map(str,g.patsig)).zfill(bits)           # * make a binary number from the values

                    val = int(bsig, base=2)                                 # * convert it to an int
                    hexv= '%08X' % int(bsig, 2)                             # * make hex val string of bin value

                    sstr = f"{str(bsig[:-1])}"                              # * gate the <n-1> bits as a string to preserve leading 0s
                    bin_ary[bsig]=sstr                                      # * add to array as a key

                    bin_ary_ct[bsig] = 1                                    # * default count array elemnts as 1 to prevent errors later on


                    outfile.write(f'0,{val},"{bsig}", {delta}\n')           # * save dec value, bin value. and delta value to CSV file
                idx += 1
                lastclose = close
            except Exception as e:
                print("\n")
                print(e)
                pass
cmd="""
LOAD DATA LOCAL INFILE '/tmp/_tmppb3.csv' 
INTO TABLE vals3 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 0 ROWS;
"""
o.sqlex(cmd)

print("")
countdown = len(bin_ary)
cmd = f"delete from rootperf3 where chart = '{chart}' and pair = '{pair}' and bits = '{bits}'"

o.sqlex(cmd)


ary = {}

cmd = f"select bin,val,count(val) as c, avg(delta) as a from vals3  where bin like '%0' group by val order by val"
rs = o.sqlex(cmd,ret="all")
for d in rs:
    ary[d[0]] = {'val':d[1],'count':d[2],'delta':d[3]}

cmd = f"select bin,val,count(val) as c, avg(delta) as a from vals3  where bin like '%1' group by val order by val"
rs = o.sqlex(cmd,ret="all")
for d in rs:
    ary[d[0]] = {'val':d[1],'count':d[2],'delta':d[3]}

keyList=sorted(bin_ary.keys())

for i,key in enumerate(keyList):
    # print(f"key:[{key}]")
    try:
        val = bin_ary[key]
        # hex = hex(int(val,2))[2:]
        hex = '%X' % int(val, 2)

        dex = int(hex, 16)

        try:
            dnct = ary[keyList[i]]['count']
            dnctv = ary[keyList[i]]['val']
            dnctd = ary[keyList[i]]['delta']

            upct = ary[keyList[i+1]]['count']
            upctv = ary[keyList[i+1]]['val']
            upctd = ary[keyList[i+1]]['delta']

            if upct > dnct:
                ratio = o.truncate((upct/dnct)-1,2)
            else:
                ratio = o.truncate((dnct/upct)-1,2)*-1

            # print(f'>>>>>>>   {delta} = {upctd} + {dnctd}')
            delta = upctd + dnctd
            # dratio = ratio

            cmd = f"""
                REPLACE INTO rootperf3 
                (root,hex,dex,perf,ups,dns,bits,pair,chart,delta) 
                VALUES 
                ('{val}','{hex}',{dex},{ratio},{upct},{dnct},{bits},'{pair}','{chart}',{delta})
            """
            # print(cmd)
            o.sqlex(cmd)

            # print(f"[{countdown}]\t{hex}\t{bin_ary[key]}?\t{ratio}\t({upct}/{dnct})")
            if countdown % 1000 == 0:
                print(f"Updating database: [{countdown}]",end="\r")
            countdown -= 1
        except:
            pass
    except Exception as e:
        traceback.print_exc()
        pass

 #4.80s user 3.35s system 7% cpu 1:46.85

o.sqlex(f"commit")#!/usr/bin/python -W ignore

saveperf = {}
cmd = f"select root,perf,delta from rootperf3 where bits = '{bits}' and chart = '{chart}' and pair = '{pair}'"
print(cmd)

rs = o.sqlex(cmd, ret="all")
for r in rs:
    saveperf[r[0]] = {"perf":r[1], 'delta':r[2]}

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
    [8,'ch'],
    [9,'delta']
]

cmd = f"select * from rootperf3 where bits = '{bits}' and pair = '{pair}' and chart = '{chart}' order by perf"
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
