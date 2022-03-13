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
cancel = False
try:
    opts, args = getopt.getopt(argv, "-hvc", ["help", "verbose","cancel"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-v --verbose")
        print("-c --cancel (all)")
        sys.exit(0)

    if opt in ("-v", "--verbose"):
        verbose = True
    if opt in ("-c", "--cancel"):
        cancel = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

keys = o.get_secret()
exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
g.ticker_src = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 50000,
    'apiKey': keys['binance']['testnet']['key'],
    'secret': keys['binance']['testnet']['secret'],
})
g.ticker_src.set_sandbox_mode(keys['binance']['testnet']['testnet'])
if keys['binance']['testnet']['testnet']:
    b.Oprint(f" MODE:SANDBOX")


if verbose:
    g.ticker_src.verbose = True




base="ETH"
quote="BTC"
pair = f"{base}/{quote}"


print(f"OPEN ORDERD FOR {base}/{quote}")
try:
    openorders = g.ticker_src.fetch_open_orders(symbol=pair)
    for oo in openorders:
        print(f"{oo['symbol']}: {oo['side']} {oo['amount']}  @ {oo['price']} (order-id: {oo['info']['orderId']})")

    if cancel:
        for oo in openorders:
            print(f"CANCELLING: {oo['symbol']}: {oo['side']} {oo['amount']}  @ {oo['price']} (order-id: {oo['info']['orderId']})")
            cresp = g.ticker_src.cancel_order(oo['info']['orderId'],pair,{'type':oo['side']})
            print(cresp['info']['status'])
            # b.Dprint(json.dumps(cresp, indent=4))

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
