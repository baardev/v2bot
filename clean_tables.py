#!/usr/bin/python -W ignore
import time

import websocket
import json
from pprint import pprint
import lib_v2_globals as g
import lib_v2_ohlc as o
import pandas as pd
import toml
import os, sys, getopt
import csv
from decimal import *
import datetime
from datetime import timedelta, datetime
import traceback
from pprint import pprint

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
pair = False
try:
    opts, args = getopt.getopt(argv, "-hp:", ["help","pair="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-p --pair ex:'BTCUSDT'")
        sys.exit(0)
    if opt in ("-p", "--pair"):
        pair = arg

if not pair:
    print("Missing -pair value")
    exit()

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.dbc, g.cursor = o.getdbconn(dictionary = True)

# * get the latest time
cmd=f"select dtime from stream_{pair} order by id desc limit 1"
# print(cmd)
rs = o.sqlex(cmd)[0]
dtime = rs['dtime']
sdtime = dtime.strftime("%Y-%m-%d %H:%M:%S")
print(f"Until Time: [{sdtime}] for [{pair}]")

# * get the first time of a non-closed record
cmd=f"select dtime from stream_{pair} where closed = 0 order by id asc limit 1"
# print(cmd)
rs = o.sqlex(cmd)[0]
odtime = rs['dtime']
osdtime = odtime.strftime("%Y-%m-%d %H:%M:%S")
# print(osdtime)
# print(f"From [{osdtime}] -> [{sdtime}] for [{pair}]")



cmd=f"select * from stream_{pair} where dtime <= '{sdtime}' and dtime >= '{osdtime}'"
rs = o.sqlex(cmd)

vlist = []
for r in rs:
    vlist.append(list(r.values()))

# *  get keys/col names
colnames = list(rs[0].keys())

# print(colnames)
csvfile = f'stream/stream_{pair}.csv'

print(f"saving to [{csvfile}]")

if os.path.isfile(csvfile):
    with open(csvfile, 'a', newline='') as f_handle:
        writer = csv.writer(f_handle)
        for row in vlist:
            writer.writerow(row)
else:
    with open(csvfile, 'w', newline='') as f_handle:
        writer = csv.writer(f_handle)
        writer.writerow(colnames)
        for row in vlist:
            writer.writerow(row)

ts = f"{time.time()}"


g.issue = o.get_issue()
if g.issue == "LOCAL":
    cmd = f"mysqldump -ujmc -p6kjahsijuhdxhgd jmcap stream_{pair} --add-drop-table > stream/stream_{pair}_{ts}.sql"
    os.system(cmd)
if g.issue == "REMOTE":
    cmd = f"mysqldump -uSpartacus -pholo3601q2w3e jmcap stream_{pair} --add-drop-table > stream/stream_{pair}_{ts}.sql"
    os.system(cmd)

cmd=f"delete from stream_{pair} where dtime <= '{sdtime}' and closed = 0"
# print(cmd)
rs = o.sqlex(cmd)



exit()

# * make table output

df = pd.DataFrame(rs)
print(df)
dfcsv = df.to_csv()
csvfile = f'_tmp_{bits}_{g.BASE}{g.QUOTE}_{chart}.csv'
with open(csvfile, 'w') as outfile:
    outfile.write(dfcsv)
print(f"CSV file saved as: {csvfile}")

