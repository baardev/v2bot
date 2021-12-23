#!/usr/bin/env python
import cProfile
import gc
import re
import ccxt
import sys
import getopt
import logging
import os
import time
import toml
import pandas as pd
import lib_v2_globals as g
import lib_v2_ohlc as o
from datetime import datetime
from pathlib import Path
from colorama import init as colorama_init
from colorama import Fore, Back, Style

g.cvars = toml.load(g.cfgfile)
g.display = g.cvars['display']
g.headless = g.cvars['headless']

try:
    import matplotlib
    matplotlib.use("Qt5agg")
    import matplotlib.animation as animation
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure
    import lib_v2_listener as kb
    g.headless = False
except:
     # * assume this is headless if er end up here as the abive requires a GUI
    g.headless = True

# * this needs to load first
colorama_init()
pd.set_option('display.max_columns', None)
g.verbose = g.cvars['verbose']
g.dbc, g.cursor = o.getdbconn()
g.startdate = o.adj_startdate(g.cvars['startdate']) # * adjust startdate so that the listed startdate is the last date in the df array
g.datawindow = g.cvars["datawindow"]

# * if not statefile, make one, otherwise load existing 'state' file
# * mainly meant to initialise the state vars. vals should be empty unless in recovery
if not os.path.isfile(g.cvars['statefile']):
    Path(g.cvars['statefile']).touch()
else:
    g.state = o.cload(g.cvars['statefile'])

# * check for/set session name
o.state_wr("session_name", o.get_sessioname())
datatype =g.cvars["datatype"]

g.logit = logging
g.logit.basicConfig(
    filename="logs/ohlc.log",
    filemode='w',
    format='%(asctime)s - %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=g.cvars['logging']
)
stdout_handler = g.logit.StreamHandler(sys.stdout)

# * Load the ETH data and BTC data for price conversions
if datatype == "backtest":
    o.get_priceconversion_data()
    o.get_bigdata()

    # * create the global buy/sell and all_records dataframes
    columns = ['Timestamp', 'buy', 'mclr', 'sell', 'qty', 'subtot', 'tot', 'pnl', 'pct']
    g.df_buysell = pd.DataFrame(index = range(g.cvars['datawindow']), columns = columns)

if datatype == "live":
    o.waitfor(f"!!! RUNNING ON LIVE / {g.cvars['datatype']} !!!")
    g.interval = g.cvars['live_interval']
else:
    if not g.cvars["offline"]:
        g.interval = 1

if g.cvars["convert_price"]:
    o.convert_price()

# * prebuild MAsn columns - these are a series of moving averages, but can be anything
for i in range(6):
    if g.cvars['MAsn'][i]['on']:
        g.bigdata[f'MAs{i}'] = g.bigdata['Close'].ewm(span=g.cvars['MAsn'][i]['span']).mean()

g.logit.info(f"Loaded [{len(g.bigdata.index)}] items from [{g.cvars['backtestfile']}]")

# * arrays that need to exist from the start, but can;t be in globals as we need g.cvars to exist first

g.mav_ary[0] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[1] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[2] = [None for i in range(g.cvars['datawindow'])]
g.mav_ary[3] = [None for i in range(g.cvars['datawindow'])]

g.dstot_ary = [0 for i in range(g.cvars['datawindow'])]
g.dstot_lo_ary = [0 for i in range(g.cvars['datawindow'])]
g.dstot_hi_ary = [0 for i in range(g.cvars['datawindow'])]

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
g.autoclear = True

try:
    opts, args = getopt.getopt(argv, "-hrn", ["help", "recover", 'nohead'])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-r, --recover  ")
        sys.exit(0)

    if opt in ("-r", "--recover"):
        g.recover = True

    if opt in ("-n", "--nohead"):
        g.headless = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

if g.autoclear: #* automatically clear all (defauly)
    o.clearstate()
    o.state_wr('isnewrun',True)
    g.gcounter = 0

    o.threadit(o.sqlex(f"delete from orders where session = '{g.session_name}'")).run()
    # rs = o.sqlex(f"delete from orders where session = '{g.session_name}'")

if g.recover:  # * automatically recover from saved data (-r)
    o.state_wr('isnewrun', False)
    o.loadstate()
    g.needs_reload = True
    g.gcounter = o.state_r("gcounter")
    g.session_name = o.state_r("session_name")
    lastdate = o.sqlex(f"select order_time from orders where session = '{g.session_name}' order by id desc limit 1",ret="one")[0]
    # * we get lastdate here, but only use if in recovery
    g.startdate = f"{lastdate}"


