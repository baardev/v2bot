#!/usr/bin/python
import gc
import getopt
import logging
import os
import sys, json
import time
import shutil
from datetime import datetime
from pathlib import Path

import ccxt
import pandas as pd
import toml
from colorama import Fore, Style, Back
from colorama import init as colorama_init
import importlib
import lib_v2_globals as g
import lib_v2_ohlc as o
import lib_v2_binance as b

g.DD0 = False

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
g.autoclear = True
g.datatype = "backtest"
g.showeach = False
g.showdates = False
autoyes = False
runcfg = False
dynamic_load = False
g.runlevel = 0

try:
    opts, args = getopt.getopt(argv, "-h ndeyD c:L:C:p:",
                               [
                                    "help",
                                    "nohead",
                                    "dates",
                                    "each",
                                    "auto yes",
                                    "dynamic",
                                    "cfgfile=",
                                    "runlevel=",
                                    "counterpos=",
                                    "prevcoverprice=",
                               ])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-n, --nohead")
        print("-d, --dates")
        print("-e, --each")
        print("-y, --auto yes")
        print("-D, --dynamic")
        print("-c, --cfgfile")
        print("-L, --runlevel")
        print("-C, --counterpos")
        print("-p, --prevcoverprice")
        sys.exit(0)


    if opt in ("-n", "--nohead"):
        g.headless = True

    if opt in ("-d", "--dates"):
        g.showdates = True

    if opt in ("-e", "--each"):
        g.showeach = True

    if opt in ("-y", "--autoyes"):
        autoyes = True

    if opt in ("-D", "--dynamic"):
        dynamic_load = True

    if opt in ("-L", "--runlevel"):
        g.runlevel = int(arg)

    if opt in ("-c", "--cfgfile"):
        g.cfgfile = arg
        g.cvars = toml.load(g.cfgfile)
        g.datatype = g.cvars["datatype"]
        if g.runlevel == 0:
            print(f"USING CONFIG: [{g.cfgfile}]")
    else:
        g.cfgfile = "config.toml"
        g.cvars = toml.load(g.cfgfile)

    g.cdata = toml.load(f"C_data_{str(g.cvars['pair']).replace('/','')}.toml")

    if opt in ("-C", "--counterpos"):
        # if g.runlevel > 0:
        g.counterpos = int(arg)
        g.gcounter += g.counterpos


    if opt in ("-p", "--prevcoverprice"):
        if g.runlevel > 0:
            g.saved_coverprice = float(arg)
            o.write_val_to_file(g.saved_coverprice, f"_next_sell_price{g.runlevel-1}")
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
# * create glogal state array
g.state = {}

# * check for/set session name
o.state_wr("session_name", o.get_sessioname())
g.tmpdir = f"/tmp/{g.session_name}"
if o.isfile("_last_sell"):
    o.deletefile("_last_sell")
# print(f"checking {g.tmpdir}")
# if g.runlevel == 0:
#     if os.path.isdir(g.tmpdir):
#         # print(f"exists... deleting")
#         print(f"rmdir {g.tmpdir}")
#         os.system(f"rm -rf {g.tmpdir}")
#     print(f"mkdir {g.tmpdir}")
#     os.mkdir(g.tmpdir)

if o.isfile("_sess_tot"):
    g.sess_tot = float(o.read_val_from_file("_sess_tot"))
else:
    o.write_val_to_file(0,"_sess_tot")

if not g.headless:
    g.display = g.cvars['display']
    g.headless = g.cvars['headless']
else:
    g.display = False

g.show_textbox = g.cvars["show_textbox"]
g.tm = g.cvars['trademodel_version']

try:
    import matplotlib

    matplotlib.use("Qt5agg")
    import matplotlib.animation as animation
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure
    # from matplotlib.gridspec import GridSpec
    import lib_v2_listener as kb
    import matplotlib.patches as mpatches
    import matplotlib.dates as mdates


    g.headless = False
