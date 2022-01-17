#!/usr/bin/python -W ignore
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
from colorama import Fore, Style
from colorama import init as colorama_init

import lib_v2_globals as g
import lib_v2_ohlc as o


g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
g.autoclear = True
g.datatype = g.cvars["datatype"]
g.override = False
runcfg = False
try:
    opts, args = getopt.getopt(argv, "-hrnD:O:R:", ["help", "recover", 'nohead', 'datatype=', 'override=','runcfg='])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-r, --recover")
        print("-n, --nohead")
        print("-D, --datatype")
        print("-O, --override")
        print("-R, --runcfg <cfg>  ('T1')")
        sys.exit(0)

    if opt in ("-r", "--recover"):
        g.recover = True

    if opt in ("-n", "--nohead"):
        g.headless = True

    if opt in ("-D", "--datatype"):
        g.datatype = arg

    if opt in ("-O", "--override"):
        g.override = arg
        o.apply_overrides()

    if opt in ("-R", "--runcfg"):
        runcfg = arg
        ts = time.time()
        bufile = f"safe/config.toml.{ts}"
        print(f"Backup toml file: [{bufile}]")
        shutil.copy("config.toml",bufile)
        print(f"Running: [./run_{runcfg}.sh]")
        os.system(f"./run_{runcfg}.sh")

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)



g.display = g.cvars['display']
g.headless = g.cvars['headless']
if g.headless:
    g.display = False
g.show_textbox = g.cvars["show_textbox"]

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
    # * assume this is headless if er end up here as the abive requires a GUI
    g.headless = True

# * this needs to load first
colorama_init()
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
g.ticker_src.load_markets()
# g.ticker_src.load_fees() # breask intestnet

g.spot_src = g.ticker_src
g.dbc, g.cursor = o.getdbconn()

g.startdate = o.adj_startdate(
    g.cvars['startdate'])  # * adjust startdate so that the listed startdate is the last date in the df array
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

if g.cvars["convert_price"]:
    o.convert_price()

# * arrays that need to exist from the start, but can;t be in globals as we need g.cvars to exist first

g.mav_ary[0] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[1] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[2] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[3] = [None for i in range(g.cvars['datawindow'])]

g.dstot_ary = [0 for i in range(g.cvars['datawindow'])]
g.dstot_lo_ary = [0 for i in range(g.cvars['datawindow'])]
g.dstot_hi_ary = [0 for i in range(g.cvars['datawindow'])]



if g.datatype == "backtest":
    o.get_priceconversion_data()
    o.get_bigdata()

if g.datatype == "live":
    g.interval = g.cvars['live']['interval']

# * if not statefile, make one, otherwise load existing 'state' file
# * mainly meant to initialise the state vars. vals should be empty unless in recovery

g.state = {}

# ! reload stuff here
# if not os.path.isfile(g.cvars['statefile']):
#     # Path(g.cvars['statefile']).touch()
#     g.state = {}
# else:
#     g.state = o.cload(g.cvars['statefile'])

# * check for/set session name
o.state_wr("session_name", o.get_sessioname())
g.tmpdir = f"/tmp/{g.session_name}"
print(f"checking {g.tmpdir}")
if os.path.isdir(g.tmpdir):
    print(f"exists... deleting")
    os.system(f"rm -rf {g.tmpdir}")
os.mkdir(g.tmpdir)


if g.autoclear:  # * automatically clear all (default)
    o.clearstate()
    o.state_wr('isnewrun', True)
    g.gcounter = 0

    o.threadit(o.sqlex(f"delete from orders where session = '{g.session_name}'")).run()
    o.sqlex(f"ALTER TABLE orders AUTO_INCREMENT = 1")

if g.cvars['log_mysql']:
    o.sqlex(f"SET GLOBAL general_log = 'ON'")
else:
    o.sqlex(f"SET GLOBAL general_log = 'OFF'")

if g.recover:  # * automatically recover from saved data (-r)
    o.state_wr('isnewrun', False)
    o.loadstate()
    g.needs_reload = True
    g.gcounter = o.state_r("gcounter")
    g.session_name = o.state_r("session_name")
    lastdate = \
    o.sqlex(f"select order_time from orders where session = '{g.session_name}' order by id desc limit 1", ret="one")[0]
    # * we get lastdate here, but only use if in recovery
    g.startdate = f"{lastdate}"

# * these vars are loaded into mem as they (might) change during runtime
# g.interval          = g.cvars["interval"]
g.buy_fee = g.cvars['buy_fee']
g.sell_fee = g.cvars['sell_fee']
g.ffmaps_lothresh = g.cvars['ffmaps_lothresh']
g.ffmaps_hithresh = g.cvars['ffmaps_hithresh']
g.sigffdeltahi_lim = g.cvars['sigffdeltahi_lim']
g.dstot_buy = g.cvars["dstot_buy"]