# * these vars are loaded into mem as they (might) change during runtime
g.interval          = g.cvars["interval"]
g.buy_fee           = g.cvars['buy_fee']
g.sell_fee          = g.cvars['sell_fee']
g.ffmaps_lothresh   = g.cvars['ffmaps_lothresh']
g.ffmaps_hithresh   = g.cvars['ffmaps_hithresh']
g.sigffdeltahi_lim  = g.cvars['sigffdeltahi_lim']
g.dstot_buy         = g.cvars["dstot_buy"]
# g.capital           = g.cvars["capital"]
# g.purch_pct         = g.cvars["purch_pct"]/100
# g.purch_qty         = g.capital * g.purch_pct
# g.purch_qty         = g.cvars['purch_qty']
# o.state_wr("purch_qty", g.purch_qty)
g.bsuid             = 0
g.capital       = g.cvars["reserve_seed"]*g.cvars["margin_x"]
# g.purch_qty_adj_pct = g.cvars["purch_qty_adj_pct"]
g.lowerclose_pct    = g.cvars['lowerclose_pct']
g.cwd               = os.getcwd().split("/")[-1:][0]
# * ccxt doesn't yet support Coinbase ohlcv data, so CB and binance charts will be a little off
# g.ticker_src = ccxt.bibox()
# g.spot_src = ccxt.bibox()
g.ticker_src = ccxt.binance()
g.spot_src = ccxt.coinbase()

# * get screens and axes
try:
    fig, fig2, ax = o.make_screens(figure)
except:
    fig = False
    fig2 = False
    ax = [0, 0, 0, 0, 0, 0]

# * Start the listner threads and join them so the script doesn't end early
# * This needs X-11, so is no display, no listener
if g.display and not g.headless:
    kb.keyboard_listener.start()
