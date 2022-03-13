#!/usr/bin/python -W ignore
import sys, os
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
    opts, args = getopt.getopt(argv, "-hvc", ["help", "verbose", "cancel"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-v --verbose")
        print("-c --cancel")
        sys.exit(0)

    if opt in ("-v", "--verbose"):
        verbose = True
    if opt in ("-c", "--cancel"):
        cancel_order = True
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

def get_balance(**kwargs):
    bal = False
    currency = False
    bals = {}
    try:
        currency = kwargs['currency']
    except:
        pass

    try:
        rs = g.ticker_src.fetch_balance()
        if currency:
            for c in currency:
                # print(c,rs[c])
                bals[c] = rs[c]
        else:
            bal = rs
    except Exception as e:
        print(str(e))

    return bals

try:
    balances = get_balance(currency=["BTC","USDT"])

    # print(price)


    # print(json.dumps(balances, indent=4))
    total = 0
    rtotal = 0
    tqty = 0
    fqty = 0
    uqty = 0
    dval = 0
    rval = 0
    total_sold_quote = 0

    skey = "SYM"
    stqty = "TQTY"
    sfqty = "FQTY"
    suqty = "UQTY"
    sdval = "DOLLAR"
    sprice = "LAST"
    srprice = "REL"
    squote = "QUOTE"

    print(f"{skey:<7} {stqty:<10} {sfqty:<10} {suqty:<10} {sdval:<10} {srprice:<10} {sprice:<10} {squote:<10}")
    print(f"------- ---------- ---------- ---------- ---------- ---------- ----------")

    for key in balances:
        if key == "BTC":
            price = g.ticker_src.fetch_ticker("BTC/USDT")['last']

            rprice = 0  # * for comparing trades, not market value

            if os.path.isfile("/tmp/_startprice"):
                with open('/tmp/_startprice', 'r') as infile:
                    rprice = float(infile.readline())

            tqty = o.toPrec("amount",balances[key]['total'])
            fqty = o.toPrec("amount",balances[key]['free'])
            uqty = o.toPrec("amount",balances[key]['used'])

            dval =  o.toPrec("price", tqty * price)
            rval =  o.toPrec("price", tqty * rprice)

            total += dval
            rtotal += rval
        else:
            price = 1
            rprice = 1

            tqty = o.toPrec("price",balances[key]['total'])
            fqty = o.toPrec("price",balances[key]['free'])
            uqty = o.toPrec("price",balances[key]['used'])

            dval = o.toPrec("price", tqty * price)
            rval = o.toPrec("price", tqty * rprice)

            current_price = float(b.get_ticker(g.cvars['pair'], field='close'))
            total_sold_quote =  o.toPrec("price", dval / current_price)

            total += dval
            rtotal += rval

        print(Fore.YELLOW+f"{key:<7} {tqty:<10} {fqty:<10} {uqty:<10} {dval:<10} {rval:<10} {price:<10} {total_sold_quote:<10}" + Style.RESET_ALL)


    # b.Dprint(json.dumps(balances['total'], indent=4))
    print(Fore.GREEN+f"TOT:                                     { o.toPrec('price',total):<10} { o.toPrec('price',rtotal):<10}" + Style.RESET_ALL)

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