with open('issue', 'r') as f:
    g.issue = f.readline().strip()

# g.capital           = g.cvars["capital"]
# g.purch_pct         = g.cvars["purch_pct"]/100
# g.purch_qty         = g.capital * g.purch_pct
# g.purch_qty         = g.cvars['purch_qty']
# o.state_wr("purch_qty", g.purch_qty)
g.bsuid = 0
_reserve_seed = g.cvars[g.datatype]['reserve_seed']
_margin_x = g.cvars[g.datatype]['margin_x']
g.capital = _reserve_seed * _margin_x
g.cwd = os.getcwd().split("/")[-1:][0]
g.cap_seed = _reserve_seed

streamfile = o.resolve_streamfile()
if os.path.isfile(streamfile):
    os.remove(streamfile)

g.BASE = g.cvars['pair'].split("/")[0]
g.QUOTE = g.cvars['pair'].split("/")[1]

# print("test fr perf")
if str(g.cvars[g.datatype]['testpair'][0]).find("perf") != -1:
    # print("found")
    # o.waitfor()
# if g.cvars[g.datatype]['testpair'][0] == "BUY_perf":
    # pfile = f"data/perf_{g.cvars['perf_bits']}_{g.BASE}{g.QUOTE}_{g.cvars[g.datatype]['timeframe']}.json"
    g.pfile = f"data/perf_{g.cvars['perf_bits']}_{g.BASE}{g.QUOTE}_{g.cvars[g.datatype]['timeframe']}_{g.cvars['perf_filter']}f.json"

    print(g.pfile)
    o.waitfor()
    try:
        f = open(g.pfile, )
        g.rootperf = json.load(f)
    except Exception as e:
        print(f"ERROR trying to load performance data file [{g.pfile}]: {e}")
        exit()

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
b = Fore.CYAN + Style.BRIGHT
e = Style.RESET_ALL
print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print(f"           CURRENT PARAMS             ")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
if g.datatype == "stream":
    print(f"{a}WSS Datafile:    {b}{o.resolve_streamfile()}{e}")

if g.cvars[g.datatype]['testpair'][0] == "BUY_perf":
    print(f"{a}Soundex file:       {b}{g.pfile}{e}")

print(f"{a}Display:         {b}{g.display}{e}")
print(f"{a}Save:            {b}{g.cvars['save']}{e}")
print(f"{a}MySQL log:       {b}{g.cvars['log_mysql']}{e}")
print(f"{a}Log to file:     {b}{g.cvars['log2file']}{e}")
print(f"{a}Textbox:         {b}{g.show_textbox}{e}")
print("")
print(f"{a}Testnet:         {b}{g.cvars['testnet']}{e}")
print(f"{a}Offline:         {b}{g.cvars['offline']}{e}")
print(f"{a}Overrides:       {b}{g.override}{e}")
print("")
print(f"{a}Datatype:        {b}{g.datatype}{e}")
print(f"{a}S/L purch:       {b}{g.cvars[g.datatype]['short_purch_qty']}/{g.cvars[g.datatype]['long_purch_qty']}{e}")
print(f"{a}Nextbuy inc.:    {b}{g.cvars[g.datatype]['next_buy_increments']}{e}")
print(f"{a}Testpair:        {b}{g.cvars[g.datatype]['testpair']}{e}")
print(f"{a}Loop interval:   {b}{g.interval}ms ({g.interval / 1000}{e})")
print(f"{a}Res. seed:       {b}{g.cvars[g.datatype]['reserve_seed']}{e}")
print(f"{a}Margin:          {b}{g.cvars[g.datatype]['margin_x']}{e}")
print("")
if g.datatype == "backtest":
    print(f"{a}datafile:       {b}{g.cvars['backtestfile']}{e}")
    print(f"{a}Start date:     {b}{g.cvars['startdate']}{e}")
    print(f"{a}End date:       {b}{g.cvars['enddate']}{e}")
o.cclr()

if sys.stdout.isatty():
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
def animate(k):
    working(k)

