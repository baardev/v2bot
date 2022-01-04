#!/usr/bin/env python

import websocket
import json
from pprint import pprint
import lib_v2_globals as g
import pandas as pd
import toml
import os, sys
from decimal import *
import datetime
from datetime import timedelta, datetime
from time import time
from time import sleep
import random
from math import*

g.cvars = toml.load(g.cfgfile)


def cycle_in_range(number, amin, amax, invert=False):
    try:
        mod_num = number % amax
    except:
        mod_num = 0

    try:
        mod_num2 = number % (amax * 2)
    except:
        mod_num2 = 0

    new_val1 = abs(mod_num2 - (mod_num * 2))

    old_min = 0
    old_min = 0
    old_max = amax
    new_max = amax
    new_min = amin

    try:
        new_value = ((new_val1 - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
    except:
        new_value = 0

    new_value = amax - new_value if invert else new_value

    return (round(new_value))




# a=[0]*sample
# for n in range(sample):
#     a[n]=sin(2*pi*f*n/Fs)

g.cvars = toml.load(g.cfgfile)

dary = []

dline = [float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan")]
g.dprep = [dline]*288

i = 0
j=0
while True:

    g.cvars = toml.load(g.cfgfile)

    Fs = g.cvars['Fs']
    f = g.cvars['f']

    c =  cycle_in_range(i, 1, 100)

    j=((sin(2*pi*f*i/Fs) ** 2) * 100 * c) + 1

    epoch = milliseconds = int(time() * 1000)
    Timestamp   = epoch
    Open        = j
    High        = j
    Low         = j
    Close       = j
    Volume      = j
    str=[Timestamp,Open,High,Low,Close,Volume]
    g.dprep.append(str)
    g.dprep = g.dprep[-288:]
    ppjson = json.dumps(g.dprep)

    spair = g.cvars['pair'].replace("/","")
    outfile = '/tmp/_stream_test.tmp'

    with open(outfile, 'w') as fo:  # open the file in write mode
        fo.write(ppjson)
    fo.close()

    # # * mv when done
    os.rename('/tmp/_stream_test.tmp', f'/tmp/_stream_{spair}_test.json')

    i = i + 1
    # j = i % 10
    sleep(0.5)

