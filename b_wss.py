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
    # print(str)
    g.dprep.append(str)
    g.dprep = g.dprep[-288:]
    # ppjson = json.dumps(g.dprep,indent=4)
    ppjson = json.dumps(g.dprep)

    spair = g.cvars['pair'].replace("/","")
    outfile = '/tmp/_stream.tmp'

    with open(outfile, 'w') as fo:  # open the file in write mode
        fo.write(ppjson)
    fo.close()

    os.rename('/tmp/_stream.tmp', f'/tmp/_stream_{spair}.json')



    #
    #
    # file1 = open(outfile, "w")
    # spair = g.cvars['pair'].replace("/","")
    # file1.write("Timestamp, Open, High, Low, Close, Volume\n")
    # for d in g.dprep:
    #     file1.write(f"{d}\n")
    # file1.close()
    # df = pd.read_csv(outfile)
    #
    # # df.to_json(filename, orient='split', compression='infer', index='true')
    # df.to_json(f'data/stream_{spair}.json', orient='split', compression='infer', index='true')
    # # * mv when done
    # os.rename(f'data/stream_{spair}.json', f'data/_stream_{spair}.json')
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