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

    global long_file_handle
    global long_file
    global long_json_file

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

    if g.gcounter == 0:
        g.last_close = Close

    g.running_total += Close - g.last_close

    if abs(g.running_total) >= g.filteramt:
        g.recover += 1
        if g.verbose:
            print(Fore.YELLOW,g.recover, g.gcounter, line_ary, g.filteramt, f'{g.running_total:,.2f}', Style.RESET_ALL)

        # * save data to small file

        g.wss_small.append(line_ary)
        iloc_s = g.cvars['datawindow'] * -1
        g.wss_small = g.wss_small[iloc_s:]
        ppjson = json.dumps(g.wss_small, indent=4)
        spair = g.cvars['pair'].replace("/","")
        outfile = f'/tmp/_stream_filter_{g.filteramt}.tmp'

        # * save data to long file - fluch every n writes
        long_file_handle.write(line_str)
        if g.gcounter % 10 == 0:
            long_file_handle.flush()


        # * process long file every datawindow cycle
        if g.gcounter % g.cvars['datawindow'] == 0:
            long_file_handle_ro = open(long_file, "r")
            line = long_file_handle_ro.readline().strip()
            while(line):
                line = long_file_handle_ro.readline().strip()
                g.wss_large.append(line.split(","))
            # print(g.wss_large)
            long_ppjson = json.dumps(g.wss_large)
            with open(long_json_file, 'w') as fo:  # open the file in write mode
                fo.write(long_ppjson)
            fo.close()

            # df = pd.read_csv(long_file, compression='infer')
            # dfjson = df.to_json()
            # with open(long_json_file, 'w') as fo:  # open the file in write mode
            #     fo.write(json.dumps(dfjson))
            # fo.close()
            # del dfjson
            # del df

        # * don't keep file open as we are rewriting fromn scratch.
        with open(outfile, 'w') as fo:  # open the file in write mode
            fo.write(ppjson)
        fo.close()

        # # * mv when done - atomic action to prevent read error
        os.rename(f'/tmp/_stream_filter_{g.filteramt}.tmp', f'/tmp/_stream_filter_{g.filteramt}_{spair}.json')
        # shutil.copy2(f'/tmp/_stream_filter_{g.filteramt}_{spair}.json',f'/tmp/cp_stream_filter_{g.filteramt}_{spair}.json')
        g.running_total = 0
    else:
        if g.verbose:
            print(Fore.RED, g.recover, g.gcounter, line_ary, g.filteramt, f'{g.running_total:,.2f}', Style.RESET_ALL)
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

colorama_init()
g.recover = 0

# fn = f'/tmp/_stream_filter_{g.filteramt}.tmp'
#
# g.message_out =


long_file = f'data/_running_stream_filter_{g.filteramt}.tmp'
long_json_file = f'data/_running_stream_filter_{g.filteramt}.json'
long_file_handle = open(long_file, "a")  # append mode


dline = [float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan"),float("Nan")]
g.wss_small = [dline]*g.cvars['datawindow']

cc = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/{cc}@kline_1m"

ws = websocket.WebSocketApp(socket,on_message = on_message, on_error = on_error, on_close = on_close)

ws.run_forever()