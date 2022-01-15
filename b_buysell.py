#!/usr/bin/python -W ignore
import sys
import getopt
import json
import toml
import ccxt
import lib_v2_globals as g
import lib_v2_ohlc as o
import lib_v2_binance as b

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
verbose = False
side = False
qty = False
base = False
quote = False

try:
    opts, args = getopt.getopt(argv, "-hs:a:b:q:", ["help", "side=","amt=","base=","quote="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-v --verbose")
        sys.exit(0)

    if opt in ("-s", "--side"):
        side = arg
    if opt in ("-a", "--amt"):
        amount = float(arg)
    if opt in ("-b", "--base"):
        base = arg
    if opt in ("-q", "--quote"):
        quote = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

if not side or not amount or not base or not quote:
    print("missing SIDE or AMOUNT or BASE or QUOTE")
    print("-s --side  'buy'|'sell'")
    print("-a --amt  <amount in base>")
    print("-b --base  <base>")
    print("-q -quote  <quote>")
    print("EX: ./b_buysell.py -s sell -a 1 -b BTC -q USDT")
    exit()

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

# if verbose:
#     g.ticker_src.verbose = True




# base="BNB"
# to_buy_amt=1.0
# to_sell_amt=1.0

to_buy_amt = 0.31
to_sell_amt = 0.01

pair = f"{base}/{quote}"


try:
    b.Oprint(f"4) {side} {amount} {base} to {quote}")
    resp = b.market_order(symbol=pair,type="market",side=side,amount=amount)
    if resp['status'] != 0:
        b.Eprint("ERROR")
        b.Eprint(json.dumps(resp,indent=4))
        exit(1)
    else:
        print("----------\nBALANCES\n-----------")
        balances = b.get_balance()
        b.Dprint(json.dumps(balances['total'], indent = 4))


except ccxt.DDoSProtection as e:
    print(type(e).__name__, e.args, 'DDoS Protection (ignoring)')
except ccxt.RequestTimeout as e:
    print(type(e).__name__, e.args, 'Request Timeout (ignoring)')
except ccxt.ExchangeNotAvailable as e:
    print(type(e).__name__, e.args, 'Exchange Not Available due to downtime or maintenance (ignoring)')
except ccxt.AuthenticationError as e:
    print(type(e).__name__, e.args, 'Authentication Error (missing API keys, ignoring)')
except ccxt.ExchangeError as e:
    print(type(e).__name__, e.args, 'Loading markets failed')
