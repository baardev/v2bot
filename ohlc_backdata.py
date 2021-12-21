#!/usr/bin/python3.9
from datetime import datetime
import ccxt
import pandas as pd
# + from lib_cvars import Cvars
import lib_ohlc as o
import getopt, sys, os
import time
import lib_globals as g
import logging

g.logit = logging
g.logit.basicConfig(
    filename="/home/jw/src/jmcap/ohlc/logs/ohlc.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=o.cvars.get('logging')
)
stdout_handler = g.logit.StreamHandler(sys.stdout)

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hi:d::", ["help","index","date"])
except getopt.GetoptError as err:
    sys.exit(2)

input_filename = False
date = False
g.idx = 0
# print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-d, --date  in miliseconds")
        print("-i, --index  sequential number in series")
        sys.exit(0)

    if opt in ("-i", "--index"):
        g.idx=int(arg)
    if opt in ("-d", "--date"):
        date = int(arg)

# + g.cfgfile = "/home/jw/src/jmcap/ohlc/config_0.hcl"
# + o.cvars = Cvars(g.cfgfile)

exch = 'binance' # + initial exchange
# t_frame = '5m' # + 1-day timeframe, usually from 1-minute to 1-week depending on the exchange
t_frame = o.cvars.get('timeframe')
# symbols = ['ETH/BTC'] # + initial symbol
symbols = [o.cvars.get('pair')]
symbol = symbols[0] # + initial symbol
exchange_list = ['binance']
exch=exchange_list[0]
# + exchange_list = ['binance','bitfinex','bytetrade','ftx','kraken','poloniex','upbit','aax','bequant','bigone','bitforex',
# + 'bitz','btcalpha','coinex','crex24','digifinex','gateio','hitbtc2','huobipro','huobiru','kucoin',
# + 'lbank','okex','okex3','stex','upbit','whitebit','zb']
# + exchange_list = ['btcalpha','coinex','crex24','digifinex','gateio','hitbtc2','huobipro','huobiru','kucoin',
# + 'lbank','okex','okex3','stex','upbit','whitebit','zb']
# + Get our Exchange
try:
    exchange = getattr (ccxt, exch) ()
except AttributeError:
    print('-'*36,' ERROR ','-'*35)
    print('Exchange "{}" not found. Please check the exchange is supported.'.format(exch))
    print('-'*80)
    quit()
 
# + Check if fetching of OHLC Data is supported
if exchange.has["fetchOHLCV"] != True:
    print('-'*36,' ERROR ','-'*35)
    print('{} does not support fetching OHLC data. Please use another  exchange'.format(exch))
    print('-'*80)
    quit()
 
# + Check requested timeframe is available. If not return a helpful error.
if (not hasattr(exchange, 'timeframes')) or (t_frame not in exchange.timeframes):
    print('-'*36,' ERROR ','-'*35)
    print('The requested timeframe ({}) is not available from {}\n'.format(t_frame,exch))
    print('Available timeframes are:')
    for key in exchange.timeframes.keys():
        print('  - ' + key)
    print('-'*80)
    quit()
 
# + Check if the symbol is available on the Exchange
exchange.load_markets()
if symbol not in exchange.symbols:
    print('-'*36,' ERROR ','-'*35)
    print('The requested symbol ({}) is not available from {}\n'.format(symbol,exch))
    print('Available symbols are:')
    for key in exchange.symbols:
        print('  - ' + key)
    print('-'*80)
    quit()

if not date:
    start_date = int(datetime(2018, 1, 1, 10, 20).timestamp() * 1000)
else:
    start_date = date

def grab(**kwargs):
    start_date = kwargs['start']
    t_frame = kwargs['t']
    symbol = kwargs['sym']

    sdate =  pd.to_datetime(start_date, unit='ms')

    print(f"---{g.idx}--{start_date}-----{sdate}---------------------------------------------------")

    # + Get data
    print(symbol, t_frame, start_date)
    data = exchange.fetch_ohlcv(symbol, t_frame, since=start_date, limit=2000)


    df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['symbol'] = symbol
    df['exchange'] = exch

    ohlc = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    ohlc['Stamp'] = pd.to_datetime(ohlc['Date'], unit='ms')

    # print(ohlc)

    fromdate_ms = ohlc['Date'].iloc[0]
    todate_ms = ohlc['Date'].iloc[-1]

    print("start_date", start_date, "fromdate_ms", fromdate_ms, "todate_ms", todate_ms)

    fromdate = f"{pd.to_datetime(ohlc['Date'].iloc[0], unit='ms')}"
    todate = f"{pd.to_datetime(ohlc['Date'].iloc[-1], unit='ms')}"
    fromdate = fromdate.replace(" ", "_")
    todate = todate.replace(" ", "_")
    symbol = symbol.replace("/", "+")

    df.index = df.index / 1000  # + Timestamp is 1000 times bigger than it should be in this case
    # + df['Date'] = pd.to_datetime(df.index, unit='s')

    input_filename = f"backdata_{symbol}.{t_frame}.{fromdate}...{todate}.{len(df.index)}_{exch}_{g.idx}"

    csvfile = f"data/{input_filename}.csv"
    print(f"Saving to {csvfile}")
    df.to_csv(f"{csvfile}")

    backtestfile = f"data/{input_filename}.json"
    print(f"Saving to {backtestfile}")
    o.cvars.save(df, backtestfile)
    return todate_ms +1000

# + start wirh
# + 
# + ./ohlc_backdata.py -d 1514812800000 -i 0

sd0 = start_date
sd1 = grab(start=sd0, t=t_frame, sym=symbol)

print(sd1)

file1 = open("_backtest.tmp", "w") 
file1.write(f"{sd1}")
file1.close()
exit()

cmd = f"./ohlc_backdata.py -d {sd1} -i {g.idx+1}"

print(f"NEXT: ./ohlc_backdata.py -d {sd1} -i {g.idx+1}")
# + exit()
time.sleep(5)
os.system(cmd)
