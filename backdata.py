#!/usr/bin/env python

import getopt, sys, os, glob
import time
import calendar
from dateutil.parser import parse as date_parse

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-ho:i:d:m", ["help","outfile=","index=","date=","user="])
except getopt.GetoptError as err:
    sys.exit(2)

input_filename = False
adate = "2020-01-01 00:00:00"
idx = 0
out_filename = "xout.txt"
manual = False

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-o, --outfile  alt saved filename")
        print("-d, --date  startdate")
        print("-i, --index  number of series")
        print("-m, --manual  prompt for each load")
        sys.exit(0)

    if opt in ("-i", "--index"):
        idx=int(arg)
    if opt in ("-d", "--date"):
        adate = arg
    if opt in ("-o", "--outfile"):
        out_filename = arg
    if opt in ("-m", "--manual"):
        manual = True
        idx=1000
try:
    os.remove("_backtest.tmp")
except:
    pass

files = glob.glob('data/backdata*')
for file in files:
    os.remove(file)

tm = adate #'1970-01-01 06:00:00 +0500'
# fmt = '%Y-%m-%d %H:%M:%S %z'
fmt = '%Y-%m-%d %H:%M:%S'
# epoch = calendar.timegm(datetime.strptime(tm, fmt).utctimetuple())
# epoch = datetime.strptime(tm, fmt).utctimetuple()
dt = date_parse(adate)
epoch = calendar.timegm(dt.timetuple())
epoch = f"{epoch}000"

for i in range(idx):
    if manual:
        nxt = input("Next? (x to quit) :")
        if nxt == "x":
            break
    if os.path.isfile("_backtest.tmp"):
        with open('_backtest.tmp', 'r') as file:
            epoch = file.read().replace('\n', '')
    cmd = f"./ohlc_backdata.py -d {epoch} -i {i}"
    # print(cmd)
    os.system(cmd)
    # time.sleep(10)

print("================= MERGING ==================")    
cmd = f"./merge.py -i {idx} -o {out_filename}"
print(cmd)
print("============================================")
os.system(cmd)
