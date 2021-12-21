#!/usr/bin/python3.9
from datetime import datetime
import ccxt
import pandas as pd
# + from lib_cvars import Cvars
import lib_ohlc as o
import getopt, sys, os
import time
import lib_globals as g
import logging

g.logit = logging
g.logit.basicConfig(
    filename="/home/jw/src/jmcap/ohlc/logs/ohlc.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=o.cvars.get('logging')
)
stdout_handler = g.logit.StreamHandler(sys.stdout)

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hi:f:o:b:e:", ["help","index=","infile=","outfile=","begin=", "end="])
except getopt.GetoptError as err:
    sys.exit(2)

in_files = "backdata*"
out_file = "out"
g.idx = 0
# + begindate = '1970-01-01 00:00:00'
# + enddate = '2970-01-01 00:00:00'
begindate = '2017-01-01'
enddate = '2025-01-01'

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-d, --infile   files to readin")
        print("-o, --outfile  output file (alt name)")
        print("-i, --index  sequential number in series")
        print("-b, --begin  filter start date (def '1970-01-01 00:00:00'")
        print("-e, --end    filter end  date (def '2025-01-01 00:00:00'")
        sys.exit(0)

    if opt in ("-i", "--index"):
        g.idx=int(arg)
    if opt in ("-f", "--infile"):
        in_files = arg
    if opt in ("-o", "--outfile"):
        out_file = arg
    if opt in ("-b", "--begin"):
        begindate = arg
    if opt in ("-e", "--end"):
        enddate = arg

# + g.cfgfile = "/home/jw/src/jmcap/ohlc/config_0.hcl"
# + o.cvars = Cvars(g.cfgfile)


import glob
import re

type = 0
pair = 1
t_frame = 2
fromdate = 3
todate = 4
count = 5
exchange = 6
sequence = 7

datas = []
for i in range(g.idx):
     dlist = glob.glob(f'data/{in_files}*_{i}.json')
     for d in dlist:
         parts = re.split('\/|\.|_',d)

         dir = parts[0]
         type = parts[1]
         pair = parts[2]
         t_frame = parts[3]
         fromdate = parts[4]
         fromtime = parts[5]
         todate = parts[8]
         totime = parts[9]
         count = parts[10]
         exchange = parts[11]
         sequence = parts[12]

         # + print(parts)
         # + print("xxx",dir,type,pair,t_frame,fromdate,fromtime,todate,totime, count,exchange,sequence)
         # + exit()

         print(f"Reading: {d}")
         # + * fill out
         jd = o.cvars.load(f"{d}") # + ! returns list
         ndf = pd.DataFrame(jd)
         # + print(pd.to_datetime(ndf['Date'], unit='ms'))
         fndf = ndf[
             (ndf['Date'] >= begindate) & (ndf['Date'] <= enddate)
         ]
         # + print(fndf)
         # + datas.append(pd.DataFrame(jd))
         datas.append(fndf)



bigdata = pd.concat(datas,  ignore_index=True)
bigdata.set_index('Date')

fromdate = f"{pd.to_datetime(bigdata['Date'].iloc[0], unit='ms')}"
todate = f"{pd.to_datetime(bigdata['Date'].iloc[-1], unit='ms')}"
# + fromdate = f"{pd.to_datetime(bigdata['Date'].iloc[0])}"
# + todate = f"{pd.to_datetime(bigdata['Date'].iloc[-1])}"
fromdate = fromdate.replace(" ", "_")
todate = todate.replace(" ", "_")


names = {
    'fromdate': fromdate,
    'todate': todate,
    'type': type,
    'pair': pair,
    't_frame':  t_frame,
    'count': count,
    'exchange': exchange
}

bigfn = f"data/_ALL.{type}.{pair}.{t_frame}.{fromdate}...{todate}.{count}.{exchange}"
o.cvars.csave(names,f"{bigfn}_DATA.json")
cmd = f"cp {bigfn}_DATA.json data/{out_file}_DATA.json"
os.system(cmd)

# + print(bigdata.info)
o.cvars.save(bigdata,f"{bigfn}.json")
cmd = f"cp {bigfn}.json data/{out_file}.json"
os.system(cmd)