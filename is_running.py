#!/usr/bin/python -W ignore
import lib_v2_ohlc as o

import toml
import lib_v2_globals as g
g.cvars = toml.load(g.cfgfile)

if o.checkIfProcessRunning(f"{g.cvars['cwd']}b_wss.py"):
    print('Already running... exiting')
    exit(1)
else:
    exit(0)

