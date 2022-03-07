#!/usr/bin/python -W ignore
import lib_v2_ohlc as o
import getopt,sys

import toml
import lib_v2_globals as g
g.cvars = toml.load(g.cfgfile)

pname = "python ./sr_00.py"

isRunning = o.checkIfProcessRunning(pname)

if isRunning:
    print(f'[{pname}] already running... exiting')
    exit(1)
else:
    print(f'[{pname}] not running... starting')
    exit(0)

