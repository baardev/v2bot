import lib_v2_globals as g
import lib_v2_ohlc as o
from pprint import pprint

import lib_v2_ohlc
from colorama import init as colorama_init
from colorama import Fore, Back, Style

colorama_init()

# params = {
#     'quoteOrderQty': amount,
# }

def market_order(**kwargs):
    symbol = False
    amount = False
    side = False
    # ================
    try:
        side = kwargs['side']
    except:
        print("Missing 'side'")
        exit(1)
    # ================
    try:
        symbol = kwargs['symbol']
    except:
        print("Missing 'symbol'")
        exit(1)
    # ================
    try:
        amount = kwargs['amount']
    except:
        print("Missing 'amount'")
        exit(1)
    # ================

    symbol = symbol.replace("/","")
    params = {}
    # params = {'reduceOnly': 'false'} # reduceOnly orders are supported for futures and perpetuals only
    # ! params doc -> https://python-binance.readthedocs.io/en/latest/binance.html

    this_order = "no action taken"
    resp = {'return': this_order}

    try:
        if side == "sell":
            this_order = g.ticker_src.create_market_sell_order(symbol, amount, params)
        if side == "buy":
            this_order = g.ticker_src.create_market_buy_order(symbol, amount, params)
        resp["return"] = this_order
        resp["status"] = 0
    except Exception as e:
        resp["return"] = str(e)
        resp["status"] = 1

    return resp

def close_all(symbol,amount):
    symbol = symbol.replace("/", "")
    return market_order(symbol=symbol,side="sell",amount=amount)

def get_balance(**kwargs):
    bal = False
    base = False
    try:
        base = kwargs['base']
    except:
        pass

    try:
        rs = g.ticker_src.fetch_balance()
        if base:
            bal = rs[base]
        else:
            bal = rs
    except Exception as e:
        print(str(e))

    return bal

def get_orderbook(symbol):
    symbol = symbol.replace("/","")
    orderbook =  g.ticker_src.fetch_order_book(symbol)
    return orderbook

def Oprint(msg):
    print(Fore.GREEN + msg + Style.RESET_ALL)

def Eprint(msg):
    print(Fore.RED + msg + Style.RESET_ALL)

def Dprint(msg):
    print(Fore.YELLOW + msg + Style.RESET_ALL)
