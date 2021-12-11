#!/usr/bin/python3.9

import matplotlib
# ! other matplotplib GUI options
matplotlib.use("Qt5agg")
import gc
import ccxt
import sys
import getopt
import logging
import os
import time
import toml
import pandas as pd
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.widgets import MultiCursor
import matplotlib.dates as mdates

# import mplfinance as mpf

# import lib_v2_panzoom as c
import lib_v2_globals as g
import lib_v2_ohlc as o
import lib_v2_listener as kb

from pathlib import Path
from colorama import init
from colorama import Fore, Back, Style
from datetime import datetime
from datetime import timedelta
# import datetime

init()
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)

#  * load all the config vars that are altered in runtime
g.verbose = g.cvars['verbose']



argv = sys.argv[1:]
pd.set_option('display.max_columns', None)

if g.cvars["datatype"] == "backtest":
    datafile = f"{g.cvars['datadir']}/{g.cvars['backtest_priceconversion']}"
    g.df_priceconversion_data = o.load(datafile)
    g.df_priceconversion_data.rename(columns={'Date': 'Timestamp'}, inplace=True)
    g.df_priceconversion_data["Date"] = pd.to_datetime(g.df_priceconversion_data['Timestamp'], unit='ms')
    g.df_priceconversion_data.index = pd.DatetimeIndex(g.df_priceconversion_data['Timestamp'])

