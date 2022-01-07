#!/usr/bin/env python

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

from colorama import Fore, Style
from colorama import init as colorama_init

colorama_init()


def on_message(ws, message):
    # !'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

    dary = json.loads(message)
    epoch  =dary['E']

    # Timestamp = f"{datetime.utcfromtimestamp(epoch / 1000).replace(microsecond = epoch % 1000 * 1000)}"
    Timestamp   = epoch
    Open        = float(dary['k']['o'])
    High        = float(dary['k']['h'])
    Low         = float(dary['k']['l'])
    Close       = float(dary['k']['c'])
    Volume      = float(dary['k']['v'])

    str=[Timestamp,Open,High,Low,Close,Volume]

    if g.gcounter == 0:
        g.last_close = Close

    g.running_total += Close - g.last_close

    if abs(g.running_total) > g.filteramt:
        g.recover += 1
        if g.verbose:
            print(Fore.YELLOW,g.recover, g.gcounter,str,g.filteramt, f'{g.running_total:,.2f}', Style.RESET_ALL)
        g.wss_small.append(str)

        iloc_s = g.cvars['datawindow'] * -1
        # iloc_l = iloc_s * 4
        # g.wss_large = g.wss_large[iloc_l:]
        g.wss_small = g.wss_small[iloc_s:]
        # ppjson = json.dumps(g.wss_small,indent=4)
        ppjson = json.dumps(g.wss_small, indent=4)
        # ppjson = json.dumps(g.dprep)

        spair = g.cvars['pair'].replace("/","")
        outfile = f'/tmp/_stream_filter_{g.filteramt}.tmp'

        with open(outfile, 'w') as fo:  # open the file in write mode
            fo.write(ppjson)
        fo.close()

        # # * mv when done
        os.rename(f'/tmp/_stream_filter_{g.filteramt}.tmp', f'/tmp/_stream_filter_{g.filteramt}_{spair}.json')
        g.running_total = 0
    else:
        if g.verbose:
            print(Fore.RED, g.recover, g.gcounter, str, g.filteramt, f'{g.running_total:,.2f}', Style.RESET_ALL)
    g.last_close = Close
    g.gcounter += 1

def on_error(ws,error):
    print(error)

def on_close(ws,a,b):
    print(f"### closed [{a}] [{b}]   ###")

g.cvars = toml.load(g.cfgfile)
g.filteramt = 0 # * def no filter


# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
g.verbose = False
try:
    opts, args = getopt.getopt(argv, "-hva:", ["help", "verbose", "amtfilter="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help")
        print("-v, --verbose")
        print("-a, --amtfilter <cum amount>")
        sys.exit(0)

    if opt in ("-a", "--amtfilter"):
        g.filteramt = float(arg)

    if opt in ("-v", "--verbose"):
        g.verbose = True

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡


dline = [float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan")]
g.wss_large = [dline]*1000
g.wss_small = [dline]*g.cvars['datawindow']

cc = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/{cc}@kline_1m"

ws = websocket.WebSocketApp(socket,on_message = on_message, on_error = on_error, on_close = on_close)

ws.run_forever()