except:
    # * assume this is headless if we end up here as the abive requires a GUI
    g.headless = True

# * this needs to load first
colorama_init(strip=False, autoreset=False)
pd.set_option('display.max_columns', None)
# g.verbose = g.cvars['verbose']


# * ccxt doesn't yet support Coinbase ohlcv data, so CB and binance charts will be a little off
g.keys = o.get_secret()
g.ticker_src = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 50000,
    'apiKey': g.keys['binance']['testnet']['key'],
    'secret': g.keys['binance']['testnet']['secret'],
})
g.ticker_src.set_sandbox_mode(g.keys['binance']['testnet']['testnet'])

# * load market/fees for precision parameters
# * need this even if offline for precision function in ccxt for binance
try:
    g.ticker_src.load_markets()
except:
    pass
g.spot_src = g.ticker_src

g.dbc, g.cursor = o.getdbconn()

# * adjust startdate so that the listed startdate is the last date in the df array
if g.datatype == "backtest":
    # g.startdate = o.adj_startdate(g.cvars['startdate'])
    g.startdate = o.adj_startdate(g.cvars['startdate'])

    # print(g.startdate)
# exit()
g.datawindow = g.cvars["datawindow"]

g.logit = logging
g.logit.basicConfig(
    filename="logs/ohlc.log",
    filemode='w',
    format='%(asctime)s - %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=g.cvars['logging']
)
stdout_handler = g.logit.StreamHandler(sys.stdout)

# * create the global buy/sell and all_records dataframes
columns = ['Timestamp', 'buy', 'mclr', 'sell', 'qty', 'subtot', 'tot', 'pnl', 'pct']
g.df_buysell = pd.DataFrame(index=range(g.cvars['datawindow']), columns=columns)
g.df_buysell.index = pd.DatetimeIndex(pd.to_datetime(g.df_buysell['Timestamp'], unit=g.units))
g.df_buysell.index.rename("index", inplace=True)

# * Load the ETH data and BTC data for price conversions
g.interval = 1

if g.datatype == "backtest":
    # o.get_priceconversion_data()
    o.get_bigdata()

# if g.cvars["convert_price"]:
#     o.convert_price()

# * arrays that need to exist from the start, but can;t be in globals as we need g.cvars to exist first

g.mav_ary[0] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[1] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[2] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[3] = [None for i in range(g.cvars['datawindow'])]

g.dstot_ary = [0 for i in range(g.cvars['datawindow'])]
g.dstot_lo_ary = [0 for i in range(g.cvars['datawindow'])]
g.dstot_hi_ary = [0 for i in range(g.cvars['datawindow'])]


if g.datatype == "live":
    g.interval = g.cvars['live']['interval']






if g.autoclear:  # * automatically clear all (default)
    o.clearstate()
    o.state_wr('isnewrun', True)
    # g.gcounter = 0

if g.cvars['log_mysql']:
    o.sqlex(f"SET GLOBAL general_log = 'ON'")
else:
    o.sqlex(f"SET GLOBAL general_log = 'OFF'")

# * these vars are loaded into mem as they (might) change during runtime
# g.interval          = g.cvars["interval"]
g.buy_fee = g.cvars['buy_fee']
g.sell_fee = g.cvars['sell_fee']
g.ffmaps_lothresh = g.cvars['ffmaps_lothresh']
g.ffmaps_hithresh = g.cvars['ffmaps_hithresh']
g.sigffdeltahi_lim = g.cvars['sigffdeltahi_lim']
g.dstot_buy = g.cvars["dstot_buy"]
g.sell_count = 0
g.buy_count = 0
g.issue = o.get_issue()

g.BASE = g.cvars['pair'].split("/")[0]
g.QUOTE = g.cvars['pair'].split("/")[1]

