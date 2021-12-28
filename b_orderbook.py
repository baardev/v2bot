#!/usr/bin/env python

import lib_v2_globals as g
import toml
import getopt
import sys
import ccxt
import time
import operator
from pprint import pprint
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
pair = "ETH/BTC"
appendfile = False
interval = 10
try:
    opts, args = getopt.getopt(argv, "-hap:i:", ["help","append","pair=","interval="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-a --append (to '_od_<base>_<quote>.csv')")
        print("-p --pair <base/quote>  defauiltr: ETH/BTC")
        sys.exit(0)
    if opt in ("-a", "--append"):
        appendfile = True
    if opt in ("-p", "--pair"):
        pair = arg

    if opt in ("-i", "--interval"):
        interval = int(arg)

spair = pair.replace("/","_")
outfile = f"_ob_{spair}.csv"
print(f"OUTFILE: {outfile}")
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

# ! https://www.binance.com/en/orderbook/ETH_BTC

g.cvars = toml.load(g.cfgfile)
srcurl = "https://testnet.binance.vision"

g.ticker_src = ccxt.binance()

str = "MAX bid amt\tAVG bid amt\tMAX ask amt\tAVG avg amt\n"
# print(str)
if not appendfile:
    file1 = open(outfile, "w")
    file1.write(str)
    file1.close()

while True:
    orderbook = g.ticker_src.fetch_order_book(pair, limit=15)
    asks = orderbook['asks']
    bids = orderbook['bids']

    ask_amt = []
    for a in asks:
        ask_amt.append(a[1])

    bid_amt = []
    for b in bids:
        bid_amt.append(b[1])

    max_bid_amt = max(bid_amt)
    avg_bid_amt = sum(bid_amt)/len(bid_amt)
    max_ask_amt = max(ask_amt)
    avg_ask_amt = sum(ask_amt)/len(ask_amt)

    str = f"{max_bid_amt}\t{avg_bid_amt}\t{max_ask_amt}\t{avg_ask_amt}\n"
    # print(str)
    file1 = open(outfile, "a")
    file1.write(str)
    file1.close()

    time.sleep(interval)

