#!/usr/bin/env python

import websocket
import json
import lib_v2_globals as g
import lib_v2_ohlc as o
import toml
import os, sys, getopt, mmap
import pandas as pd

from colorama import Fore, Style
from colorama import init as colorama_init

def on_message(ws, message):
    # !'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

    global long_file_handle_ary
    global long_file_ary
    global long_json_file_ary
    global spair

    dary = json.loads(message)
    epoch  =dary['E']
    g.wss_large = []

    # Timestamp = f"{datetime.utcfromtimestamp(epoch / 1000).replace(microsecond = epoch % 1000 * 1000)}"
    Timestamp   = epoch
    Open        = float(dary['k']['o'])
    High        = float(dary['k']['h'])
    Low         = float(dary['k']['l'])
    Close       = float(dary['k']['c'])
    Volume      = float(dary['k']['v'])

    line_ary = [Timestamp,Open,High,Low,Close,Volume]
    line_str = f"{Timestamp},{Open},{High},{Low},{Close},{Volume}\n"

    if g.gcounter == 1:
        g.last_close = Close


    _index = []
    _data = []
    g.tmp1 = {'columns': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], 'index': [], 'data': []}

    for f in range(len(g.wss_filters)):
        g.running_total[f] += Close - g.last_close
        if abs(g.running_total[f]) >= g.wss_filters[f]:
            g.recover += 1
            if g.verbose:
                print(Fore.YELLOW,g.recover, g.gcounter, line_ary, f"f={g.wss_filters[f]}", f'{g.running_total[f]:,.2f}', Style.RESET_ALL)

            # * save data to small file

            g.wss_small.append(line_ary)                # * add each line to list
            iloc_s = g.cvars['datawindow'] * -1         # * get size to trim array
            g.wss_small = g.wss_small[iloc_s:]          # * create resize list
            ppjson = json.dumps(g.wss_small)  # * create JSON format of data
            # spair = g.cvars['pair'].replace("/","")     # * get restringed pair name
            outfile = f"/tmp/_{spair}_0m_{g.wss_filters[f]}f.tmp"
            # print(f"WRITING to {outfile}")
            # * save to file - don't keep file open as we are rewriting fromn scratch.
            with open(outfile, 'w') as fo:  # open the file in write mode
                fo.write(ppjson)
            fo.close()

            # * save data to long file - flush every n writes
            long_file_handle_ary[f].write(line_str)
            if g.gcounter % 10 == 0:
                long_file_handle_ary[f].flush()


            # * process long file every datawindow cycle
            # if g.gcounter % 1 == 0:
            if g.gcounter % g.cvars['datawindow'] == 0:
                long_file_handle_ro = open(long_file_ary[f], "r")
                line = long_file_handle_ro.readline().strip()
                nidx = 0
                while(line):
                    line = long_file_handle_ro.readline().strip()
                    g.wss_large.append(line.split(","))
                    _index.append(nidx)
                    nidx += 1
                # g.tmp1['columns'] = g.dprep['columns']
                g.tmp1['index'] = _index
                g.tmp1['data'] = g.wss_large

                long_ppjson = json.dumps(g.tmp1)
                long_file_handle_ary[f].flush()
                with open(long_json_file_ary[f], 'w') as fo:  # open the file in write mode
                    if g.verbose:
                        print("writing final OHLC file:",long_json_file_ary[f])
                    fo.write(long_ppjson)
                fo.close()


            # # * mv when done - atomic action to prevent read error
            os.rename(f'/tmp/_{spair}_0m_{g.wss_filters[f]}f.tmp', f'/tmp/_{spair}_0m_{g.wss_filters[f]}f.json')
            # shutil.copy2(f'/tmp/_stream_filter_{g.filteramt}_{spair}.json',f'/tmp/cp_stream_filter_{g.filteramt}_{spair}.json')
            g.running_total[f] = 0
        else:
            if g.verbose:
                print(Fore.RED, g.recover, g.gcounter, line_ary, f"f={g.wss_filters[f]}", f'{g.running_total[f]:,.2f}', Style.RESET_ALL)
    g.last_close = Close
    g.gcounter += 1

def on_error(ws,error):
    print(error)

def on_close(ws,a,b):
    print(f"### closed [{a}] [{b}]   ###")

# + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

#
# if o.checkIfProcessRunning('/home/jw/store/src/jmcap/v2bot/b_wss.py'):
#     print('Already running... exiting')
#     exit()
os.chdir("/home/jw/src/jmcap/v2bot")

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

long_file_ary = []
long_json_file_ary = []
long_file_handle_ary = []
g.running_total = []
for f in range(len(g.wss_filters)):
    long_file_ary.append(f"data/{spair}_0m_{g.wss_filters[f]}f.csv")
    long_json_file_ary.append(f"data/{spair}_0m_{g.wss_filters[f]}f.json")
    long_file_handle_ary.append(open(long_file_ary[f], "a"))  # append mode
    g.running_total.append(0)

dline = [float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan")]
g.wss_small = [dline]*g.cvars['datawindow']

cc = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/{cc}@kline_1m"

g.gcounter +=1 # * add one to skipe the first  mod 0 condition in the flush routine
ws = websocket.WebSocketApp(socket,on_message = on_message, on_error = on_error, on_close = on_close)

ws.run_forever()