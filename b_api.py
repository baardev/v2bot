#!/usr/bin/env python
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

keys = o.get_secret(provider='binance', apitype='testnet')
exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
g.ticker_src = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 50000,
    'apiKey': keys['key'],
    'secret': keys['secret'],
})
g.ticker_src.set_sandbox_mode(keys['testnet'])
if keys['testnet']:
    b.Oprint(f" MODE:SANDBOX")

if verbose:
    g.ticker_src.verbose = True




# base="BNB"
# to_buy_amt=1.0
# to_sell_amt=1.0

to_buy_amt = 0.31
to_sell_amt = 0.01

base="BTC"
quote="USDT"
pair = f"{base}/{quote}"


try:
    markets = g.ticker_src.load_markets()
    # b.Dprint(json.dumps(markets, indent=4))
    balances = b.get_balance()
    # b.Dprint(json.dumps(balances, indent=4))
    openorders = g.ticker_src.fetch_open_orders(symbol=pair)
    # b.Dprint(json.dumps(openorders, indent=4))
    tradehist = g.ticker_src.fetch_trades(pair)
    # b.Dprint(json.dumps(tradehist, indent=4))

    test_buy_amount = g.ticker_src.amount_to_precision(pair, to_buy_amt)
    test_sell_amount = g.ticker_src.amount_to_precision(pair, to_sell_amt)

    # = ************************************************************************
    b.Oprint(f"1) OPENING BAL {b.get_balance(base=base)['free']}")
    # = ************************************************************************
    b.Oprint(f"2) BUY {test_buy_amount} {base}")
    resp = b.market_order(symbol=pair,type="market",side="buy",amount=test_buy_amount)
    if verbose:
        b.Dprint(json.dumps(resp,indent=4))
    if resp['status'] != 0:
        b.Eprint("ERROR")
        b.Eprint(f"CURRENT BALANCE: [{b.get_balance(base=base)['free']}]")
        b.Eprint(json.dumps(resp,indent=4))
    # = ************************************************************************
    b.Oprint(f"3) NEW BAL {b.get_balance(base=base)['free']}")
    # = ************************************************************************
    b.Oprint(f"4) SELL {test_sell_amount} {base}")
    resp = b.market_order(symbol=pair,type="market",side="sell",amount=test_sell_amount)
    if verbose:
        b.Dprint(json.dumps(resp,indent=4))
    if resp['status'] != 0:
        b.Eprint("ERROR")
        b.Eprint(json.dumps(resp,indent=4))
        exit(1)
    # = ************************************************************************
    total_base_holding = float(g.ticker_src.amount_to_precision(pair,b.get_balance(base=base)['free']))
    b.Oprint(f"5) SELL ALL [{total_base_holding}] {base}")
    resp = b.close_all(pair, total_base_holding)
    if verbose:
        b.Dprint(json.dumps(resp,indent=4))
    if resp['status'] != 0:
        b.Eprint("ERROR")
        b.Eprint(json.dumps(resp,indent=4))
    # = ************************************************************************
    b.Oprint(f"6) NEW BAL {b.get_balance(base=base)['free']}")

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
