#!/usr/bin/python -W ignore
import sys, os, time
import getopt
import json
import toml
import ccxt
import lib_v2_globals as g
import lib_v2_ohlc as o
import lib_v2_binance as b
from colorama import Fore, Style
from colorama import init as colorama_init

colorama_init()

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
verbose = False
cancel_order = False
try:
    opts, args = getopt.getopt(argv, "-hv", ["help", "verbose"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-v --verbose")
        sys.exit(0)

    if opt in ("-v", "--verbose"):
        verbose = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)

g.keys = o.get_secret()
g.ticker_src = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 50000,
    'apiKey': g.keys['binance']['testnet']['key'],
    'secret': g.keys['binance']['testnet']['secret'],
})

g.ticker_src.set_sandbox_mode(g.keys['binance']['testnet']['testnet'])
if g.keys['binance']['testnet']['testnet']:
    b.Oprint(f" MODE:SANDBOX")

if verbose:
    g.ticker_src.verbose = True

order = 0
ct = 0
while True:
    try:
        mytrades = g.ticker_src.fetch_my_trades(symbol = "BTCUSDT",limit = 1)
    except Exception as e:
        print(e)
        continue

    last_trade = False

    selltrades = []
    lp = 0

    # print(json.dumps(mytrades,indent=4))
    m = mytrades[0]
    pf = Fore.RED if m['side'] == "buy" else Fore.GREEN
    last_trade = f"{m['order']}: {m['side']} {m['amount']} @ {m['price']} = {o.toPrec('price',m['amount']*m['price'])}"
    if order != m['order']:
        if ct > 0:
            print(pf + f"{last_trade}"+Style.RESET_ALL)

        openorders = g.ticker_src.fetch_open_orders(symbol=g.cvars['pair'])
        for oo in openorders:
            t = oo['type']
            p = oo['price']
            s = oo['stopPrice']
            i = oo['side']
            a = oo['amount']
            d = oo['id']

            oostr = f"\t{t} {i} {a} @ {p} ({d})"
            b.Iprint(oostr)



    time.sleep(3)
    order = m['order']
    ct += 1
