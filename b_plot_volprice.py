#!/usr/bin/python
import getopt
import sys

import ccxt
import pandas as pd
import toml

import lib_v2_globals as g
import lib_v2_ohlc as o

g.cvars = toml.load(g.cfgfile)
g.display = g.cvars['display']
g.headless = g.cvars['headless']

try:
    import matplotlib

    if o.X_is_running():
        matplotlib.use("Qt5agg")
    else:
        matplotlib.use("Agg")
    import matplotlib.animation as animation
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure
    import lib_v2_listener as kb

    g.headless = False
except Exception as e:
    # * assume this is headless if er end up here as the abive requires a GUI
    print(e)
    g.headless = True

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
isX = False
try:
    opts, args = getopt.getopt(argv, "-hX", ["help", "isX"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-X, --isX (has X11 def=False)")
        sys.exit(0)

    if opt in ("-X", "--isX"):
        isX = True

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

binance = ccxt.binance()

orderbook_binance_btc_usdt = binance.fetch_order_book('BTC/USDT')
bids_binance = orderbook_binance_btc_usdt['bids']
asks_binanace = orderbook_binance_btc_usdt['asks']
df_bid_binance = pd.DataFrame(bids_binance, columns=['price', 'qty'])
df_ask_binance = pd.DataFrame(asks_binanace, columns=['price', 'qty'])

fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 8), dpi=80)

ax1.plot(df_bid_binance['price'], df_bid_binance['qty'], label='Binance', color='g')
ax1.fill_between(df_bid_binance['price'], df_bid_binance['qty'], color='g')

ax2.plot(df_ask_binance['price'], df_ask_binance['qty'], label='FTX', color='r')
ax2.fill_between(df_ask_binance['price'], df_ask_binance['qty'], color='r')

t = o.get_datetime_str()
ax1.set_title(f"{g.cvars['pair']} {t}\nAsk vs Qty")
ax2.set_title('Bid vs Qty')

if o.X_is_running():
    if isX:
        plt.show()
fig.savefig('images/plot_volprice.png')
