#!/usr/bin/python -W ignore
import sys, os
import getopt
import json
import toml
import ccxt
import lib_v2_globals as g
import lib_v2_ohlc as o
import lib_v2_binance as b
from colorama import Fore, Style
from colorama import init as colorama_init
from datetime import datetime

colorama_init()

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
verbose = False
try:
    opts, args = getopt.getopt(argv, "-hvc", ["help", "verbose"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-v --verbose")
        sys.exit(0)

    if opt in ("-v", "--verbose"):
        verbose = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.dbc, g.cursor = o.getdbconn(dictionary = True)


cmd="select dtime, CAST(tstamp/1000 as INT) as tstamp,closed from stream"
rs = o.sqlex(cmd,ret="all")

for r in rs:

    # ststamp = datetime.strptime(r['dtime'], "%Y-%m-%d %H:%M:%S")
    print(r['dtime'].second,r['closed'])

    # if round(r['tstamp']) % 60 == 0:
    #     print(r['dtime'],r['tstamp'],r['closed'])


