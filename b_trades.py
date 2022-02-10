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
import hashlib

colorama_init()

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
verbose = False
cancel_order = False
nohup = False
loopct = 1

try:
    opts, args = getopt.getopt(argv, "-hnl", ["help", "nohup","loop"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-n --nohup")
        print("-l --loop")
        sys.exit(0)

    if opt in ("-n", "--nohup"):
        nohup = True
    if opt in ("-l", "--loop"):
        loopct = int(10e+10)
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if not nohup:
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

    mytrades = g.ticker_src.fetch_my_trades(symbol = "BTCUSDT",limit = 10)

    for m in mytrades:
        pf = Fore.RED if m['side'] == "buy" else Fore.GREEN
        last_trade = f"{m['order']}: {m['datetime']}: {m['side']} {m['amount']} @ {m['price']} = {o.toPrec('price',m['amount']*m['price'])}"
        if order != m['order']:
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

else:
    last_MD5 = ""
    for i in range(loopct):
        this_MD5 = md5("nohup.out")

        if this_MD5 != last_MD5:
            with open("nohup.out") as file:
                mytrades = file.readlines()

            print("---------------------------------------------------------------")
            for m in mytrades:
                pf = ""

                if m.find("CAP") != -1 or m.find("AVG") != -1:
                    if m.find("Hold") != -1:
                        pf = Fore.RED
                    if m.find("Sold") != -1:
                        pf = Fore.GREEN
                    if m.find("CAP") != -1:
                        pf = Fore.YELLOW

                    line = m.strip()
                    print(pf+f"{line}"+Style.RESET_ALL)
            last_MD5 = this_MD5
        time.sleep(3)
