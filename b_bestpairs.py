#!/usr/bin/env python

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.animation as animation
import lib_v2_globals as g
import toml
import getopt
import sys
import lib_v2_binance as b
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
src = "test"
pairs = "ETHBTC"
bases = ['ETH','BTC','BNB','OOKI','BUSD','SAND','LUNA','XRP','SHIB','NEAR','FTM','MATIC','AVAX','MANA','GALA']
quotes = ['BTC','USDT','BUSD']


try:
    opts, args = getopt.getopt(argv, "-h", ["help"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        sys.exit(0)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
srcurl = "https://testnet.binance.vision"

for base in bases:
    for quote in quotes:
        if base == quote:
            continue
        pair = f"{base}{quote}"

        try:
            r = requests.get(f"{srcurl}/api/v3/depth", params=dict(symbol=pair))
            results = r.json()
            bids = len(results['bids'])
            asks = len(results['asks'])
            print(f"{pair}: {bids}/{asks}")


            # frames = {side: pd.DataFrame(data=results[side], columns=["price", "quantity"], dtype=float) for side in ["bids", "asks"]}
            # frames_list = [frames[side].assign(side=side) for side in frames]
            # data = pd.concat(frames_list, axis="index",ignore_index=True, sort=True)
            #
            #
            # price_summary = data.groupby("side").price.describe()
            # price_summary.to_markdown()
            #
            # r = requests.get(f"{srcurl}/api/v3/ticker/bookTicker", params=dict(symbol=pair))
            # book_top = r.json()
            #
            # name = book_top.pop("symbol")  # get symbol and also delete at the same time
            # s = pd.Series(book_top, name=name, dtype=float)
            # s.to_markdown()
            # print("OK",pair)
        except:
            # print("BAD",pair)
            pass

