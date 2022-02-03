#!/usr/bin/python -W ignore
import readline as readline
from io import StringIO
import csv
import lib_v2_globals as g
import lib_v2_ohlc as o
import pandas as pd
import toml
import os, sys, getopt, json
import matplotlib.pyplot as plt
import datetime

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-h", ["help"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        sys.exit(0)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)




infile = open("data/BTCUSDT_0m_0f.csv", 'r')
lines = infile.readlines()

count = 0
for line in lines:
    count += 1
    # if count > 10: exit()

    reader = line.split(',')
    try:
        timestamp = int(int(reader[0])/1000)

        modby = 59
        # print(timestamp)
        # print(timestamp % modby)
        #
        if timestamp % modby == 0:
            date = datetime.datetime.fromtimestamp(timestamp)
            close = float(reader[4])
            print(date,close)
    except:
        pass
