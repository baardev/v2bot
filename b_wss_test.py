#!/usr/bin/python

import websocket
import json
import lib_v2_globals as g
import lib_v2_ohlc as o
import toml
import os, sys, getopt, mmap, time, math
import pandas as pd
import datetime

from colorama import Fore, Style
from colorama import init as colorama_init

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn(dictionary = True)

def typeit(v):
    try:
        x=float(v)
        return(v)
    except:
        return(f"'{v}'")

def on_message(ws, message):
    # !'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

    global long_file_handle_ary
    global long_file_ary
    global long_json_file_ary
    global spair

    cnames = {
        "start_time" : "t",
        "close_time" : "T",
        "symbol" : "s",
        "chart_interval" : "i",
        "first_trade_id" : "f",
        "last_trade_id" : "L",
        "open" : "o",
        "close" : "c",
        "high" : "h",
        "low" : "h",
        "base_asset_vol" : "v",
        "trades" : "n",
        "closed" : "x",
        "quote_asset_vol" : "q",
        "taker_buy_base_asset_vol" : "V",
        "taker_buy_quote_asset_vol" : "Q",
        "ignored" : "B"
    }

    dary = json.loads(message)
    epoch = dary['E']

    # if dary['k']['x']:
    #     dary['k']['x'] = False
    # else:

    cols = ""
    vals = ""
    for key in cnames:
        cols += f"{key},"
        vals += f"{typeit(dary['k'][cnames[key]])},"

    cols = f"dtime,tstamp," + cols
    vals = f"'{datetime.datetime.fromtimestamp(epoch/1000)}',{epoch}," + vals

    cols = cols.rstrip(",")
    vals = vals.rstrip(",")

    # ! used just to feill > 288 rows
    # for i in range(288):
    #     cmd = f"INSERT INTO stream ({cols.rstrip(',')}) VALUES ({vals.rstrip(',')})"
    #     o.sqlex(cmd)

    cmd = f"INSERT INTO stream ({cols.rstrip(',')}) VALUES ({vals.rstrip(',')})"
    # print(cmd)
    try:
        o.sqlex(cmd)
    except Exception as e:
        print(f"SQL ERROR: [{e}]")

    sdata = []
    # if dary['k'][cnames['closed']]:
    if True:
        # cmd = "select dtime,tstamp,open,high,low,close,base_asset_vol from stream where closed = True"
        cmd = f"""
        SELECT * FROM (
            SELECT dtime,tstamp,open,high,low,close,base_asset_vol FROM stream
            WHERE closed = TRUE 
            ORDER BY dtime DESC LIMIT 288
        ) Var1
            ORDER BY dtime ASC
        """
        rs = o.sqlex(cmd,ret="all")

        for r in rs:
            ary = [r['tstamp'],r['open'],r['high'],r['low'],r['close'],r['base_asset_vol']]
            sdata.append(ary)

        # fdtime = datetime.datetime.fromtimestamp(sdata[len(sdata)-1][0]/1000)
        # fclose = sdata[len(sdata)-1][4]

        # print(f"{g.gcounter} Saved: {fdtime} [{fclose}]")

        with open("/tmp/_BTCUSDT_1m_0f.json", 'w') as outfile:
            outfile.write(json.dumps(sdata))

        g.gcounter += 1

def on_error(ws,error):
    print("ERROR",error)

def on_close(ws,a,b):
    print(f"### closed [{a}] [{b}]   ###")

# + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
os.chdir(g.cvars['cwd'])
g.cvars = toml.load(g.cfgfile)
g.wss_filters = g.cvars['wss_filters']
g.filteramt = 0 # * def no filter
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
g.verbose = False
g.pair = g.cvars['pair']
try:
    opts, args = getopt.getopt(argv, "-hva:p:", ["help", "verbose", "pair="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help")
        print("-v, --verbose")
        print("-p, --pair")
        sys.exit(0)

    if opt in ("-v", "--verbose"):
        g.verbose = True

    if opt in ("-p", "--pair"):
        g.pair = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

colorama_init()
g.recover = 0

spair = g.pair.replace("/","")
# * define and open here to reduse file i/o


cc = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/{cc}@kline_1m"

g.gcounter +=1 # * add one to skipe the first  mod 0 condition in the flush routine
ws = websocket.WebSocketApp(socket,on_message = on_message, on_error = on_error, on_close = on_close)

ws.run_forever()