g.bsuid = 0
g.reserve_seed          = o.get_cdata_val(g.cdata["rseed"], default=g.cvars[g.datatype]['reserve_seed'])
g.maxbuys               = o.get_cdata_val(g.cdata["maxbuys"],  default=g.cvars['maxbuys'])
g.mult                  = o.get_cdata_val(g.cdata["mult"],     default=g.cvars[g.datatype]['purch_mult'])
g.next_buy_increments   = o.get_cdata_val(g.cdata["intval"],   default=g.cvars[g.datatype]['next_buy_increments'])
# g.initial_purch_qty     = o.get_cdata_val(g.cdata["pqty"],   default=o.get_purch_qty(g.reserve_seed))
g.initial_purch_qty = g.cdata["pqty"][0]

# print("g.initial_purch_qty:",g.initial_purch_qty)

if g.cvars['testnet'] and not g.cvars['offline']:
    try:
        balances = b.get_balance()

        bal = balances[g.QUOTE]['free']
        tic = b.get_ticker(g.cvars['pair'],field='close')
        # print(f"[{bal}],[{tic}]")
        g.reserve_seed = o.toPrec("amount",bal/tic)
        print(f"reserve_seed now = [{g.reserve_seed}]")
        # g.initial_ 0n = o.get_purch_qty(g.reserve_seed)
        print(f"purch_qty now = [{g.initial_purch_qty}]")

        o.set_opening_price(bal)
        # g.opening_price = float(o.read_val_from_file("_opening_price", default=bal))
        # print(f"OPENING BALANCE (from _opeining_price): {g.QUOTE}: {g.opening_price}")

    except:
        print("Error connecting to Binance... exiting")
        exit()
else:
    g.opening_price = 0

_margin_x = g.cvars[g.datatype]['margin_x']
g.capital = g.reserve_seed * _margin_x
g.cwd = os.getcwd().split("/")[-1:][0]
g.cap_seed = g.reserve_seed

if g.datatype == "stream":
    streamfile = o.resolve_streamfile()
    if os.path.isfile(streamfile):
        os.remove(streamfile) #!!! JWFIX CHECK
else:
    streamfile = False

if str(g.cvars[g.datatype]['testpair'][0]).find("perf") != -1:
    # = JWFIX g.pfile = f"data/perf3_{g.cvars['perf_bits']}_{g.BASE}{g.QUOTE}_{g.cvars[g.datatype]['timeframe']}_{g.cvars['perf_filter']}f.json"
    g.pfile = f"data/perf{g.tm}_{g.cvars['perf_bits']}_{g.BASE}{g.QUOTE}_{g.cvars[g.datatype]['timeframe']}_0f.json"

    # ! not needed for perf5
    # try:
    #     print(f"LOADING: [data/_perf{g.tm}.json]")
    #     f = open(f"data/_perf{g.tm}.json", )
    #     g.rootperf[g.tm] = json.load(f)
    #
    # except Exception as e:
    #     print(f"ERROR trying to load performance data file [data/_perf{g.tm}.json]: {e}")
    #     # exit()


# * get screens and axes
try:
    fig, fig2, ax = o.make_screens(figure)
except:
    fig = False
    fig2 = False
    ax = [0, 0, 0, 0, 0, 0]

# * Start the listner threads and join them so the script doesn't end early
# * This needs X-11, so if no display, no listener
if g.display:
    kb.keyboard_listener.start()