# ! https://pynput.readthedocs.io/en/latest/keyboard.html
# ! WARNING! This listens GLOBALLY, on all windows, so be careful not to use these keys ANYWHERE ELSE
print(Fore.MAGENTA + Style.BRIGHT)
print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print(f"           {g.session_name}            ")
print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
print("┃ Alt + Arrow Down : Decrease interval ┃")
print("┃ Alt + Arrow Up   : Increase interval ┃")
print("┃ Alt + End        : Shutdown          ┃")
print("┃ Alt + Delete     : Pause (10s)/Resume┃")
print("┃ Alt + Home       : Verbose/Quiet     ┃")
print("┃ Alt + b          : Buy signal        ┃")
print("┃ Alt + s          : Sell signal       ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
o.cclr()

# * ready to go, but launch only on boundry if live
if g.cvars['datatype'] == "live":
    bt = g.cvars['load_on_boundary']
    if not g.epoch_boundry_ready:
        while o.is_epoch_boundry(bt) != 0:
            print(f"{bt - g.epoch_boundry_countdown} waiting for epoch boundry ({bt})", end="\r")
            time.sleep(1)
        g.epoch_boundry_ready = True
        # * we found teh boundry, but now need to wait for teh data to get loaded and updated from the provider
        print(f"{g.cvars['boundary_load_delay']} sec. latency pause...")
        time.sleep(g.cvars['boundary_load_delay'])

print(f"Loop interval set at {g.interval}ms ({g.interval/1000}s)                                         ")

# * mainyl for textbox formatting
plt.rcParams['font.family'] = 'monospace'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.default'] = 'regular'
g.now_time = o.get_now()
g.last_time = o.get_now()
g.sub_now_time = o.get_now()
g.sub_last_time = o.get_now()

props = dict(boxstyle = 'round', pad = 1, facecolor = 'black', alpha = 1.0)
# tracemalloc.start()

#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    LOOP    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
def animate(k):
    working(k)
# @profile
def working(k):
    # print(tracemalloc.get_traced_memory())
    # del g.ohlc
    # del g.df_buysell
    # del g.cvars
    # g.ohlc = False
    gc.collect()

    g.cvars = toml.load(g.cfgfile)
    g.display = g.cvars['display']
    if g.gcounter % 100 == 0:
        loop_time = g.now_time - g.last_time
        g.last_time = g.now_time
        g.now_time = o.get_now()
        o.log2file(loop_time/100, "secs.log")
        o.log2file(f"\t[{g.gcounter}] #0: {sum(g.rtime[0]) / 100}", "secs.log")
        o.log2file(f"\t[{g.gcounter}] #1: {sum(g.rtime[1]) / 100}", "secs.log")
        o.log2file(f"\t[{g.gcounter}] #2: {sum(g.rtime[2]) / 100}", "secs.log")
        o.log2file(f"\t[{g.gcounter}] #3: {sum(g.rtime[3]) / 100}", "secs.log")
        g.rtime[0] = []
        g.rtime[1] = []
        g.rtime[2] = []
        g.rtime[3] = []

    # * reload cfg file - alows for dynamic changes during runtime

    g.logit.basicConfig(level=g.cvars['logging'])
    this_logger = g.logit.getLogger()
    if g.verbose:
        this_logger.addHandler(stdout_handler)
    else:
        this_logger.removeHandler(stdout_handler)
    if g.time_to_die:
        exit(0)

    g.gcounter = g.gcounter + 1
    o.state_wr('gcounter',g.gcounter)
    g.datasetname = g.cvars["backtestfile"]  if datatype == "backtest" else "LIVE"
    pair = g.cvars["pair"]
    t = o.Times(g.cvars["since"])
    # * Title of ax window
    add_title = f"{g.cwd}/[{g.cvars['testpair'][0]}]-[{g.cvars['testpair'][1]}]:{g.cvars['datawindow']}]"
    timeframe = g.cvars["timeframe"]
    g.reserve_cap = g.cvars["reserve_seed"] * g.cvars["margin_x"]

    # * track the numner of short buys
    if g.short_buys > 0:
        g.since_short_buy += 1

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + get the source data as a dataframe
    # + ───────────────────────────────────────────────────────────────────────────────────────
    retry = 0
    expass = False

    while not expass or retry < 10:
        try:
            # g.ohlc = o.get_ohlc(since=t.since)
            g.ohlc = o.get_ohlc(t.since)
            # cProfile.run('re.compile("o.get_ohlc|t.since")')

            retry = 10
            expass = True
        except Exception as e:
            print(f"Exception error: [{e}]")
            print(f'Something went wrong. Error occured at {datetime.now()}. Retrying in 1 minute.')
            # * reinstantiate connections in case of timeout
            time.sleep(60)
            g.ticker_src = ccxt.binance() #! JWFIX un-hardcode exchanges
            g.spot_src = ccxt.coinbase()
            retry = retry + 1
            expass = False

    # o.log2file(f"\tRTIME #1: {o.report_time(g.sub_last_time)}","secs.log")
    # print(g.capital , g.this_close)
    g.total_reserve = (g.capital * g.this_close)

    # * just used in debugging to stop at some date
    enddate = datetime.strptime(g.cvars['enddate'], "%Y-%m-%d %H:%M:%S")
    if g.ohlc['Date'][-1] > enddate:
        print(f"Reached endate of {enddate}")
        exit()

    # * Make frame title
    if g.display and not g.headless:
        ft = o.make_title(type="UNKNOWN", pair=pair, timeframe=timeframe, count="N/A", exchange="Binance",fromdate="N/A", todate="N/A")
        fig.suptitle(ft, color='white')

        if g.cvars["convert_price"]:
            ax[0].set_ylabel("Asset Value (in $USD)", color='white')
        else:
            ax[0].set_ylabel("Asset Value (in BTC)", color = 'white')

    # ! ───────────────────────────────────────────────────────────────────────────────────────
    # ! CHECK THE SIZE OF THE DATAFRAME and Gracefully exit on error or command
    # ! ───────────────────────────────────────────────────────────────────────────────────────
    if datatype == "backtest":
        if len(g.ohlc.index) != g.cvars['datawindow']:
            if not g.time_to_die:
                if g.batchmode:
                    exit(0)
                else:
                    print(f"datawindow: [{g.cvars['datawindow']}] != index: [{[{len(g.ohlc.index)}] }])")
                    o.waitfor("End of data (or some catastrophic error)... press enter to exit")
            else:
                print("Goodbye")
            exit(0)

    # # + ───────────────────────────────────────────────────────────────────────────────────────
    # # + make the data, add to dataframe !! ORDER IS IMPORTANT
    # # + ───────────────────────────────────────────────────────────────────────────────────────
    o.threadit(o.make_lowerclose(g.ohlc)).run()                             # * make EMA of close down by n%
    o.threadit(o.make_mavs(g.ohlc)).run()                                           # * make series of MAVs

    o.make_rohlc(g.ohlc)  # * make inverted Close

    o.make_sigffmb(g.ohlc)  # * make 6 band passes of org
    o.make_sigffmb(g.ohlc, inverted = True)  # * make 6 band passes of inverted
    o.make_ffmaps(g.ohlc)# * find the delta of both
    o.make_dstot(g.ohlc)                                          # * cum sum of slopes of each band

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + update some values based on current data
    # + ───────────────────────────────────────────────────────────────────────────────────────
    bull_bear_limit = 1
    if g.ohlc.iloc[-1]['Close'] > g.ohlc.iloc[-1][f'MAV{bull_bear_limit}']:
        g.lowerclose_pct = g.cvars['lowerclose_pct_bull']
        g.market = "bull"
        # MOVED TO LIB - g.dstot_Dadj = 0 #g.cvars['dstot_Dadj'][0]
    else:
        g.market = "bear"
        g.lowerclose_pct = g.cvars['lowerclose_pct_bear']
        # MOVED TO LIB - g.dstot_Dadj = g.cvars['dstot_Dadj'] * g.long_buys #g.cvars['dstot_Dadj'][g.long_buys]

    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    TRIGGER    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    rem_cd = g.cooldown - g.gcounter if g.cooldown - g.gcounter > 0 else 0

    # * clear all the plots and patches
    if g.display and not g.headless:
        g.ax_patches = []
        o.threadit(o.rebuild_ax(ax)).run()
        ax[0].set_title(f"{add_title} - ({o.get_latest_time(g.ohlc)}-{t.current.second})", color = 'white')

        # * Make text box

        pretty_nextbuy = "N/A" if g.next_buy_price > 100000 else f"{g.next_buy_price:6.2f}"
        next_buy_pct = (g.cvars['next_buy_increments'] * o.state_r('curr_run_ct')) * 100


# g.dstot_Dadj:      {g.dstot_Dadj}
# dshloamp:          {o.truncate(g.ohlc['Dstot_lo'][-1],2)}
# Bull/Bear MAV:     {g.cvars['lowerclose_pct_bull']*100:3.2f}/{g.cvars['lowerclose_pct_bear']*100:3.2f}
# g.cooldown:        {rem_cd}
# g.since_short_buy: {g.since_short_buy}
#coverprice:        {g.coverprice:6.2f}
# close:             {g.ohlc['Close'][-1]:6.2f}
# nextbuy:           {pretty_nextbuy} ({next_buy_pct:2.1f})%

        if g.cvars['show_textbox']:
            textstr = f'''
g.gcounter:        {g.gcounter}
g.curr_run_ct:     {g.curr_run_ct}

MX int/tot:        ${g.margin_interest_cost:,.2f}/${g.total_margin_interest_cost:,.2f}
Buys long/short:    {g.long_buys}/{g.short_buys}

Cap. Raised: (ETH)  {g.capital - (g.cvars['reserve_seed'] * g.cvars['margin_x']):7.5f}
Tot Capital: (ETH)  {g.capital:6.2f}

Cap. Raised %:      {g.pct_cap_return*100:7.5f}
Seed Cap. Raised %: {g.pct_capseed_return*100:7.5f}

Tot Reserves:      ${g.total_reserve:,.0f}
Tot Seed:          ${g.cvars['reserve_seed']*g.this_close:,.0f}
Net Profit:        ${g.running_total:,.2f}

<{g.coverprice:6.2f}> <{g.ohlc['Close'][-1]:6.2f}> <{pretty_nextbuy}> ({next_buy_pct:2.1f}%)
'''
            ax[1].text(0.05, 0.9, textstr, transform = ax[1].transAxes, color = 'wheat', fontsize = 10, verticalalignment = 'top', bbox = props)

        # * plot everything
        # * panel 0

        o.threadit(o.plot_close(        g.ohlc, ax = ax, panel = 0, patches = g.ax_patches)).run()
        o.threadit(o.plot_mavs(         g.ohlc, ax = ax, panel = 0, patches = g.ax_patches)).run()
        o.threadit(o.plot_lowerclose(   g.ohlc, ax = ax, panel = 0, patches = g.ax_patches)).run()
        o.threadit(o.plot_MAsn(         g.ohlc, ax = ax, panel = 0, patches = g.ax_patches)).run()
        # * panel 1
        o.threadit(o.plot_dstot(        g.ohlc, ax = ax, panel = 1, patches = g.ax_patches)).run()

        if g.cvars['allow_pause']:
            plt.ion()
            plt.gcf().canvas.start_event_loop(g.interval / 1000)

    o.trigger(ax[0])
    # o.trigger(g.ohlc, ax=ax[0])
    # cProfile.run('re.compile("o.trigger|ax[0]")')

    o.threadit(o.savefiles()).run()

    # if g.gcounter > 200:
    #     exit()

if g.display and not g.headless:
    ani = animation.FuncAnimation(fig=fig, func=animate, frames=1086400, interval=g.interval, repeat=False)
    plt.show()
else:
    while True:
        # time.sleep(g.interval) #! JWFIX  porobably should be a timer watch thread with an event
        working(0)