try:
    opts, args = getopt.getopt(argv, "-hcr:", ["help", "clear", "recover"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-c, --clear  auto clear")
        print("-r, --recover  ")
        sys.exit(0)

    if opt in ("-c", "--clear"):
        g.autoclear = True
    if opt in ("-r", "--recover"):
        g.recover = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.dstot_ary = [0 for i in range(288)]
g.dstot_lo_ary = [0 for i in range(288)]
g.dstot_hi_ary = [0 for i in range(288)]

g.dbc, g.cursor = o.getdbconn()

g.logit = logging
g.logit.basicConfig(
    filename="logs/ohlc.log",
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=g.cvars['logging']
)
stdout_handler = g.logit.StreamHandler(sys.stdout)
# * Did we exit gracefully from the last time?

g.startdate = o.adj_startdate(g.cvars['startdate'])
# g.startdate = g.cvars['startdate']


# print("ORG g.startdate", g.startdate)
# print("NEW g.startdate", g.startdate)




if os.path.isfile('_session_name.txt'):
    with open('_session_name.txt') as f:
        g.session_name = f.readline().strip()
    # os.remove('_session_name.txt') # * del to ensure next run is not using same name
else:
    g.session_name = o.get_a_word()

g.state = o.cload("state.json")

if g.autoclear: #* automatically clear all (-c)
    o.clearstate()
    o.state_wr('isnewrun',True)
    g.gcounter = 0

else:
    if g.recover:  # * automatically recover from saved data (-r)
        o.state_wr('isnewrun', False)
        o.loadstate()
        g.needs_reload = True
        g.gcounter = o.state_r("gcounter")
        g.session_name = o.state_r("session_name")
        lastdate = o.sqlex(f"select order_time from orders where session = '{g.session_name}' order by id desc limit 1",ret="one")[0]
        # * we get lastdate here, but only use if in recovery
        g.startdate = f"{lastdate}"

    else:
        if o.waitfor(["Clear Last Data? (y/N)"]): # * True if 'y', defaults to 'N'
            o.clearstate()
            o.state_wr('isnewrun',True)
            g.autoclear = True

        else:                                     # * reload old data
            o.state_wr('isnewrun', False)
            o.loadstate()
            g.needs_reload = True
            g.gcounter = o.state_r("gcounter")
            g.session_name = o.state_r("session_name")
            lastdate = o.sqlex(f"select order_time from orders where session = '{g.session_name}' order by id desc limit 1",ret="one")[0]
            # * we get lastdate here, but only use if in recovery
            g.startdate = lastdate
            g.autoclear = True

if g.autoclear:  # * automatically clear all (-c)
    rs = o.sqlex(f"delete from orders where session = '{g.session_name}'")

if g.cvars["datatype"] == "live":
    o.waitfor(f"!!! RUNNING ON LIVE / {g.cvars['datatype']} !!!")

g.logit.info(f"Loading from {g.cfgfile}", extra={'mod_name': 'olhc'})

if o.state_r('isnewrun'):
    o.state_wr("session_name",g.session_name)

g.datawindow = g.cvars["datawindow"]
g.interval = g.cvars["interval"]

# g.purch_qty = g.cvars["purch_qty") #use
g.buy_fee = g.cvars['buy_fee']
g.sell_fee = g.cvars['sell_fee']
g.ffmaps_lothresh = g.cvars['ffmaps_lothresh']
g.ffmaps_hithresh = g.cvars['ffmaps_hithresh']
g.sigffdeltahi_lim = g.cvars['sigffdeltahi_lim']
g.dstot_buy = g.cvars["dstot_buy"]
g.dstot_sell = g.cvars["dstot_sell"]


g.capital =  g.cvars["capital"]
g.purch_pct =  g.cvars["purch_pct"]/100

g.purch_qty = g.capital * g.purch_pct

g.bsuid = 0
# g.uid=uuid.uuid4().hex
o.state_wr("purch_qty", g.purch_qty)
g.purch_qty_adj_pct = g.cvars["purch_qty_adj_pct"]

g.lowerclose_pct = g.cvars['lowerclose_pct']
datatype =g.cvars["datatype"]

# print(f"---{datatype}")
if datatype == "live":
    g.interval = g.cvars['live_interval']
else:
    if not g.cvars["offline"]:
        g.interval = 1000
    else:
        g.interval = 1
    # ! 1sec = 1000
    # ! 300000 = 5min


# * create the global buy/sell and all_records dataframes
# g.df_allrecords = pd.DataFrame()
g.df_buysell = pd.DataFrame(index=range(g.cvars['datawindow']),
                            columns=['Timestamp', 'buy', 'mclr', 'sell', 'qty', 'subtot', 'tot', 'pnl', 'pct'])
g.cwd = os.getcwd().split("/")[-1:][0]

# * ccxt doesn't yet support CB ohlcv data, so CB and binance charts will be a little off
# g.ticker_src = ccxt.binance()
# g.spot_src = ccxt.coinbase()
g.ticker_src = ccxt.bibox()
g.spot_src = ccxt.bibox()
# g.conversion = o.get_last_price(g.spot_src, date=g.df_priceconversion_data.iloc[-1]['Timestamp'])

o.clearstate()

fig2 = False
fig = False
ax = [0,0,0,0,0,0]
if g.cvars['display']:
    # * set up the canvas and windows
    fig = figure(figsize=(g.cvars["figsize"][0], g.cvars["figsize"][1]), dpi=96)
    fig.patch.set_facecolor('black')

    if g.cvars['2nd_screen']:
        fig2 = figure(figsize=(g.cvars["figsize2"][0], g.cvars["figsize"][1]), dpi=96)
        fig2.add_subplot(111)
        fig2.patch.set_facecolor('black')

    fig.add_subplot(211)  # OHLC - top left
    fig.add_subplot(212)  # VOl - mid left
    # fig.add_subplot(313)  # Delta - bottom left
    # fig.add_subplot(324)  # top right
    # fig.add_subplot(325)  # mid right
    # fig.add_subplot(326)  # bottom right

    ax = fig.get_axes()

    if g.cvars['2nd_screen']:
        ax2 = fig2.get_axes()
        ax[0] = ax2[0]

    g.num_axes = len(ax)
    multi = MultiCursor(fig.canvas, ax, color='r', lw=1, horizOn=True, vertOn=True)

# * Start the threads and join them so the script doesn't end early
kb.keyboard_listener.start()
if not os.path.isfile(g.cvars['statefile']): Path(g.cvars['statefile'].touch())

# + ! https://pynput.readthedocs.io/en/latest/keyboard.html
print(Fore.MAGENTA + Style.BRIGHT)
print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print(f"           {g.session_name}            ")
print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
print("┃ Alt + Arrow Down : Decrease interval ┃")
print("┃ Alt + Arrow Up   : Increase interval ┃")
print("┃ Alt + Arrow Left : Jump back 20 tcks ┃")
print("┃ Alt + Arrow Right: Jump fwd 20 tcks  ┃")
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


plt.rcParams['font.family'] = 'monospace'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.default'] = 'regular'


def animate(k):
    working(k)

#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    LOOP    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
def working(k):

    g.cvars = toml.load(g.cfgfile)
    this_logger = g.logit.getLogger()
    if g.verbose:
        this_logger.addHandler(stdout_handler)
    else:
        this_logger.removeHandler(stdout_handler)
    if g.time_to_die:
        exit(0)

    g.gcounter = g.gcounter + 1
    o.state_wr('gcounter',g.gcounter)

    if g.cvars["datatype"] == "backtest":
        g.datasetname = g.cvars["backtestfile"]
    else:
        g.datasetname = "LIVE"

    pair = g.cvars["pair"]

    t = o.Times(g.cvars["since"])
    add_title = f"{g.cwd}/{g.cvars['testpair'][0]}-{g.cvars['testpair'][1]}:{g.cvars['datawindow']}]"
    timeframe = g.cvars["timeframe"]


    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + get the source data as a dataframe
    # + ───────────────────────────────────────────────────────────────────────────────────────

    g.ticker_src = ccxt.binance()
    g.spot_src = ccxt.coinbase()
    g.ohlc = o.get_ohlc(g.ticker_src, g.spot_src, since=t.since)

            # continue
    # retry = 0
    # expass = False

    # while not expass or retry < 10:
    #     try:
    #         # * reinstantiate connections in case of timeout
    #         g.ticker_src = ccxt.binance()
    #         g.spot_src = ccxt.coinbase()
    #         g.ohlc = o.get_ohlc(g.ticker_src, g.spot_src, since=t.since)
    #         retry = 10
    #         expass = True
    #     except Exception as e:
    #         print(f"Exception error: [{e}]")
    #         print(f'Something went wrong. Error occured at {datetime.datetime.now()}. Wait for 1 minute.')
    #         time.sleep(60)
    #         retry = retry + 1
    #         expass = False
    #         # continue
    ohlc = g.ohlc

    g.CLOSE = ohlc['Close'][-1]

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + clear all the plots and patches
    # + ───────────────────────────────────────────────────────────────────────────────────────
    if g.cvars['display']:
        for i in range(g.num_axes): ax[i].clear()
        ax_patches = []
        for i in range(g.num_axes): ax_patches.append([])
        for i in range(g.num_axes): ax[i].grid(True, color='grey', alpha=0.3)

        ft = o.make_title(type="UNKNOWN", pair=pair, timeframe=timeframe, count="N/A", exchange="Binance",fromdate="N/A", todate="N/A")
        fig.suptitle(ft, color='white')
        # fig.patch.set_facecolor('black')
        # if o.cvars.get('2nd_screen'):
        #     fig2.patch.set_facecolor('black')

        ax[0].set_title(f"{add_title} - ({o.get_latest_time(ohlc)}-{t.current.second})", color='white')
        ax[0].set_ylabel("Asset Value (in $USD)", color='white')


    # ! ───────────────────────────────────────────────────────────────────────────────────────
    # ! CHECK THE SIZE OF THE DATAFRAME and Gracefully exit on error or command
    # ! ───────────────────────────────────────────────────────────────────────────────────────
    if g.cvars['datatype'] == "backtest":
        if len(ohlc.index) != g.cvars['datawindow']:
            if not g.time_to_die:
                if g.batchmode:
                    exit(0)
                else:
                    o.announce(what="finished")
                    o.waitfor("End of data... press enter to exit")
            else:
                print("Goodbye")
                o.announce(what="finished")
            exit(0)

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + make the data, add to dataframe !! ORDER IS IMPORTANT
    # + ───────────────────────────────────────────────────────────────────────────────────────
    for m in g.cvars["mavs"]: o.make_mav(ohlc, mav=m['length']) # * make 3 MAVS
    o.make_rohlc(ohlc)                                          # * make inverted Close
    o.make_sigffmb(ohlc)                                        # * make 6 band passes of org
    o.make_sigffmb(ohlc, inverted = True)                       # * make 6 band passes of inverted
    o.make_ffmaps(ohlc)                                         # * find the delta of both
    o.make_dstot(ohlc)                                          # * cum sum of slopes of each band
    o.make_lowerclose(ohlc)                                     # * make EMA of close down by n%

    # + ───────────────────────────────────────────────────────────────────────────────────────
    # + plot the data
    # + ───────────────────────────────────────────────────────────────────────────────────────

    # #!FILTERS
    if ohlc.iloc[-1]['Close'] > ohlc.iloc[-1]['MAV40']:
        g.lowerclose_pct = g.cvars['lowerclose_pct_bull']
        g.market = "bull"
        # g.dstot_Dadj = g.cvars['dstot_Dadj'][0]

    else:
        g.market = "bear"
        g.lowerclose_pct = g.cvars['lowerclose_pct_bear']
        # g.dstot_Dadj = g.cvars['dstot_Dadj'][g.long_buys]


    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    TRIGGERS    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # # + ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    o.trigger(ohlc, ax=ax[0])
    # * save a copy of the final data plotted - used for debugging and viewing
    if g.cvars["save"]:
        o.save_df_json(ohlc, "_ohlcdata.json")
        o.save_df_json(g.df_buysell, "_buysell.json")

        # * save every transaction
        if g.gcounter == 1:
            header = True
            mode = "w"
        else:
            header = False
            mode = "a"

        ohlc.tail(1).to_csv(f"_allrecords.csv", header=header, mode=mode, sep='\t', encoding='utf-8')

        try:
            adf = pd.read_csv(f'_allrecords.csv')
            fn = f"_allrecords.json"
            g.logit.debug(f"Save {fn}")
            o.save_df_json(adf, fn)
            del adf
        except:
            pass
    # * embaressingly innefficient, but we have 5 minutes between updates.. so nuthin but time :/
    cmd="SET @tots:= 0"
    o.sqlex(cmd)
    cmd=f"UPDATE orders SET fintot = null WHERE session = '{g.session_name}'"
    o.sqlex(cmd)
    cmd=f"UPDATE orders SET runtotnet = credits - fees"
    o.sqlex(cmd)
    cmd=f"UPDATE orders SET fintot = (@tots := @tots + runtotnet) WHERE session = '{g.session_name}'"
    o.sqlex(cmd)

    if g.cvars['display']:
        o.plot_close(ohlc,ax=ax, panel=0, patches = ax_patches)
        o.plot_mavs(ohlc,ax=ax, panel=0, patches = ax_patches)
        o.plot_lowerclose(ohlc,ax=ax, panel=0, patches = ax_patches)
        o.plot_dstot(ohlc,ax=ax, panel=1, patches = ax_patches)



        # * add a grid to all charts
        for i in range(g.num_axes):
            ax[i].grid(True, color='grey', alpha=0.3)

        # * add the legends
        usecolor="olive"
        for i in range(g.num_axes):
            ax[i].set_facecolor("black")
            ax[i].legend(handles=ax_patches[i], loc='upper left', shadow=True, fontsize='x-small')

            ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))
            for label in ax[i].get_xticklabels(which='major'):
                label.set(rotation=12, horizontalalignment='right')

            ax[i].xaxis.label.set_color(usecolor)
            ax[i].yaxis.label.set_color(usecolor)

            ax[i].tick_params(axis='x', colors=usecolor)
            ax[i].tick_params(axis='y', colors=usecolor)

            ax[i].spines['left'].set_color(usecolor)
            ax[i].spines['top'].set_color(usecolor)

            textstr  = f"g.gcounter:   {g.gcounter}\n"
            textstr += "\n"
            textstr += f"g.dstot_Dadj: {g.dstot_Dadj}\n"
            textstr += f"g.dshiamp:    {g.dshiamp:4.2}\n"
            textstr += "\n"
            rem_cd = g.cooldown - g.gcounter
            rem_cd = 0 if rem_cd < 0 else rem_cd
            textstr += f"g.cooldown:   {rem_cd}\n"
            textstr += f"g.long_buys:  {g.long_buys}\n"
            textstr += "\n"
            textstr += f"coverprice:   {g.coverprice:6.2f}\n"
            textstr += f"df[Close]:    {ohlc['Close'][-1]:6.2f}\n"
            pretty_nextbuy = "N/A" if g.next_buy_price > 100000 else f"{g.next_buy_price:6.2f}"
            textstr += f"nextbuy:      {pretty_nextbuy}\n"
            textstr += "\n"
            textstr += f"Net Profit:   ${g.running_total:6.2f}\n"
            textstr += f"Net Capital:  {(g.capital-1)*100:6.2f}%\n"

            props = dict(boxstyle='round', pad = 1, facecolor='black', alpha=1.0)
            ax[1].text(0.05, 0.8, textstr, transform=ax[1].transAxes,  color='wheat', fontsize=10, verticalalignment='top', bbox=props)
            # o.waitfor()

if g.cvars['display']:
    ani = animation.FuncAnimation(fig=fig, func=animate, frames=1086400, interval=g.interval, repeat=False)
    plt.show()
else:
    while True:
        working(0)