def working(k):
    # * reload cfg file - alows for dynamic changes during runtime
    g.cvars = toml.load(g.cfgfile)
    if g.override:
        o.apply_overrides()

    try:
        g.cursor.execute("SET AUTOCOMMIT = 1")
    except:
        #* restart mysql
        os.system("./restart_mysql")


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
    _reserve_seed = g.cvars[g.datatype]['reserve_seed']
    _margin_x = g.cvars[g.datatype]['margin_x']
    g.reserve_cap = _reserve_seed * _margin_x

    # * track the number of short buys
    if g.short_buys > 0:
        g.since_short_buy += 1

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + get the source data as a dataframe
    # + ───────────────────────────────────────────────────────────────────────────────────────
    # ! JWFIX need to put this in an error-checking loop

    if not o.load_data(t):
        exit(1)

    g.total_reserve = (g.capital * g.this_close)

    # * just used in debugging to stop at some date
    enddate = datetime.strptime(g.cvars['enddate'], "%Y-%m-%d %H:%M:%S")
    if g.ohlc['Date'][-1] > enddate and g.datatype == "backtest":
        print(f"Reached endate of {enddate}")
        exit()

    # * Make frame title
    if g.display:
        ft = o.make_title()
        fig.suptitle(ft, color='white')

        if g.cvars["convert_price"]:
            ax[0].set_ylabel("Asset Value (in $USD)", color='white')
        else:
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

    o.make_rohlc(g.ohlc)  # * make inverted Close

    o.make_sigffmb(g.ohlc)  # * make 6 band passes of org
    o.make_sigffmb(g.ohlc, inverted=True)  # * make 6 band passes of inverted
    o.make_ffmaps(g.ohlc)  # * find the delta of both
    o.make_dstot(g.ohlc)  # * cum sum of slopes of each band

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

        # o.threadit(o.rebuild_ax(ax)).run()
        ax[0].set_title(f"{add_title} - ({o.get_latest_time(g.ohlc)}-{t.current.second})", color='white')

        # * Make text box

        pretty_nextbuy = "N/A" if g.next_buy_price > 100000 else f"{g.next_buy_price:6.2f}"
        next_buy_pct = (g.cvars[g.datatype]['next_buy_increments'] * o.state_r('curr_run_ct')) * 100

        if g.show_textbox:
            textstr = f'''
g.gcounter:         {g.gcounter}
g.curr_run_ct:      {g.curr_run_ct}
MX int/tot:        ${g.margin_interest_cost}/${g.total_margin_interest_cost}
Buys long/short:    {g.long_buys}/{g.short_buys}
Cap. Raised: ({g.BASE})  {g.capital - (_reserve_seed * _margin_x)}
Tot Capital: ({g.BASE})  {g.capital}
Cap. Raised %:      {g.pct_cap_return * 100}
Seed Cap. Raised %: {g.pct_capseed_return * 100}
Tot Reserves:      ${g.total_reserve}
Tot Seed:          ${_reserve_seed * g.this_close}
Net Profit:        ${g.running_total}
Covercost:         ${g.adjusted_covercost}
<{g.coverprice:6.2f}> <{g.ohlc['Close'][-1]:6.2f}> <{pretty_nextbuy}> ({next_buy_pct:2.1f}%)
'''

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
        o.plot_mavs(g.ohlc,         ax=ax, panel=0, patches=g.ax_patches)
        o.plot_lowerclose(g.ohlc,   ax=ax, panel=0, patches=g.ax_patches)
        # # * panel 1
        o.plot_dstot(g.ohlc,        ax=ax, panel=1, patches=g.ax_patches)
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

    if g.display:
        ax[0].fill_between(
            g.ohlc.index,
            g.ohlc['Close'],
            g.ohlc['MAV1'],
            color=g.cvars['styles']['bullfill']['color'],
            alpha=g.cvars['styles']['bullfill']['alpha'],
            where=g.ohlc['Close']<g.ohlc['MAV1']
        )
        ax[0].fill_between(
            g.ohlc.index,
            g.ohlc['Close'],
            g.ohlc['MAV1'],
            color=g.cvars['styles']['bearfill']['color'],
            alpha=g.cvars['styles']['bearfill']['alpha'],
            where=g.ohlc['Close']>g.ohlc['MAV1']
        )
        ax[0].fill_between(
            g.ohlc.index,
            g.ohlc['Close'],
            g.ohlc['lowerClose'],
            color=g.cvars['styles']['bulllow']['color'],
            alpha=g.cvars['styles']['bulllow']['alpha'],
            where=g.ohlc['Close']<g.ohlc['lowerClose']
        )
        ax[0].fill_between(
            g.ohlc.index,
            g.ohlc['Close'],
            g.ohlc['lowerClose'],
            color=g.cvars['styles']['bearlow']['color'],
            alpha=g.cvars['styles']['bearlow']['alpha'],
            where=g.ohlc['Close']>g.ohlc['lowerClose']
        )

    print(g.gcounter, end="\r")

if g.display:
    ani = animation.FuncAnimation(fig=fig, func=animate, frames=1086400, interval=g.interval, repeat=False)
    plt.show()
else:
    while True:
        working(0)
