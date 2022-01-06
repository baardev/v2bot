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


g.cvars = toml.load(g.cfgfile)

g.last_close = 0
g.gcounter = 0
def on_message(ws, message):
    g.cvars = toml.load(g.cfgfile)
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
    wclose      = float(dary['k']['x'])

    str=[Timestamp,Open,High,Low,Close,Volume]
    # str=[g.gcounter,Open,High,Low,Close,Volume]

    print("\t",g.gcounter)
    if abs(Close-g.last_close) >= (Close * Volume) * g.cvars['time_filter_pct']:
        print(g.gcounter,str)
        g.dprep.append(str)
        g.dprep = g.dprep[-288:]
        # ppjson = json.dumps(g.dprep,indent=4)
        ppjson = json.dumps(g.dprep)

        spair = g.cvars['pair'].replace("/","")
        outfile = '/tmp/_stream_ohlc.tmp'

        with open(outfile, 'w') as fo:  # open the file in write mode
            fo.write(ppjson)
        fo.close()

        # # * mv when done
        os.rename('/tmp/_stream_ohlc.tmp', f'/tmp/_stream_ohlc_{spair}.json')
    g.last_close = Close
    g.gcounter += 1
def on_error(ws,error):
    print(error)

def on_close(ws,a,b):
    print(f"### closed [{a}] [{b}]   ###")


dline = [float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan")]
g.dprep = [dline]*288

cc = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/{cc}@kline_1m"

ws = websocket.WebSocketApp(socket,on_message = on_message, on_error = on_error, on_close = on_close)


ws.run_forever()