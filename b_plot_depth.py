#!/usr/bin/python

import getopt
import sys

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import toml

import lib_v2_globals as g
import lib_v2_ohlc as o

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
src = "live"
pair = "BTCUSDT"
isX = False
try:
    opts, args = getopt.getopt(argv, "-hp:lX", ["help", "pair=", 'live', 'isX'])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-p --pair def:BTCBUSD")
        print("-l --live def:test")
        print("-X, --isX (has X11 def=False)")
        sys.exit(0)

    if opt in ("-p", "--pair"):
        pair = arg

    if opt in ("-l", "--live"):
        src = "live"

    if opt in ("-X", "--isX"):
        isX = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡


g.cvars = toml.load(g.cfgfile)

fig, ax = plt.subplots()

# if src == "live":
#     srcurl = "https://api.binance.com"
# else:
#     srcurl = "https://testnet.binance.vision"

srcurl = "https://api.binance.com"

r = requests.get(f"{srcurl}/api/v3/depth", params=dict(symbol=pair))
results = r.json()

frames = {side: pd.DataFrame(data=results[side], columns=["price", "quantity"], dtype=float) for side in
          ["bids", "asks"]}
frames_list = [frames[side].assign(side=side) for side in frames]
data = pd.concat(frames_list, axis="index", ignore_index=True, sort=True)

price_summary = data.groupby("side").price.describe()
price_summary.to_markdown()

r = requests.get(f"{srcurl}/api/v3/ticker/bookTicker", params=dict(symbol=pair))
# r = requests.get("https://api.binance.com/api/v3/ticker/bookTicker", params=dict(symbol=pair))
book_top = r.json()

name = book_top.pop("symbol")  # get symbol and also delete at the same time
s = pd.Series(book_top, name=name, dtype=float)
s.to_markdown()

ax.clear()

t = o.get_datetime_str()
ax.set_title(f"{pair} {src} {t}")

sns.ecdfplot(x="price", weights="quantity", stat="count", complementary=True, data=frames["bids"], ax=ax)
sns.ecdfplot(x="price", weights="quantity", stat="count", data=frames["asks"], ax=ax)
sns.scatterplot(x="price", y="quantity", hue="side", data=data, ax=ax)

ax.set_xlabel("Price")
ax.set_ylabel("Quantity")

if o.X_is_running():
    if isX:
        plt.show()
fig.savefig('images/plot_depth.png')