# ! https://pynput.readthedocs.io/en/latest/keyboard.html
# ! WARNING! This listens GLOBALLY, on all windows, so be careful not to use these keys ANYWHERE ELSE
if g.runlevel == 0:
    print(Fore.MAGENTA + Style.BRIGHT)
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"           {g.session_name}            ")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    print("┃ Alt + Arrow Down : Display Toggle    ┃")
    print("┃ Alt + Delete     : Textbox Toggle    ┃")
    print("┃ Alt + Arrow Up   :                   ┃")
    print("┃ Alt + End        : Shutdown          ┃")
    print("┃ Alt + Home       : Verbose/Quiet     ┃")
    print("┃ Alt + b          : Buy signal        ┃")
    print("┃ Alt + s          : Sell signal       ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    o.cclr()
# else:
#     print(Fore.MAGENTA + Style.BRIGHT)
#     print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
#     print(f"  LEVEL 1: {g.session_name}            ")
#     print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
#     o.cclr()

# * ready to go, but launch only on boundry if live
if g.datatype == "live":
    bt = g.cvars['live']['load_on_boundary']
    if not g.epoch_boundry_ready:
        while o.is_epoch_boundry(bt) != 0:
            print(f"{bt - g.epoch_boundry_countdown} waiting for epoch boundry ({bt})", end="\r")
            time.sleep(1)
        g.epoch_boundry_ready = True
        # * we found the boundry, but now need to wait for teh data to get loaded and updated from the provider
        print(f"{g.cvars['live']['boundary_load_delay']} sec. latency pause...")
        time.sleep(g.cvars['live']['boundary_load_delay'])

print(Fore.YELLOW + Style.BRIGHT)
a = Fore.YELLOW + Style.BRIGHT
c = Fore.CYAN + Style.BRIGHT
e = Style.RESET_ALL

if g.runlevel == 0:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"           CURRENT PARAMS             ")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    if g.datatype == "stream":
        print(f"{a}WSS Datafile:    {c}{o.resolve_streamfile()}{e}")

    if str(g.cvars[g.datatype]['testpair'][0]).find("perf") != -1:
        print(f"{a}Perfbit file:    {c}{g.pfile}{e}")

    # print(f"{a}Display:         {c}{g.display}{e}")
    # print(f"{a}Save:            {c}{g.cvars['save']}{e}")
    # print(f"{a}MySQL log:       {c}{g.cvars['log_mysql']}{e}")
    # print(f"{a}Log to file:     {c}{g.cvars['log2file']}{e}")
    # print(f"{a}Textbox:         {c}{g.show_textbox}{e}")
    # print("")
    # print(f"{a}Testnet:         {c}{g.cvars['testnet']}{e}")
    # print(f"{a}Offline:         {c}{g.cvars['offline']}{e}")
    # print("")
    print(f"{a}Datatype:        {c}{g.datatype}{e}")
    print(f"{a}Capital:         {c}{g.capital}{e}")
    print(f"{a}purch:           {c}{g.initial_purch_qty}{e}")
    print(f"{a}Nextbuy inc.:    {c}{g.next_buy_increments}{e}")
    print(f"{a}Testpair:        {c}{g.cvars[g.datatype]['testpair']}{e}")
    print(f"{a}Loop interval:   {c}{g.interval}ms ({g.interval / 1000}{e})")
    print(f"{a}Res. seed:       {c}{g.reserve_seed}{e}")
    print(f"{a}Margin:          {c}{g.cvars[g.datatype]['margin_x']}{e}")
    print("")
    if g.datatype == "backtest":
        print(f"{a}datafile:       {c}{g.cvars['backtestfile']}{e}")
        print(f"{a}Start date:     {c}{g.cvars['startdate']}{e}")
        print(f"{a}End date:       {c}{g.cvars['enddate']}{e}")
    o.cclr()

    if sys.stdout.isatty():
        if not autoyes:
            o.waitfor("OK?")
    else:
        print("No TTY... assuming 'OK'")

# * mainly for textbox formatting
if g.display:
    plt.rcParams['font.family'] = 'monospace'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['mathtext.default'] = 'regular'

props = dict(boxstyle='round', pad=1, facecolor='black', alpha=1.0)

g.now_time = o.get_now()
g.last_time = o.get_now()
g.sub_now_time = o.get_now()
g.sub_last_time = o.get_now()

#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    LOOP    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓


o.botmsg("Starting New Run...")
# print(f"Runlevel = {g.runlevel}/{g.counterpos}")
o.DDp(f" >>>> ─────────────────────────────────────────────────────────────────────────────────────── [{g.runlevel}] ─────", tabs = False)


def animate(k):
    working(k)

def working(k):

    # if g.runlevel == 0:
    if o.isfile(f"_counterpos{g.runlevel}"):
        g.gcounter = int(o.read_val_from_file(f"_counterpos{g.runlevel}"))
        # g.counterpos = int(o.read_val_from_file("/tmp/_counterpos"))
        # print(f"?????bef  g,gcounter = {g.gcounter} + {g.counterpos}")
        # g.gcounter += g.counterpos
        if g.DD0:
            o.DDp(f"━━━━━━━━━━━━━━>>> L{g.runlevel} g.gcounter = {g.gcounter}")
        os.remove(f"{g.tmpdir}/_counterpos{g.runlevel}")

    if dynamic_load:
        mod = sys.modules.get('lib_v2_ohlc')
        importlib.reload(mod)


    if o.isfile(f"XSELL{g.runlevel}"):
        # print(f"SELLING LEVEL-{g.runlevel}- FOUND XSELL{g.runlevel}")
        if g.DD0:
            o.DDp(f">┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            o.DDp(f">┃(v2) TURNING ON g.external_sell_signal ")
            o.DDp(f">┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        g.external_sell_signal = True
        o.deletefile(f"XSELL{g.runlevel}")
        # print(f"ERXTERAL SELL SIGNAH = {g.external_sell_signal}")
    else:
        g.external_sell_signal = False  # * turn off external sell signal


    if o.isfile(f"XBUY{g.runlevel}"):
        g.external_buy_signal = True
        o.deletefile(f"XBUY{g.runlevel}")

    # * reload cfg file - alows for dynamic changes during runtime
    g.cvars = toml.load(g.cfgfile)
    g.cdata = toml.load(f"C_data_{str(g.cvars['pair']).replace('/','')}.toml")

    # if g.gcounter == 0:
    #     o.set_opening_price()    g.opening_price = g.ohlc.iloc[0]['Close']

    try:
        g.cursor.execute("SET AUTOCOMMIT = 1")
    except:
        # * problem with server, flag to restart at 0 seconds
        o.restart_db()

    g.logit.basicConfig(level=g.cvars['logging'])
    this_logger = g.logit.getLogger()
    if g.verbose:
        this_logger.addHandler(stdout_handler)
    else:
        this_logger.removeHandler(stdout_handler)
    if g.time_to_die:
        exit(0)

    g.gcounter = g.gcounter + 1
    o.state_wr('gcounter', g.gcounter)
    g.datasetname = g.cvars["backtestfile"] if g.datatype == "backtest" else "LIVE"
    _since = g.cvars[g.datatype]['since']
    t = o.Times(_since)
    # * Title of ax window
    _testpair = g.cvars[g.datatype]['testpair']
    add_title = f"{g.cwd}/[{_testpair[0]}]-[{_testpair[1]}]:{g.cvars['datawindow']}]"

    # g.reserve_seed = o.read_val_from_file("_rseed", default=g.cvars[g.datatype]['reserve_seed'])
    # g.maxbuys = o.read_val_from_file("_maxbuys", default=g.cvars['maxbuys'])
    # g.mult = o.read_val_from_file("_mult", default=g.cvars[g.datatype]['purch_mult'])
    # g.next_buy_increments = o.read_val_from_file("_intval", default=g.cvars[g.datatype]['next_buy_increments'])

    g.reserve_seed = o.get_cdata_val(g.cdata["rseed"], default=g.cvars[g.datatype]['reserve_seed'])
    g.maxbuys = o.get_cdata_val(g.cdata["maxbuys"], default=g.cvars['maxbuys'])
    g.mult = o.get_cdata_val(g.cdata["mult"], default=g.cvars[g.datatype]['purch_mult'])
    g.next_buy_increments = o.get_cdata_val(g.cdata["intval"], default=g.cvars[g.datatype]['next_buy_increments'])
    # g.initial_purch_qty = o.get_cdata_val(g.cdata["pqty"], default=o.get_purch_qty(g.reserve_seed))
    g.initial_purch_qty = g.cdata["pqty"][0]

    g.cfile_states_str = f"rseed:[{g.reserve_seed}]  maxbuys:[{g.maxbuys}]  mult:[{g.mult}]  intval:[{g.next_buy_increments}]  pqty:[{g.initial_purch_qty}] "

    _margin_x = g.cvars[g.datatype]['margin_x']
    padj = (1 + float(o.read_val_from_file(f"_pct{g.runlevel}", default=0)))
    # padj = 1
    g.reserve_cap = (g.reserve_seed * padj) * _margin_x


    # * track the number of short buys
    if g.short_buys > 0:
        g.since_short_buy += 1

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + get the source data as a dataframe
    # + ───────────────────────────────────────────────────────────────────────────────────────
    # ! JWFIX need to put this in an error-checking loop

    if not o.load_data(t):
        exit(1)

    g.mmphi = float(g.ohlc['Close'].min() + ((g.ohlc['Close'].max() - g.ohlc['Close'].min()) * 0.618))

    # if g.showdates:
    #     sdate = f"{g.ohlc['Date'].iloc[-1]}"
    #     if g.showeach:
    #         end = "\n"
    #     else:
    #         end = "\r"
    #     print(f"{sdate}",end=end)

    g.total_reserve = (g.capital * g.this_close)

    # * just used in debugging to stop at some date
    if g.datatype == "backtest":
        enddate = datetime.strptime(g.cvars['enddate'], "%Y-%m-%d %H:%M:%S")
        if g.ohlc['Date'][-1] > enddate and g.datatype == "backtest":
            print(f"Reached endate of {enddate}")
            exit()

    # * Make frame title
    if g.display:
        ft = o.make_title()
        fig.suptitle(ft, color='white')

        # if g.cvars["convert_price"]:
        #     ax[0].set_ylabel("Asset Value (in $USD)", color='white')
        # else:
        ax[0].set_ylabel("Asset Value (in BTC)", color='white')

    # ! ───────────────────────────────────────────────────────────────────────────────────────
    # ! CHECK THE SIZE OF THE DATAFRAME and Gracefully exit on error or command
    # ! ───────────────────────────────────────────────────────────────────────────────────────
    if g.datatype == "backtest":
        if len(g.ohlc.index) != g.cvars['datawindow']:
            if not g.time_to_die:
                if g.batchmode:
                    exit(0)
                else:
                    print(f"datawindow: [{g.cvars['datawindow']}] != index: [{[{len(g.ohlc.index)}]}])")
                    o.waitfor("End of data (or some catastrophic error)... press enter to exit")
            else:
                print("Goodbye")
            exit(0)

    # # + ───────────────────────────────────────────────────────────────────────────────────────
    # # + make the data, add to dataframe !! ORDER IS IMPORTANT
    # # + ───────────────────────────────────────────────────────────────────────────────────────
    o.threadit(o.make_lowerclose(g.ohlc)).run()  # * make EMA of close down by n%
    o.threadit(o.make_mavs(g.ohlc)).run()  # * make series of MAVs
    #!! o.make_allavg(g.ohlc)  # * make inverted Close
    #!! o.make_rohlc(g.ohlc)  # * make inverted Close
    #!! o.make_sigffmb(g.ohlc)  # * make 6 band passes of org
    #!! o.make_sigffmb(g.ohlc, inverted=True)  # * make 6 band passes of inverted
    #!! o.make_ffmaps(g.ohlc)  # * find the delta of both
    #!! o.make_dstot(g.ohlc)  # * cum sum of slopes of each band

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + update some values based on current data
    # + ───────────────────────────────────────────────────────────────────────────────────────
    bull_bear_limit = 1 #* index of the mav[] array
    if g.ohlc.iloc[-1]['Close'] > g.ohlc.iloc[-1][f'MAV{bull_bear_limit}']:
        g.market = "bull"
        _lowerclose_pct_bull = g.cvars[g.datatype]['lowerclose_pct_bull']
        g.lowerclose_pct = _lowerclose_pct_bull
    else:
        g.market = "bear"
        _lowerclose_pct_bear = g.cvars[g.datatype]['lowerclose_pct_bear']
        g.lowerclose_pct = _lowerclose_pct_bear

    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    TRIGGER    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    rem_cd = g.cooldown - g.gcounter if g.cooldown - g.gcounter > 0 else 0

    # * clear all the plots and patches
    if g.display:
        o.rebuild_ax(ax)

        ax[0].set_title(f"{add_title} - ({o.get_latest_time(g.ohlc)}-{t.current.second})", color='white')

        # * Make text box

        pretty_nextbuy = "N/A" if g.next_buy_price > 100000 else f"{g.next_buy_price:6.2f}"
        next_buy_pct = (g.next_buy_increments * o.state_r('curr_run_ct')) * 100

        if g.show_textbox:
            textstr = f'''
g.gcounter:           {g.gcounter}
g.curr_run_ct:        {g.curr_run_ct}

g.long_buys           {g.long_buys}
g.reserve_cap         {g.reserve_cap}
g.purch_qty           {g.purch_qty}

g.initial_purch_qty   {g.initial_purch_qty}
g.reserve_seed        {g.reserve_seed}
g.maxbuys:            {g.maxbuys}
g.mult                {g.mult}
g.next_buy_increments {g.next_buy_increments}

<{g.coverprice:6.2f}> <{g.ohlc['Close'][-1]:6.2f}> <{pretty_nextbuy}> ({next_buy_pct:2.1f}%)
'''


# Buys long/short:    {g.long_buys}/{g.short_buys}
# Cap. Raised: ({g.BASE})  {g.capital - (_reserve_seed * _margin_x)}
# Tot Capital: ({g.BASE})  {g.capital}
# Cap. Raised %:      {g.pct_cap_return * 100}
# Seed Cap. Raised %: {g.pct_capseed_return * 100}
# Tot Reserves:      ${g.total_reserve}
# Tot Seed:          ${_reserve_seed * g.this_close}
# Net Profit:        ${g.running_total}
# Covercost:         ${g.adjusted_covercost}
# MX int/tot:        ${g.margin_interest_cost}/${g.total_margin_interest_cost}



            ax[1].text(
                    0.05,
                    0.9,
                    # 0,
                    # 0,
                    textstr,
                    transform=ax[1].transAxes,
                    color='wheat',
                    fontsize=10,
                    verticalalignment='top',
                    horizontalalignment='left',
                    # verticalalignment='center',
                    # horizontalalignment='center',
                    bbox=props
            )
        plt.rcParams['legend.loc'] = 'best'

        # * plot everything
        # # * panel 0
        #= o.threadit(o.plot_close(g.ohlc, ax=ax, panel=0, patches=g.ax_patches)).run()
        #= o.threadit(o.plot_mavs(g.ohlc, ax=ax, panel=0, patches=g.ax_patches)).run()
        #= o.threadit(o.plot_lowerclose(g.ohlc, ax=ax, panel=0, patches=g.ax_patches)).run()
        # # # * panel 1
        #= o.threadit(o.plot_dstot(g.ohlc, ax=ax, panel=1, patches=g.ax_patches)).run()

        # # * panel 0
        o.plot_close(g.ohlc,        ax=ax, panel=0, patches=g.ax_patches)
        o.plot_allavg(g.ohlc,       ax=ax, panel=0, patches=g.ax_patches)
        o.plot_mavs(g.ohlc,         ax=ax, panel=0, patches=g.ax_patches)
        #= o.plot_lowerclose(g.ohlc,   ax=ax, panel=0, patches=g.ax_patches)
        # # * panel 1
        #= o.plot_dstot(g.ohlc,        ax=ax, panel=1, patches=g.ax_patches)
        #

        # * add the legends
        # for i in range(g.num_axes):
        #     ax[i].legend(handles=g.ax_patches[i], loc='upper left', shadow=True, fontsize='x-small')

        # * clear the legends so as not to keep appending to previous legend
        g.ax_patches = []
        for i in range(g.num_axes):
            g.ax_patches.append([])

        if g.cvars['allow_pause']:
            plt.ion()
            plt.gcf().canvas.start_event_loop(g.interval / 1000)

    o.trigger(ax[0])
    if g.cvars["save"]:
        o.threadit(o.savefiles()).run()

    # if g.display:
    #     ax[0].fill_between(
    #         g.ohlc.index,
    #         g.ohlc['Close'],
    #         g.ohlc['MAV1'],
    #         color=g.cvars['styles']['bullfill']['color'],
    #         alpha=g.cvars['styles']['bullfill']['alpha'],
    #         where=g.ohlc['Close']<g.ohlc['MAV1']
    #     )
    #     ax[0].fill_between(
    #         g.ohlc.index,
    #         g.ohlc['Close'],
    #         g.ohlc['MAV1'],
    #         color=g.cvars['styles']['bearfill']['color'],
    #         alpha=g.cvars['styles']['bearfill']['alpha'],
    #         where=g.ohlc['Close']>g.ohlc['MAV1']
    #     )
    #     ax[0].fill_between(
    #         g.ohlc.index,
    #         g.ohlc['Close'],
    #         g.ohlc['lowerClose'],
    #         color=g.cvars['styles']['bulllow']['color'],
    #         alpha=g.cvars['styles']['bulllow']['alpha'],
    #         where=g.ohlc['Close']<g.ohlc['lowerClose']
    #     )
    #     ax[0].fill_between(
    #         g.ohlc.index,
    #         g.ohlc['Close'],
    #         g.ohlc['lowerClose'],
    #         color=g.cvars['styles']['bearlow']['color'],
    #         alpha=g.cvars['styles']['bearlow']['alpha'],
    #         where=g.ohlc['Close']>g.ohlc['lowerClose']
    #     )

    # print(g.gcounter, end="\r")
    if g.last_side == "sell":

        if o.isfile("_exit_on_sell"):
            o.deletefile("_exit_on_sell")
            print("Exiting on '_exit_on_sell'")
            exit(0)
        if o.isfile("_wait_on_sell"):
            o.deletefile("_wait_on_sell")
            print("Exiting on '_wait_on_sell'")
            o.waitfor()

        if g.cvars['testnet'] and not g.cvars['offline']:
            try:
                balances = b.get_balance()
                g.reserve_seed = o.toPrec("amount",balances[g.QUOTE]['free']/b.get_ticker(g.cvars['pair'],field='close'))
                # print(f"reserve_seed now = [{_reserve_seed}]")
                g.initial_purch_qty = g.cdata["pqty"][0]
                # g.initial_purch_qty = float(o.read_val_from_file("_pqty", default=o.get_purch_qty(g.reserve_seed)))
                # print(f"purch_qty now = [{g.initial_purch_qty}]")
                # g.live_balance = balances[g.BASE]['free']
            except:
                pass

    # g.now_time = o.get_now()
    # print(g.now_time-g.last_time)
    # g.last_time = g.now_time

    # if g.gcounter > 3000: exit()
if g.display:
    ani = animation.FuncAnimation(fig=fig, func=animate, frames=1086400, interval=g.interval, repeat=False)
    plt.show()
else:
    while True:
        working(0)
