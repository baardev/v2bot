#!/usr/bin/python -W ignore
import cProfile
import gc
import re
import ccxt
import sys
import getopt
import logging
import os
import time
import toml
import pandas as pd
import lib_v2_globals as g
import lib_v2_ohlc as o
from datetime import datetime
from pathlib import Path
from colorama import init as colorama_init
from colorama import Fore, Back, Style

g.cvars = toml.load(g.cfgfile)
g.display = g.cvars['display']
g.headless = g.cvars['headless']

try:
    import matplotlib
    matplotlib.use("Qt5agg")
    import matplotlib.animation as animation
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure
    import lib_v2_listener as kb
    g.headless = False
except:
     # * assume this is headless if er end up here as the abive requires a GUI
    g.headless = True


binance = ccxt.binance()

orderbook_binance_btc_usdt = binance.fetch_order_book('BTC/USDT')
bids_binance = orderbook_binance_btc_usdt['bids']
asks_binanace = orderbook_binance_btc_usdt['asks']
df_bid_binance = pd.DataFrame(bids_binance, columns=['price','qty'])
df_ask_binance = pd.DataFrame(asks_binanace, columns=['price','qty'])

fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 8), dpi=80)
ax1.plot(df_bid_binance['price'], df_bid_binance['qty'],label='Binance',color='g')
ax1.fill_between(df_bid_binance['price'], df_bid_binance['qty'],color='g')
ax2.plot(df_ask_binance['price'], df_ask_binance['qty'],label='FTX',color='r')
ax2.fill_between(df_bid_binance['price'], df_bid_binance['qty'],color='r')
ax1.set_title('Ask Price vs Quantity for Binance')
ax2.set_title('Bid Price vs Quantity for Binance')
# plt.show()
fig.savefig('images/plot_volprice.png')
exit()