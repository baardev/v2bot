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

o.sqlex(f"delete from vals2")
o.sqlex(f"ALTER TABLE vals2 AUTO_INCREMENT = 1")
g.cursor.execute("SET AUTOCOMMIT = 0")

with open("/tmp/_tmppb2.csv","w") as outfile:
    for d in data:
        if len(d) > 1:
            try:
                timestamp =  datetime.fromtimestamp(int(d[0])/1000)
                # exit()
                close = d[4]
                hold.append(close)
                hold = hold[-(bits+1):]
                delta = 0
                if idx > bits+1:
                    for i in range(bits):
                        g.patsig[i] = 1 if hold[i+1] > hold[i] else 0
                        # if g.patsig[i] == 1:
                        delta = round(float(hold[i+1]) - float(hold[i]))

                    bsig = ''.join(map(str,g.patsig)).zfill(bits)

                    val = int(bsig, base=2)
                    sstr = str(bsig[:-1])
                    sstr = f"{sstr}"
                    # print(f"Analyzing patterns in record: [{idx}]\t{sstr}?", end="\r")
                    bin_ary[bsig]=sstr
                    # delta_ary[bsig]=delta

                    bin_ary_ct[bsig] = 1
                    hexv= '%08X' % int(bsig, 2)

                    outfile.write(f'0,{val},"{bsig}", {delta}\n')

                    # cmd = f"insert into vals2 (val, bin, delta) values ({val},'{bsig}', {delta})"
                    # o.sqlex(cmd)
                idx += 1
                lastclose = close
            except Exception as e:
                print("\n")
                print(e)
                pass

cmd="""
LOAD DATA LOCAL INFILE '/tmp/_tmppb2.csv' 
INTO TABLE vals2 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 0 ROWS;
"""
o.sqlex(cmd)
print("")
countdown = len(bin_ary)
cmd = f"delete from rootperf2 where chart = '{chart}' and pair = '{pair}' and bits = '{bits}'"
o.sqlex(cmd)



ary0 = {}
ary1 = {}

cmd = f"select bin,val,count(val)+0 as c, avg(delta)+0 as a from vals3  group by val order by val"
rs = o.sqlex(cmd,ret="all")
for d in rs:
    ary0[d[0]] = {'val':d[1],'count':d[2],'delta':d[3]}

cmd = f"select bin,val,count(val)+0 as c, avg(delta)+1 as a from vals3  group by val order by val"
rs = o.sqlex(cmd,ret="all")
for d in rs:
    ary1[d[0]] = {'val':d[1],'count':d[2],'delta':d[3]}

print(f"LINES: {len(bin_ary)}")



for key in bin_ary:
    # print(f"key:[{key}]")
    try:
        val = bin_ary[key]
        # hex = hex(int(val,2))[2:]
        hex = '%X' % int(val, 2)

        dex = int(hex, 16)

        dnct = ary0[key]['count']
        dnctv = ary0[key]['val']

        upct = ary1[key]['count']
        upctv = ary1[key]['val']

        # cmd = f"select count(val)+0 as c, avg(delta)+0 as a from vals2 where bin like '{val}0' group by val order by c"
        # # print(cmd)
        # dnctx = o.sqlex(cmd, ret="all")
        # if len(dnctx) == 0:
        #     dnctx = [(1, 0)]
        # dnct = dnctx[0][0]
        # dnctv = dnctx[0][1]
        #
        # cmd = f"select count(val)+0 as c, avg(delta)+0 as a  from vals2 where bin like '{val}1' group by val order by c"
        # upctx = o.sqlex(cmd, ret="all")
        # if len(upctx) == 0:
        #     upctx = [(1,0)]
        # upct = upctx[0][0]
        # upctv = upctx[0][1]

        if upct > dnct:
            ratio = o.truncate((upct/dnct)-1,2)
        else:
            ratio = o.truncate((dnct/upct)-1,2)*-1



        dratio = (dnctv+upctv)


        cmd = f"replace into rootperf2 (root,hex,dex,perf,ups,dns,bits,pair,chart,delta) values ('{val}','{hex}',{dex},{ratio},{upct},{dnct},{bits},'{pair}','{chart}',{dratio})"
        o.sqlex(cmd)

        # print(f"[{countdown}]\t{hex}\t{bin_ary[key]}?\t{ratio}\t({upct}/{dnct})")
        print(f"Updating database: [{countdown}]",end="\r")
        countdown -= 1
    except Exception as e:
        print(e)
        pass

 #4.80s user 3.35s system 7% cpu 1:46.85

o.sqlex(f"commit")
saveperf = {}
cmd = f"select root,perf from rootperf2 where bits = '{bits}' and chart = '{chart}' and pair = '{pair}'"
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
    [8,'ch'],
    [9,'delta']
]

cmd = f"select * from rootperf2 where bits = '{bits}' and pair = '{pair}' and chart = '{chart}' order by perf"
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
