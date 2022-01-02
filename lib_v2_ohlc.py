import json
import os
import random
import calendar
import uuid
import sys
import time
import numpy as np
import math
import subprocess
import traceback
from subprocess import Popen
import importlib
import threading
import toml
import MySQLdb as mdb
from scipy import signal
from datetime import datetime
from datetime import timedelta
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.widgets import MultiCursor
from colorama import Fore, Back, Style  # ! https://pypi.org/project/colorama/
import lib_v2_tests_class
import lib_v2_globals as g
import gc
from pathlib import Path
import lib_v2_binance as b
import ccxt
import hashlib

from pprint import pprint


def load_data(t):
    retry = 0
    expass = False

    g.ohlc = get_ohlc(t.since)

    # while not expass or retry < 10:
    #     try:
    #         g.ohlc = get_ohlc(t.since)
    #         retry = 10
    #         expass = True
    #     except Exception as e:
    #         handleEx(e,"in load_data (lib_v2_ohlc:46)")
    #         print(f"Exception error: [{e}]")
    #         print(f'Something went wrong. Error occured at {datetime.now()}. Retrying in 1 minute.')
    #         # * reinstantiate connections in case of timeout
    #         time.sleep(60)
    #         del g.ticker_src
    #         del g.spot_src
    #
    #         g.ticker_src = ccxt.binance({
    #             'enableRateLimit': True,
    #             'timeout': 50000,
    #             'apiKey': g.keys['key'],
    #             'secret': g.keys['secret'],
    #         })
    #         g.ticker_src.set_sandbox_mode(g.keys['testnet'])
    #
    #         retry = retry + 1
    #         expass = False
    return expass, retry

class threadit(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        if self.threadID == "run_exe":
            run_exe()

def rebuild_ax(ax):
    for i in range(g.num_axes):
        ax[i].clear()
        g.ax_patches.append([])
        ax[i].grid(True, color = 'grey', alpha = 0.3)

        try:  # * try because fails onfirst pass only when both vals are equal
            amin = g.ohlc['Timestamp'].head(1)
            amax = g.ohlc['Timestamp'].tail(1)
            ax[0].set_xlim(amin,amax)
        except:
            pass
        ax[i].set_facecolor(g.facecolor)
        ax[i].legend(handles = g.ax_patches[i], loc = 'upper left', shadow = True, fontsize = 'x-small')

        #XXX
        format_str = '%b-%d %Y:%H:%M'
        # g.ohlc.index += pd.DateOffset(days = -10000)
        # format_str = '%b-%d'
        format_ = mdates.DateFormatter(format_str)
        ax[i].xaxis.set_major_formatter(format_)


        for label in ax[i].get_xticklabels(which = 'major'):
            label.set(rotation = 12, horizontalalignment = 'right')
        #
        ax[i].xaxis.label.set_color(g.cvars['figtext']['color'])
        ax[i].yaxis.label.set_color(g.cvars['figtext']['color'])
        #
        ax[i].tick_params(axis = 'x', colors = g.cvars['figtext']['color'])
        ax[i].tick_params(axis = 'y', colors = g.cvars['figtext']['color'])
        #
        ax[i].spines['left'].set_color(g.cvars['figtext']['color'])
        ax[i].spines['top'].set_color(g.cvars['figtext']['color'])


def savefiles():
    # * save a copy of the final data plotted - used for debugging and viewing
    if g.cvars["save"]:
        save_df_json(g.ohlc, "_ohlcdata.json")
        save_df_json(g.df_buysell, "_buysell.json")
        save_everytrx()
        with open(g.statefile, 'w') as outfile:
            json.dump(g.state, outfile, indent = 4)


def get_now():
    return(int(round(time.time() * 1000)))

def report_time(idx,lasttime):
    thistime = get_now()
    dtime = thistime - lasttime
    g.rtime[idx].append(dtime)
    return(dtime)

def make_screens(figure):
    fig = False
    fig2 = False
    ax = [0, 0, 0, 0, 0, 0]
    if g.display:

        # * set up the canvas and windows
        fig = figure(figsize = (g.cvars["figsize"][0], g.cvars["figsize"][1]), dpi = 96)
        fig.patch.set_facecolor('black')

        if g.cvars['2nd_screen']:
            fig2 = figure(figsize = (g.cvars["figsize2"][0], g.cvars["figsize"][1]), dpi = 96)
            fig2.add_subplot(111)
            fig2.patch.set_facecolor('black')

        fig.add_subplot(211)
        fig.add_subplot(212)
        ax = fig.get_axes()

        if g.cvars['2nd_screen']:
            ax2 = fig2.get_axes()
            ax[0] = ax2[0]

        g.num_axes = len(ax)
        MultiCursor(fig.canvas, ax, color = 'r', lw = 1, horizOn = True, vertOn = True)
    return fig, fig2, ax

def get_bigdata():
    datafile = f"{g.cvars['datadir']}/{g.cvars['backtestfile']}"
    g.bigdata = load_df_json(datafile)

    g.bigdata.rename(columns={'Date': 'Timestamp'}, inplace=True)
    g.bigdata['orgClose'] = g.bigdata['Close']
    g.bigdata["Date"] = pd.to_datetime(g.bigdata['Timestamp'], unit='ms')
    g.bigdata['ID'] = range(len(g.bigdata))
    g.bigdata['Type'] = range(len(g.bigdata))
    g.bigdata.index = pd.DatetimeIndex(g.bigdata['Timestamp'])
    g.bigdata.drop_duplicates(subset=None, inplace=True, keep='last')
    g.bigdata = g.bigdata[~g.bigdata.index.duplicated()]  # ! The ONLY w3ay to drop dups when index is datetime

    if g.bigdata.index.is_unique:
        print(f"{datafile}/g.bigdata index is unique")
    else:
        print(f"{datafile}/g.bigdata index is NOT unique. EXITING")
        exit()



def get_sessioname():
    if os.path.isfile('_session_name.txt'):
        with open('_session_name.txt') as f:
            g.session_name = f.readline().strip()
    else:
        g.session_name = get_a_word()
    return(g.session_name)


def convert_price():
    g.ohlc_conv = g.df_priceconversion_data[g.conv_mask]

    if g.ohlc_conv.index.is_unique:
        print("g.ohlc_conv index is unique")
    else:
        print("g.ohlc_conv index is NOT unique. EXITING")
        exit()

    g.bigdata['Open']  = g.bigdata['Open']  * g.ohlc_conv['Open']
    g.bigdata['High']  = g.bigdata['High']  * g.ohlc_conv['High']
    g.bigdata['Low']   = g.bigdata['Low']   * g.ohlc_conv['Low']
    g.bigdata['Close'] = g.bigdata['Close'] * g.ohlc_conv['Close']

def get_priceconversion_data():
    datafile = f"{g.cvars['datadir']}/{g.cvars['backtest_priceconversion']}"
    if g.cvars["convert_price"]:
        g.df_priceconversion_data = load(datafile)

        g.df_priceconversion_data.rename(columns={'Date': 'Timestamp'}, inplace=True)
        g.df_priceconversion_data["Date"] = pd.to_datetime(g.df_priceconversion_data['Timestamp'], unit=g.units)
        g.df_priceconversion_data.index = pd.DatetimeIndex(g.df_priceconversion_data['Timestamp'])

        if g.df_priceconversion_data.index.is_unique:
            print(f"{datafile}/g.df_priceconversion_data index is unique")
        else:
            print(f"{datafile}/g.df_priceconversion_data index is NOT unique. EXITING")
            exit()
        startdate = datetime.strptime(g.startdate, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=g.gcounter * 5)
        g.conv_mask = (g.df_priceconversion_data['Timestamp'] >= startdate)


    datafile = f"{g.cvars['datadir']}/{g.cvars['backtestfile']}"
    g.bigdata = load_df_json(datafile)

    g.bigdata.rename(columns={'Date': 'Timestamp'}, inplace=True)
    g.bigdata['orgClose'] = g.bigdata['Close']
    g.bigdata["Date"] = pd.to_datetime(g.bigdata['Timestamp'], unit=g.units)
    g.bigdata['ID'] = range(len(g.bigdata))
    g.bigdata['Type'] = range(len(g.bigdata))
    g.bigdata.index = pd.DatetimeIndex(g.bigdata['Timestamp'])
    g.bigdata.drop_duplicates(subset=None, inplace=True, keep='last')
    g.bigdata = g.bigdata[~g.bigdata.index.duplicated()]  # ! The ONLY w3ay to drop dups when index is datetime

    if g.bigdata.index.is_unique:
        print(f"{datafile}/g.bigdata index is unique")
    else:
        print(f"{datafile}/g.bigdata index is NOT unique. EXITING")
        exit()


def exec_io(argstr, timeout=10):
    command = argstr.split()
    cp = Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    rs = False
    try:
        output, errors = cp.communicate(timeout=timeout)
        rs = output.strip()
    except Exception as ex:
        cp.kill()
        print("Timed out...")

    if not rs:
        g.logit.info(f"SENT: [{argstr}]")
        g.logit.info(f"RECIEVED: {rs}")
        g.logit.info(f"!!EMPTY RESPONSE!! Exiting:/")
        return False

        # = rs = {
        # = "message": "missing response... continuing",
        # = "settled": True,
        # = "order": "missing",
        # = "resp": ["missing"]
        # = }

    return rs



def adj_startdate(startdate):
    # * adjust startdate so that last date in the array is the startdate
    points = g.cvars['datawindow']
    hours = (points * 5) / 60

    listed_time = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
    virtual_time = listed_time - timedelta(hours=hours)

    return virtual_time.strftime('%Y-%m-%d %H:%M:%S')

def get_secret(**kwargs):
    # exchange = kwargs['provider']
    # apitype = kwargs['apitype']
    # + item = kwargs['item']

    home = str(Path.home())
    secrets_file = f"{home}/.secrets/keys.toml" if os.path.exists(f"{home}/.secrets/keys.toml") else g.cvars['secrets_file']

    data = toml.load(secrets_file)
    # return data[exchange][apitype]
    return data


def load(filename, **kwargs):
    df = pd.read_json(filename, orient='split', compression='infer')
    try:
        g.logit.debug(f"Trimming df to {kwargs['maxitems']}")
        df = df.head(g.cvars["datalength"])
    except:
        pass

    return df

def getdbconn(**kwargs):
    host = "localhost"

    try:
        host = kwargs["host"]
    except:
        pass

    home = str(Path.home())
    # secrets_file = f"{home}/.secrets/keys.toml" if os.path.exists(f"{home}/.secrets/keys.toml") else g.cvars['secrets_file']

    # keys = toml.load(secrets_file)

    # * ccxt doesn't yet support Coinbase ohlcv data, so CB and binance charts will be a little off
    g.keys = get_secret()
    username = g.keys['database']['jmcap']['username']
    password = g.keys['database']['jmcap']['password']

    dbconn = mdb.connect(user=username, passwd=password, host=host, db="jmcap")
    cursor = dbconn.cursor()
    return dbconn, cursor

def get_a_word():
    with open("data/words.txt", "r") as w:
        words = w.readlines()
    i = random.randint(0, len(words) - 1)
    g.session_name = words[i]

    with open("_session_name.txt", "w") as text_file:
        text_file.write(g.session_name)

    return words[i].strip()

def cload(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data

def make_title(**kwargs):
    ft = f"{g.current_close:6.2f} {g.session_name} "
    rpt = f" {g.subtot_qty:8.2f} @ ${g.subtot_cost:8.2f}  ${g.running_total:6.2f}"
    ft = f"{ft} !! {rpt}"
    return ft

def get_latest_time(ohlc):
    return (ohlc['Date'][int(len(ohlc.Date) - 1)])

def state_wr(name, v):
    g.state[name] = v

def state_ap(listname, v):
    if not math.isnan(v):
        g.state[listname].append(v)

def state_r(name, **kwargs):
    fromfile = False
    try:
        fromfile = kwargs['fromfile']
    except:
        pass

    if not fromfile:
        return g.state[name]
    else:
        try:
            with open("state.json") as json_file:
                data = json.load(json_file)

            if type(data[name]) == list:
                data[name] = [x for x in data[name] if np.isnan(x) == False]

            return data[name]
        except:
            print(f"Attempting to read '{name}' from state.json")
            return False

def cclr():
    print(Style.RESET_ALL, end="")
    print(Fore.RESET, end="")
    print(Back.RESET, end="")
def pcCLR():
    return Style.RESET_ALL + Fore.RESET + Back.RESET
def pcDATA():
    return Fore.YELLOW + Style.BRIGHT
def pcINFO():
    return Fore.GREEN + Style.BRIGHT
def pcTEXT():
    return Style.BRIGHT + Fore.WHITE
def pcTOREM():
    return Fore.YELLOW + Back.BLUE + Style.BRIGHT
def pcFROREM():
    return Back.YELLOW + Fore.BLUE + Style.BRIGHT
def pcERROR():
    return Fore.RED + Style.BRIGHT


def handleEx(ex, related):
    print(pcERROR())
    print("───────────────────────────────────────────────────────────────────────")
    print("Related: ", related)
    print("---------------------------------------------------------------------")
    print("Exception: ", ex)
    print("---------------------------------------------------------------------")
    for e in traceback.format_stack():
        print(e)
        print("───────────────────────────────────────────────────────────────────────")
    cclr()
    exit()
    return


def clearstate():

    state_wr('config_file', g.cfgfile)
    state_wr('session_name', g.session_name)
    state_wr('ma_low_holding', False)
    state_wr('ma_low_sellat', 1e+10)
    state_wr("open_buyscanbuy", True)
    state_wr("open_buyscansell", False)

    state_wr("from", False)
    state_wr("to", False)
    state_wr("tot_buys", 0)
    state_wr("tot_sells", 0)
    state_wr("max_qty", 0)
    state_wr("curr_qty", 0)
    state_wr("first_buy_price", 0)
    state_wr("last_buy_price", 1e+10)
    state_wr("next_buy_price", 1e+10)

    state_wr("largest_run_count", 0)
    state_wr("last_run_count", 0)
    state_wr("curr_run_ct", 0)
    state_wr("pnl_running", 0)
    state_wr("pct_running", 0)
    state_wr("order", {})
    state_wr("last_sell_price", 0)
    state_wr("last_avg_price", 0)

    state_wr("avgprice",False),
    state_wr("coverprice",False),
    state_wr("buyunder",False),

    state_wr("max_qty", 0)
    state_wr("curr_qty", 0)
    state_wr("delta_days", 0)
    state_wr("purch_qty", False)

    state_wr('open_buys', [])
    state_wr('qty_holding', [])
    state_wr('buyseries', [])

    state_wr("last_avg_price",float("Nan"))

    state_wr("pnl_running", float("Nan"))
    state_wr("pct_running", float("Nan"))

def loadstate():
    print("RECOVERING...")

    g.session_name = state_r('session_name')
    print("g.session_name",g.session_name)

    g.startdate = state_r("last_seen_date")
    print("g.startdate",g.startdate)

    g.tot_buys = state_r("tot_buys")
    print("g.tot_buys",g.tot_buys)

    g.tot_sells = state_r("tot_sells")
    print("g.tot_sells", g.tot_sells)

    g.curr_run_ct = state_r("curr_run_ct")
    print("g.curr_run_ct", g.curr_run_ct)

    g.subtot_qty = state_r("curr_qty")
    print("g.subtot_qty", g.subtot_qty)

    g.purch_qty = state_r("purch_qty")
    print("g.purch_qty", g.purch_qty)

    g.avg_price = state_r("last_avg_price")
    print("g.avg_price", g.avg_price)

    g.pnl_running = state_r("pnl_running")
    print("g.pnl_running", g.pnl_running)

    g.pct_running = state_r("pct_running")
    print("g.pct_running", g.pct_running)

def waitfor(data=["Here Now"], **kwargs):
    sdata = json.dumps(data)
    print("waiting...\n")
    x=input(sdata)
    if x == "x":
        exit()
    if x == "n":
        return False
    if x == "y":
        return True


def sqlex(cmd, **kwargs):
    ret = "all"
    try:
        ret = kwargs['ret']
    except:
        pass

    g.logit.debug(f"SQL Command:{cmd}")
    rs = False
    # try:
    g.cursor.execute("SET AUTOCOMMIT = 1")
    g.cursor.execute(cmd)
    g.dbc.commit()
    if ret == "all":
        rs = g.cursor.fetchall()
    if ret == "one":
        rs = g.cursor.fetchone()

    # except Exception as ex:
    #     handleEx(ex, cmd)
    #     exit(1)

    return (rs)

def is_epoch_boundry(modby):
    epoch_time = int(time.time())
    g.epoch_boundry_countdown  = epoch_time % modby
    return g.epoch_boundry_countdown % modby

class Times:
    def __init__(self, hours):
        self.since = 60 * 3
        self.current = datetime.now()
        self.__from_now(hours)

    def __from_now(self, hoursback):
        now = datetime.utcnow()
        unixtime = calendar.timegm(now.utctimetuple())
        _min = 60 * hoursback
        since_minutes = _min * 60
        self.since = (unixtime - since_minutes) * 1000  # ! UTC timestamp in milliseconds

def load_df_json(filename, **kwargs):
    df = pd.read_json(filename, orient='split', compression='infer')
    try:
        g.logit.debug(f"Trimming df to {kwargs['maxitems']}")
        newdf = df.head(g.cvars["datalength"])
        del df
        return newdf
    except:
        return df

def save_df_json(df,filename):
    df.to_json(filename, orient='split', compression='infer', index='true')
    del df
    g.logit.debug(f"Saving to file: {filename}")
    gc.collect()


def get_ohlc(since):
    pair = g.cvars["pair"]
    timeframe = g.cvars["timeframe"]
    # + * -------------------------------------------------------------
    # + *  LIVE DATA
    # + * -------------------------------------------------------------
    ohlcv = False
    if g.datatype == "live" or g.datatype == "stream":
        if g.datatype == "live":
            # ! timestamp as 1640731500000
            ohlcv = g.ticker_src.fetch_ohlcv(symbol=pair, timeframe=timeframe, since=since, limit=g.cvars['datawindow'])

        if g.datatype == "stream":
            # + * -------------------------------------------------------------
            # + *  STREAM DATA
            # + * -------------------------------------------------------------
            if g.datatype == "stream":
                filename = '/tmp/_stream_BTCUSDT.json'
                #! timestamp as 1640731763637
                while not os.path.isfile(filename):
                    pass

                while not ohlcv:
                    try:
                        with open(filename) as json_data:
                            ohlcv = json.load(json_data)
                        os.remove(filename)

                        # for i in range(len(ohlcv)):
                        #     ohlcv[i][0] = int(ohlcv[i][0]/1000)
                        break
                    except:
                        pass


        df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        # df.set_index('Timestamp')

#XXX

        df['orgClose'] = df['Close']
        # df["Date"] = pd.to_datetime(df['Timestamp'], unit='ms')
        # df.index = pd.DatetimeIndex(df['Timestamp'])
        g.ohlc = df.loc[:, ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'orgClose']]
        # g.ohlc.to_csv(f"_x1.csv")
        g.ohlc['ID'] = range(len(df))
        g.ohlc["Date"] = pd.to_datetime(g.ohlc['Timestamp'], unit=g.units)
        g.ohlc.index = pd.DatetimeIndex(pd.to_datetime(g.ohlc['Timestamp'], unit=g.units))
        g.ohlc.index.rename("index",inplace=True)
        # g.ohlc.to_csv(f"_x2.csv")

        # g.df_buysell = g.ohlc.copy()
        # g.df_buysell = g.df_buysell.drop(['Open'], axis = 1)

        # print("Timestamp: ",g.ohlc['Timestamp'][-1], "Date", g.ohlc['Date'][-1])


        # g.ohlc.index = g.ohlc['Date']
        # g.ohlc.index += pd.DateOffset(seconds = 0.5)


    # + -------------------------------------------------------------
    # + BACKTEST DATA
    # + -------------------------------------------------------------
    if g.datatype == "backtest":
        startdate = datetime.strptime(g.startdate, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=g.gcounter*5)

        # * g.startdate has already been adjusted, (2020-12-31 00:00:00)
        date_mask = (g.bigdata['Timestamp'] >= startdate)
        g.ohlc= g.bigdata.loc[date_mask].head(g.cvars['datawindow']).copy(deep=True)
        denddate = g.ohlc['Date'][-1]
        dstartdate = g.ohlc['Date'][0]

        tmp = f"  [{g.gcounter}] s:[{dstartdate}]\te:[{denddate}]\tl:[{len(g.ohlc.index)}]"
        g.logit.info(tmp)
        g.ohlc['ID'] = range(len(g.ohlc))

    # * data loaded
    # * save last 2 Close values
    g.this_close = g.ohlc['Close'][-1]
    g.last_close = g.this_close

    dto = f"{max(g.ohlc['Timestamp'])}"  # + * get latest time
    if not state_r("from"):
        state_wr("from", f"{dto}")
    state_wr("last_seen_date", f"{dto}")
    g.can_load = False
    return g.ohlc

def update_legend(ax, idx):
    an = ax[0]
    an.append(mpatches.Patch(color=None, fill=False, label="------------------"))
    return an

def backfill(collected_data, **kwargs):
    fillwith = None
    try:
        fillwith = kwargs['fill']
    except:
        pass

    newary = []
    _tmp = collected_data[::-1]
    # + for i in range(cvars.get('datawindow')):
    i = 0
    while len(newary) < g.datawindow:
        if i < len(_tmp):
            newary.append(_tmp[i])
        else:
            newary.append(fillwith)
        i = i + 1
    return newary[::-1]

def normalize_col(acol, newmin=0.0, newmax=1.0):
    amin = acol.min()
    amax = acol.max()
    # + acol = ((acol-amin)/(amax-amin))*newmax
    acol = ((acol - amin) / (amax - amin)) * (newmax - newmin) + newmin
    return acol

def slope(x1, y1, x2, y2):
  s = (y2-y1)/(x2-x1)
  return s

def make_rohlc(ohlc, **kwargs):
    ohlc["rohlc"] = ohlc["Close"].max() - ohlc["Close"]
    ohlc["rohlc"] = normalize_col(ohlc["rohlc"],ohlc["Close"].min(),ohlc["Close"].max())

def make_sigffmb(ohlc, **kwargs):
    inverted = False  #! JWFIX where is this used?
    basename = "sigffmb"
    basedata = "Close"
    bagbasename = "sigfft"
    try:
        inverted = kwargs['inverted']
        basename = "sigffmb2"
        basedata = "rohlc"
        bagbasename = "sigfft2"
    except:
        pass

    N = g.cvars['mbpfilter']['N']
    Wn_ary = g.cvars['mbpfilter']['Wn']

    for band in range(len(Wn_ary)):
        colname = f'{basename}{band}'
        Wn = Wn_ary[band]
        ohlc[colname] = 0
        b, a = signal.butter(N, Wn, btype="bandpass", analog=False)  # * get filter params
        sig = ohlc[basedata]  # * select data to filter
        sigff = signal.lfilter(b, a, signal.filtfilt(b, a, sig))  # * get the filter
        g.bag[f'{bagbasename}{band}'].append(sigff[len(sigff) - 1])  # * store results in temp location
        ohlc[colname] = backfill(g.bag[f'{bagbasename}{band}'])  # * fill data to match df shape
        ohlc[colname] = normalize_col(ohlc[colname])  # * set all bands to teh same data range

def make_ffmaps(ohlc):
    for band in range(len(g.cvars['mbpfilter']['Wn'])):
        ohlc[f'ffmaps{band}'] = ohlc[f'sigffmb2{band}'] - ohlc[f'sigffmb{band}']

        sy1 = list(ohlc[f'sigffmb{band}'].shift(1).tolist())
        sy2 = list(ohlc[f'sigffmb{band}'].tolist())
        sx1 = list(ohlc['ID'].shift(1).tolist())
        sx2 = list(ohlc['ID'].tolist())

        gs = []
        for i in range(len(sy1)):
            gsx = slope(sx1[i], sy1[i], sx2[i], sy2[i])
            gs.append(gsx)
        ohlc[f'Dsigffmb{band}'] = gs

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    try:
        return math.trunc(stepper * number) / stepper
    except:
        return 0


def make_dstot(ohlc):
    # * get average of last n dstot values
    def davg(ohlc,span):
        do = ohlc['Dstot'].tail(span).tolist()
        dos = 0
        for d in do:
            dos += abs(d)
        # * dstot_Dadj starts as (probably) 0.3, which means incremental in/decreses of 30%
        # * so we need to create a umultiplier by 1 +- 0.3.
        # * the starting dstot-Dadj is 0, meaning a multiplier of 1.
        #* The in/decrement only happens when a long_buy occurs
        dstot_o = (dos / span) * (1+ (g.dstot_Dadj * g.long_buys))
        return(dstot_o)

    tval = 0

    #* loop thru all filters, get the latest sigff slope vals, add them together
    for i in range(len(g.cvars['mbpfilter']['Wn'])):
        tmp = g.ohlc.iloc[-1, g.ohlc.columns.get_loc(f"Dsigffmb{i}")]

        tval = (tval + tmp)

        # * tval = tval * vlist[-1]  # * multiply cum slope by norm vol (0-1), so add 'momentum' to direction
                                     # * 2.1% less queries, 9.6% less profit :(

    # * insert this sum into dstot
    if g.gcounter < g.cvars['dstot_span']:
        g.dstot_ary.insert(0,0)
    else:
        g.dstot_ary.insert(0,tval)

    g.dstot_ary = g.dstot_ary[:g.cvars['datawindow']]

    ohlc['Dstot'] = g.dstot_ary[::-1]  # * need to invert the array to make FIFO -> FILO


    if g.cvars['dstot_relative']:    # * If opted, calc averages
        span=g.cvars['dstot_span']
        dshiamp = abs(davg(ohlc,span))
        dsloamp = dshiamp * -1
    else:                           # * otherwise, cals dstot_lo as the last adjusted dstot val
        span=1
        dshiamp = abs(g.cvars['dstot_buy']*(1 + (g.dstot_Dadj * g.long_buys)))
        dsloamp = dshiamp * -1

    # * we only use teh lo vals, but plot the hi vals just to make the chart more readable

    g.dstot_lo_ary.insert(0,dsloamp)
    g.dstot_hi_ary.insert(0,dshiamp)

    g.dstot_lo_ary = g.dstot_lo_ary[:g.cvars['datawindow']]
    g.dstot_hi_ary = g.dstot_hi_ary[:g.cvars['datawindow']]

    ohlc['Dstot_lo'] = g.dstot_lo_ary[::-1]
    ohlc['Dstot_hi'] = g.dstot_hi_ary[::-1]
    ohlc['Dstot_lo'] = ohlc['Dstot_lo'].ewm(span=span).mean()
    ohlc['Dstot_hi'] = ohlc['Dstot_hi'].ewm(span=span).mean()

def update_db_tots():
    def subthread():
        cmd="SET @tots:= 0"
        sqlex(cmd)
        cmd=f"UPDATE orders SET fintot = null WHERE session = '{g.session_name}'"
        sqlex(cmd)
        cmd=f"UPDATE orders SET runtotnet = credits - fees"
        sqlex(cmd)
        cmd=f"UPDATE orders SET fintot = (@tots := @tots + runtotnet) WHERE session = '{g.session_name}'"
        sqlex(cmd)

    threadit(subthread()).run()

def save_everytrx():
    # * save every transaction
    if g.gcounter == 1:
        header = True
        mode = "w"
    else:
        header = False
        mode = "a"

    g.ohlc.tail(1).to_csv(f"_allrecords.csv", header = header, mode = mode, sep = '\t', encoding = 'utf-8')

    try:
        adf = pd.read_csv(f'_allrecords.csv', chunksize=1000)
        fn = f"_allrecords.json"
        g.logit.debug(f"Save {fn}")
        save_df_json(adf, fn)
        del adf
        gc.collect()
    except:
        pass


def make_lowerclose(ohlc):
    ohlc['lowerClose'] = ohlc['Close'].ewm(span=12).mean() * (1 - g.lowerclose_pct)

def make_mavs(ohlc):
    for m in g.cvars["mavs"]:
        if m["on"]:
            mlen = m['length']
            mnum = m['mavnum']
            colname = f"MAV{mnum}"
            ohlc[colname] = ohlc["Close"].rolling(mlen).mean().values

            g.mav_ary[mnum].insert(0,  ohlc[colname][-1])
            g.mav_ary[mnum] = g.mav_ary[mnum][:g.cvars['datawindow']]
            ohlc[colname] = g.mav_ary[mnum][::-1]



def plot_close(ohlc,**kwargs):
    ax = kwargs['ax']
    panel = kwargs['panel']
    ax_patches = kwargs['patches']
    ax[panel].plot(
        # ohlc['Date'],  #!CRASHES
        # blank           #!CRASHES
        # ohlc['ID'],    #! OK, but bad format
        ohlc['Close'],
        color=g.cvars['styles']['close']['color'],
        linewidth=g.cvars['styles']['close']['width'],
        alpha=g.cvars['styles']['close']['alpha'],
    )
    ax_patches[panel].append(mpatches.Patch(
        color=g.cvars['styles']['close']['color'],
        label="Close"
    ))

def plot_mavs(ohlc,**kwargs):
    ax = kwargs['ax']
    panel = kwargs['panel']
    ax_patches = kwargs['patches']

    for m in g.cvars["mavs"]:
        if m["on"]:
            mnum    = m['mavnum']
            colname = f"MAV{mnum}"

            ax[panel].plot(
                ohlc[colname],
                color       = m['color'],
                linewidth   = m['width'],
                alpha       = m['alpha'],
            )
            ax_patches[0].append(mpatches.Patch(
                color       = m['color'],
                label       = colname))

def plot_MAsn(ohlc, **kwargs):
    ax = kwargs['ax']
    panel = kwargs['panel']
    ax_patches = kwargs['patches']

    for i in range(len(g.cvars["MAsn"])):
        m = g.cvars['MAsn'][i]
        if m["on"]:
            colname = f"MAs{i}"

            ax[panel].plot(
                ohlc[colname],
                color       = m['color'],
                linewidth   = m['width'],
                alpha       = m['alpha'],
            )
            ax_patches[0].append(mpatches.Patch(
                color       = m['color'],
                label       = colname))


def plot_dstot(ohlc,**kwargs):
    ax = kwargs['ax']
    panel = kwargs['panel']
    ax_patches = kwargs['patches']
    ax[panel].tick_params(labelbottom=False)

    ax[panel].plot(
        ohlc['Dstot'],
        color       =g.cvars['styles']['Dstot']['color'],
        linewidth   =g.cvars['styles']['Dstot']['width'],
        alpha       =g.cvars['styles']['Dstot']['alpha'],
    )

    ax[panel].plot(
        ohlc['Dstot_lo'],
        color       ="cyan",
        linewidth   =g.cvars['styles']['Dstot']['width'],
        alpha       =g.cvars['styles']['Dstot']['alpha'],
    )

    ax[panel].plot(
        ohlc['Dstot_hi'],
        color       ="magenta",
        linewidth   =g.cvars['styles']['Dstot']['width'],
        alpha       =g.cvars['styles']['Dstot']['alpha'],
    )

    ax_patches[1].append(mpatches.Patch(
        color=g.cvars['styles']['Dstot']['color'],
        label="Cum Slopes"
    ))
    ax[1].axhline(
        y= ohlc['Dstot_lo'][-1],
        color=g.cvars['styles']['Dstot_lo']['color'],
        linewidth=g.cvars['styles']['Dstot']['width'],
        alpha=g.cvars['styles']['Dstot_lo']['alpha'],
    )
    ax[1].axhline(
        y= ohlc['Dstot_hi'][-1],
        color=g.cvars['styles']['Dstot_hi']['color'],
        linewidth=g.cvars['styles']['Dstot']['width'],
        alpha=g.cvars['styles']['Dstot_hi']['alpha'],
    )

def plot_lowerclose(ohlc,**kwargs):
    ax = kwargs['ax']
    panel = kwargs['panel']
    ax_patches = kwargs['patches']
    ax[panel].plot(
        ohlc['lowerClose'],
        color=g.cvars['styles']['lowerClose']['color'],
        linewidth=g.cvars['styles']['lowerClose']['width'],
        alpha=g.cvars['styles']['lowerClose']['alpha'],

    )
    ax_patches[0].append(mpatches.Patch(
        color=g.cvars['styles']['lowerClose']['color'],
        label="Lower Close"
    ))

def log2file(data,filename):
    if g.cvars['log2file']:
        file1 = open(f"logs/{filename}","a")
        file1.write(f"{data}\n")
        file1.close()


def get_last_price(exchange, **kwargs):
    quiet = False
    try:
        quiet = kwargs['quiet']
    except:
        pass
    if not g.cvars['convert_price']:
        return 1
    pair = g.cvars['price_conversion']
    g.last_conversion = g.conversion
    if g.cvars['offline_price']:                    # * do we want tegh live (slow) price can we live with the fixed (fast) price?
        offprice = g.cvars['offline_price']
        return offprice                             # * if so, retuirn fixed price
    try:                                                # * otherwsie, get the live price
        g.conversion = exchange.fetch_ticker(pair)['last']
        if not quiet:
            g.logit.info(f"Latest conversion rate: {g.conversion}")
        return g.conversion
    except:                                             # * which sometimes craps out
        g.logit.critical("Can't get price from Coinbase.  Check connection?")
        return g.last_conversion                        # * in which case, use last good value


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    try:
        return math.trunc(stepper * number) / stepper
    except:
        return 0

def wavg(shares, prices):
    tot_cost = 0
    adj_tot_cost = 0
    tot_qty = 0
    for i in range(len(shares)):
        adj_price = prices[i] * (1+g.cvars['buy_fee'])
        price = prices[i]
        tot_cost = tot_cost + (price * shares[i])
        adj_tot_cost = adj_tot_cost + (adj_price * shares[i])
        tot_qty = tot_qty + shares[i]
    try:
        avg = tot_cost / tot_qty
        adj_avg = adj_tot_cost / tot_qty
    except:
        avg = tot_cost
        adj_avg = adj_tot_cost

    return tot_cost, tot_qty, avg, adj_tot_cost, adj_avg

def get_running_bal(**kwargs):
    table = "orders"
    version = 2
    ret = "all"
    sname = g.session_name
    profit = False
    try:
        table = kwargs['table']
    except:
        pass
    try:
        version = kwargs['version']
    except:
        pass
    try:
        ret = kwargs['ret']
    except:
        pass
    try:
        sname = kwargs['session_name']
    except:
        pass

    # * verion 1 loops through manually calculatingn buys/sells from the size/qty/side columns
    if version == 1: #!     "buys/sell only",
        cmd = f"select * from {table} where session = '{sname}'"
        rs = sqlex(cmd, ret=ret)
        buys = []  #! JWFIX pre-initialize
        sells = []

        i = 1
        for r in rs:
            aclose = r[g.c_price]
            aside = r[g.c_side]
            aqty = r[g.c_size]
            v =aqty*aclose
            if aside == "buy":
                buys.append(v)
            if aside == "sell":
                sells.append(v)
                profit = sum(sells) - sum(buys)
            i += 1
        return float(profit)

    # * get the last runtotnet (rename? as ths is GROSS , not NET? - JWFIX)
    if version == 2: # ! "sum(netcredits)",
        cmd = f"SELECT sum(netcredits) as profit FROM {table} where session='{sname}'"
        profit = sqlex(cmd, ret="one")
        return profit[0]


    if version == 3: # !     "sum(credits) - sum(fees) - sum(mxint)",
        # * don't need lastid, as we are in the 'sold' space, which means the last order was a sell
        cmd =f"select sum(credits)-sum(fees)-sum(mxint) as totals from {table} where session = '{sname}'"
        profit = sqlex(cmd, ret="one")
        return profit[0]


    if version == 4: # !     "sum(fees) = sum (mxint)"
        profit = sqlex(f"select sum(fees)+sum(mxint) from {table} where session = '{sname}'", ret = "one")
        return profit[0]


def tosqlvar(v):
    r = False
    try:
        x=float(v)
        r = v
    except:
        r = f"'{v}'"
    return r

def update_db(order):
    argstr = ""
    for key in order:
        vnp = f"{key} = {tosqlvar(order[key])}"
        argstr = f"{argstr},{vnp}"

    uid = order['uid']
    cmd = f"insert into orders (uid, session) values ('{uid}','{g.session_name}')"
    sqlex(cmd)
    g.logit.debug(cmd)
    cmd = f"UPDATE orders SET {argstr[1:]} where uid='{uid}' and session = '{g.session_name}'".replace("'None'", "NULL")
    threadit(sqlex(cmd)).run()

    cmd = f"UPDATE orders SET bsuid = '{g.bsuid}' where uid='{uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    credits = order['price'] * order['size']
    if order['side'] == "buy":
        credits = credits * -1

    cmd = f"UPDATE orders SET credits = {credits} where uid='{uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()
    cmd = f"UPDATE orders SET netcredits = credits-fees where uid='{uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    cmd = f"select sum(credits) from orders where bsuid = {g.bsuid} and session = '{g.session_name}'"
    sumcredits = sqlex(cmd)[0][0]

    cmd = f"select sum(fees) from orders where bsuid = {g.bsuid} and  session = '{g.session_name}'"
    try:
        sumcreditsnet = sumcredits - sqlex(cmd)[0][0]
    except: # * if returned NULL
        sumcreditsnet = sumcredits

    cmd = f"UPDATE orders SET runtot = {sumcredits}, runtotnet = {sumcreditsnet} where uid='{uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    g.logit.debug(cmd)
    return


def tryif(src, idx, fallback):
    try:
        rs = src[idx]
    except:
        rs = fallback

    return (rs)

def get_datetime_str():
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_time

def exec_io(argstr, timeout=10):
    command = argstr.split()
    cp = Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    rs = False
    try:
        output, errors = cp.communicate(timeout=timeout)
        rs = output.strip()
    except Exception as ex:
        cp.kill()
        print("Timed out...")

    if not rs:
        g.logit.info(f"SENT: [{argstr}]")
        g.logit.info(f"RECIEVED: {rs}")
        g.logit.info(f"!!EMPTY RESPONSE!! Exiting:/")
        return False

        # = rs = {
        # = "message": "missing response... continuing",
        # = "settled": True,
        # = "order": "missing",
        # = "resp": ["missing"]
        # = }

    return rs


#
# def filter_order(order):
#     tord = {}
#     supported_actions = ['market', 'sellall']
#
#     if supported_actions.count(order['type']) == 0:
#         print(f"{order['type']} not yet supported")
#         exit(1)
#     else:
#         tord['type'] = tryif(order, 'type', False)
#         tord['side'] = tryif(order, 'side', False)
#         tord['pair'] = tryif(order, 'pair', False)
#         tord['size'] = tryif(order, 'size', 0)
#         tord['price'] = tryif(order, 'price', False)
#         tord['stop_price'] = tryif(order, 'stop_price', 0)
#         tord['upper_stop_price'] = tryif(order, 'upper_stop_price', 0)
#
#         tord['funds'] = False
#         tord['uid'] = tryif(order, 'uid', -1)
#
#     tord['state'] = tryif(order, 'state', "UNKNOWN")
#     tord['order_time'] = tryif(order, 'order_time', get_datetime_str())
#
#     tord['pair'] = tord['pair'].replace("/", "-")  # ! adjust for coinbase name
#     # * this converts the field names into the command line switcheS -P, -z, etc
#     argstr = ""
#     for key in tord:
#         if tord[key]:
#             try:
#                 try:  # ! skip over missing g.cflds fields, lile 'state' and 'record_time'
#                     argstr = argstr + f" {g.cflds[key]} {tord[key]}"
#                 except Exception as ex:
#                     pass
#             except KeyError as ex:
#                 handleEx(ex, f"{tord}\n{key}")
#                 exit(1)
#             except Exception as ex:
#                 handleEx(ex, f"{tord}\n{key}")
#                 exit(1)
#
#
#     # ! JWFIX argstr = f"node /home/jw/src/jmcap/v2bot/order_mgr.py {argstr}"
#     return tord, argstr

def calcfees(rs_ary):
    fees = 0
    try:
        for fn in rs_ary['resp']:
            rrec = pd.read_pickle(fn)

            # + pp.pprint(rrec)
            fees = fees + float(rrec['fill_fees'])
    except:
        pass

    return fees

def fix_timestr_for_mysql(ts):
    return

def binance_orders(order):
    success = False
    resp = {'status':-1}
    #* This is what a buy order looks like_
    # = {'order_time': '2021-01-01 02:10:00',
    # =  'type': 'market',
    # =  'pair': 'BTC/USDT',
    # =  'price': 29248.69,
    # =  'limit_price': 29258.69,
    # =  'side': 'buy',
    # =  'size': 0.414,
    # =  'state': 'submitted',
    # =  'uid': '866f90f5c8134cf19b3da8481011c4e4'}

    # tord, argstr = filter_order(order)  # * filters out the unnecessary fields depending on order type

    # * submit order to remote proc, wait for replays


    if g.cvars['offline']:
        if g.cvars['testnet']:
            g.buy_fee = 0
            g.sell_fee = 0

        order['fees'] = 0
        if order['side'] == "buy":
            order['fees'] = (order['size'] * order['price']) * g.buy_fee  # * sumulate fee

        if order['side'] == "sell":
            order['fees'] = (order['size'] * order['price']) * g.sell_fee  # * sumulate fee

        order['session'] = g.session_name
        order['state'] = True
        order['record_time'] = get_datetime_str()
        success = True
    else: #! is live
        # g.logit.info(pcTOREM() + argstr + pcCLR(), extra={'mod_name': 'lib_olhc'})
        # sys.stdout.flush()

        # print(json.dumps(order,indent=4))
        # waitfor()

        if order['type'] == "market" or order['type'] == "sellall" :
            resp = b.market_order(symbol = g.cvars['pair'], type = "market", side = order['side'], amount = order['size'])
        if order['type'] == "limit":
            resp = b.limit_order(symbol = g.cvars['pair'], type = "limit", side = order['side'], amount = order['size'], price=order['limit_price'])

        if resp['status'] != 0:
            b.Eprint("ERROR (see 'logs/trx.log') CONTINUING (until next sell: ", end="")
            if resp['return'] == "binance Account has insufficient balance for requested action.":
                b.Eprint(f"Insufficient balance: CURRENT {g.BASE} BALANCE: [{b.get_balance(base = g.BASE)['free']}]")
                log2file(f"CURRENT {g.QUOTE} BALANCE: [{b.get_balance(base = g.QUOTE)['free']}]", "trx.log")
                log2file(f"{order['size']} * {order['price']} = {order['size'] * order['price']}", "trx.log")
            log2file(json.dumps(resp, indent = 4), "trx.log")
            log2file(json.dumps(order, indent = 4), "trx.log")
        else:
            # = {'return': {'amount': 0.00413,
            # =             'average': 47658.79,
            # =             'clientOrderId': 'x-R4BD3S827f5fa77cc83ea43eb1d9cc',
            # =             'cost': 196.8308027,
            # =             'datetime': '2021-12-28T23:14:27.994Z',
            # =             'fee': {'cost': 0.0, 'currency': 'BTC'},
            # =             'fees': [{'cost': 0.0, 'currency': 'BTC'}],
            # =             'filled': 0.00413,
            # =             'id': '9198227',
            # =             'info': {'clientOrderId': 'x-R4BD3S827f5fa77cc83ea43eb1d9cc',
            # =                      'cummulativeQuoteQty': '196.83080270',
            # =                      'executedQty': '0.00413000',
            # =                      'fills': [{'commission': '0.00000000',
            # =                                 'commissionAsset': 'BTC',
            # =                                 'price': '47658.79000000',
            # =                                 'qty': '0.00413000',
            # =                                 'tradeId': '2121284'}],
            # =                      'orderId': '9198227',
            # =                      'orderListId': '-1',
            # =                      'origQty': '0.00413000',
            # =                      'price': '0.00000000',
            # =                      'side': 'BUY',
            # =                      'status': 'FILLED',
            # =                      'symbol': 'BTCUSDT',
            # =                      'timeInForce': 'GTC',
            # =                      'transactTime': '1640733267994',
            # =                      'type': 'MARKET'},
            # =             'lastTradeTimestamp': None,
            # =             'postOnly': False,
            # =             'price': 47658.79,
            # =             'remaining': 0.0,
            # =             'side': 'buy',
            # =             'status': 'closed',
            # =             'stopPrice': None,
            # =             'symbol': 'BTC/USDT',
            # =             'timeInForce': 'GTC',
            # =             'timestamp': 1640733267994,
            # =             'trades': [{'amount': 0.00413,
            # =                         'cost': 196.8308027,
            # =                         'datetime': None,
            # =                         'fee': {'cost': 0.0, 'currency': 'BTC'},
            # =                         'id': '2121284',
            # =                         'info': {'commission': '0.00000000',
            # =                                  'commissionAsset': 'BTC',
            # =                                  'price': '47658.79000000',
            # =                                  'qty': '0.00413000',
            # =                                  'tradeId': '2121284'},
            # =                         'order': '9198227',
            # =                         'price': 47658.79,
            # =                         'side': 'buy',
            # =                         'symbol': 'BTC/USDT',
            # =                         'takerOrMaker': None,
            # =                         'timestamp': None,
            # =                         'type': 'market'}],
            # =             'type': 'market'},
            # =  'status': 0}

            order['fees'] = resp['return']['fee']['cost']
            order['session'] = g.session_name
            order['state'] = resp['return']['status']
            order['record_time'] =  get_datetime_str() #! JWFIX  use fix_timestr_for_mysql() /// resp['return']['datetime']
            success = True

        #
    update_db(order)
    return success


# def coinbase_orders(order, **kwargs):
#     tord, argstr = filter_order(order)  # * filters out the unnecessary fields depending on order type
#
#     # * submit order to remote proc, wait for replays
#
#     if g.cvars['offline']:
#         tord['fees'] = 0
#         # ! these vals are takes from the empircal number of the CB dev sandbox transactions
#         if order['side'] == "buy":
#             tord['fees'] = (order['size'] * order['price']) * g.buy_fee  # * sumulate fee
#
#         if order['side'] == "sell":
#             tord['fees'] = (order['size'] * order['price']) * g.sell_fee  # * sumulate fee
#
#         tord['session'] = g.session_name
#         tord['state'] = True
#         tord['record_time'] = get_datetime_str()
#     else:
#         g.logit.info(pcTOREM() + argstr + pcCLR(), extra={'mod_name': 'lib_olhc'})
#         sys.stdout.flush()
#
#         # - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#
#         # ! This is where the data from cb_order.py is returned as an array (json serialized)...
#         # ! in cb_order.py teh array is called 'rs_ary', and it si the last output of the program
#         # = Because the objecss returned from coinbase, or any array that has Decimal types, can't be serialized,
#         # = the pickled objects are saved as files, and these input_filenames are return in rs_ary
#         # - {
#         # -     "message": "Settled after 1 attempt",
#         # -     "settled": true,
#         # -     "order": "records/B_1635517292.ord",
#         # -     "resp": [
#         # -         "records/B_1635517292.ord.r_0"
#         # -     ]
#         # - }
#
#         ufn = exec_io(argstr)
#         if not ufn:
#             return False
#
#         # - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#
#         g.logit.info(pcFROREM() + ufn + pcCLR(), extra={'mod_name': 'lib_olhc'})
#         cclr()
#         try:
#             rs_ary = json.loads(ufn)  # * load the array of pickled files
#             rs_order = pd.read_pickle(rs_ary['order'])
#             fees = 0
#             for r in rs_ary['resp']:
#                 rs_resp = pd.read_pickle(r)
#                 try:
#                     fees = fees + float(rs_resp['fill_fees'])
#                 except Exception as ex:
#                     pass
#             tord['fees'] = calcfees(rs_ary)
#             tord['session'] = g.session_name
#             tord['state'] = rs_order["settled"]
#             tord['record_time'] = get_datetime_str()
#         except Exception as ex:
#             handleEx(ex, f"len(ufn)={len(ufn)}")
#             g.logit.info(pcFROREM() + ufn + pcCLR())
#
#     update_db(tord)
#     return True

def get_est_sell_fee(subtot_cost):
    if g.cvars['testnet']:
        return 0
    else:
        return subtot_cost * g.cvars['sell_fee']


def get_est_buy_fee(BUY_PRICE):
    if g.cvars['testnet']:
        return 0
    else:
        return (g.purch_qty * BUY_PRICE) * g.cvars['buy_fee']

# - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

def process_buy(**kwargs):
    ax = kwargs['ax']
    BUY_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    def tots(dfline):
        m = float("Nan")
        # * if there is a BUY and not a SELL, add the subtot as a neg value
        if not math.isnan(dfline['buy']) and math.isnan(dfline['sell']):
            m = dfline['buy'] * -1
            # * if there is a SELL and not a BUY, add the subtot as a pos value
        if not math.isnan(dfline['sell']) and math.isnan(dfline['buy']):
            m = dfline['sell']
        rs = m * dfline['qty']
        return (rs)

    if g.curr_run_ct == 0:
        g.session_first_buy_time = g.ohlc['Date'][-1]

    g.stoplimit_price = BUY_PRICE * (1 - g.cvars['sell_fee'])

    # * show on chart we have something to sell
    if g.cvars['display']:
        g.facecolor = g.cvars['styles']['buyface']['color']
        # ax.set_facecolor(g.cvars['styles']['buyface']['color'])
    # * first get latest conversion price
    g.conversion = get_last_price(g.spot_src, quiet=True)


    # * we are in, so reset the buy signal for next run
    g.external_buy_signal = False

    # * calc new subtot and avg
    # ! need to add current price and qty before doing the calc

    # * these list counts are how we track the total number of purchases since last sell
    state_ap('open_buys', BUY_PRICE)  # * adds to list of purchase prices since last sell
    state_ap('qty_holding', g.purch_qty)  # * adds to list of purchased quantities since last sell, respectfully

    # * calc avg price using weighted averaging, price and cost are [list] sums

    g.subtot_cost, g.subtot_qty, g.avg_price, g.adj_subtot_cost, g.adj_avg_price = wavg(state_r('qty_holding'), state_r('open_buys'))

    state_wr("last_avg_price", g.avg_price)
    state_wr("last_adj_avg_price", g.avg_price)

    # * update the buysell records
    g.df_buysell['subtot'] = g.df_buysell.apply(lambda x: tots(x), axis=1)  # * calc which col we are looking at and apply accordingly

    # print(g.ohlc.index[0])

    # * 'convienience' vars,
    bv = df['bb3avg_buy'].iloc[-1]  # * gets last buy
    sv = df['bb3avg_sell'].iloc[-1]  # * gets last sell
    tv = df['Timestamp'].iloc[-1]  # * gets last timestamp

    # * insert latest data into df, and outside the routibe we shift busell down by 1, making room for next insert as loc 0
    g.df_buysell['buy'].iloc[0] = BUY_PRICE
    g.df_buysell['qty'].iloc[0] = g.purch_qty
    g.df_buysell['Timestamp'].iloc[0] = tv  # * add last timestamp tp buysell record

    # * increment run counter and make sure the historical max is recorded
    g.curr_run_ct = g.curr_run_ct + 1
    state_wr("curr_run_ct", g.curr_run_ct)

    # * track ongoing number of buys since last sell
    g.curr_buys = g.curr_buys + 1

    # * update buy count ans set permissions
    g.buys_permitted = False if g.curr_buys >= g.cvars['maxbuys'] else True

    # * save useful data in state file
    state_wr("last_buy_date", f"{tv}")
    state_wr("curr_qty", g.subtot_qty)

    if g.is_first_buy:
        state_wr("first_buy_price", BUY_PRICE)
        g.is_first_buy = False
    state_wr("last_buy_price", BUY_PRICE)

    #! pre-calc coverprice for limit order to cover cost
    PRE_est_buy_fee = get_est_buy_fee(BUY_PRICE)
    PRE_running_buy_fee = g.running_buy_fee + PRE_est_buy_fee
    PRE_est_sell_fee = get_est_sell_fee(g.subtot_cost)
    PRE_total_fee = PRE_running_buy_fee + PRE_est_sell_fee
    PRE_covercost = PRE_total_fee * (1 / g.subtot_qty)
    PRE_coverprice = PRE_covercost + g.avg_price
    # ! --------------------------------------------------
    # * create a BUY order
    order = {}
    order["pair"] = g.cvars["pair"]
    # = order["funds"] = False
    order["side"] = "buy"
    order["size"] = truncate(g.purch_qty, 5) #! JWFIX use 'precision' function
    order["price"] = BUY_PRICE
    order["type"] = "market"
    order["limit_price"] = PRE_coverprice
    # = order["stop_price"] = CLOSE * 1/cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["uid"] = g.uid
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    state_wr("order", order)

    # print("PRE_coverprice",PRE_coverprice)

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    rs = binance_orders(order) # * BUY
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    if not rs:
        # * order failed -  return nothing and wait for next loop
        return float("Nan")

    # ! trx OK, so continue as normal
    # * calc total cost this run
    qty_holding_list = state_r('qty_holding')
    open_buys_list = state_r('open_buys')

    # * calc current total cost of session
    sess_cost = 0
    for i in range(len(qty_holding_list)):
        sess_cost = sess_cost + (open_buys_list[i] * qty_holding_list[i])

    g.est_buy_fee = get_est_buy_fee(BUY_PRICE)
    g.running_buy_fee = g.running_buy_fee + g.est_buy_fee
    g.est_sell_fee = get_est_sell_fee(g.subtot_cost)

    # * this is the total fee in dollars amount
    total_fee = g.running_buy_fee + g.est_sell_fee
    # * to calculate the closing price necessary to cover this cost
    # * we have to calculate the $ value as a % of the unit cost.
    # * example...
    # * if fee is 10%, and price is $100, and we purchased 0.5,
    # * than the cover cost is (100*0.5)*0.10=5. to make that 5 we
    # * we need to sell as 110, as we only have 0.5 shares.  So the
    # * we need need to calc the minimum closing price as
    # * 5 * (1/qty), whish gives us
    # * 5 * (1/qty) = 5*(1/.5)=5*2=10 plus the original cost
    # * 100 = 110
    g.covercost = total_fee * (1 / g.subtot_qty)
    g.coverprice = g.covercost + g.avg_price
    # ! -------------------------------------------------

    # print("g.coverprice",g.coverprice)

    # print("..........................................")
    # print(f"running total buy fee: {g.running_buy_fee}")
    # print(f"total sell fee: {g.est_sell_fee}")
    # print(f"total fee: {total_fee}")
    # print(f"purch qty: {g.subtot_qty}")
    # print(f"current average: {g.avg_price}")
    # print(f"virt covercost: {g.covercost}")
    # print(f"coverprice: {g.coverprice}")
    # print(f"close: {BUY_PRICE}")
    # print(f"avg price: {g.avg_price}")
    # print("------------------------------------------")
    # waitfor()

    if g.buymode == "D":
        state_ap("buyseries", 1)
        # * if we are in 'Dribble' mode, we want to increase buys, so we keep the dstot_lo mark loose
        g.dstot_Dadj = 0

    if g.buymode == "L":
        state_ap("buyseries", 0)
        g.long_buys += 1
        # * Once in "Long" mode, we increase the marker to reduce buys so as not to use up all our resource_cap on long valleys
        # * this is deon by rasing tehg percentage incrementer
        g.dstot_Dadj = g.cvars['dstot_Dadj'] * g.long_buys

    # * print to console
    str = []
    str.append(f"[{g.gcounter:05d}]")
    str.append(f"[{order['order_time']}]")

    if g.cvars['convert_price']:
        ts = list(g.ohlc_conv[(g.ohlc_conv['Date'] == order['order_time'])]['Close'])[0]
    else:
        ts = order['order_time'][0]

    cmd = f"UPDATE orders set SL = '{g.buymode}' where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # * make pretty strings
    s_size = f"{order['size']:,.5f}"
    s_price = f"{BUY_PRICE:,.2f}"
    s_cost = f"{order['size'] * BUY_PRICE:,.2f}"


    str.append(f"[{ts}]")
    str.append(Fore.RED + f"Hold [{g.buymode}] " + Fore.CYAN + f"{s_size} @ ${s_price} = ${s_cost}" + Fore.RESET)
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price:,.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"COV: " + Fore.CYAN + Style.BRIGHT + f"${g.coverprice:,.2f}" + Style.RESET_ALL)
    str.append(Fore.RED + f"Fee: " + Fore.CYAN + f"${g.est_buy_fee:,.2f}" + Fore.RESET)
    str.append(Fore.RED + f"QTY: " + Fore.CYAN + f"{g.subtot_qty:6.4f}" + Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)
    log2file(iline,"ansi.txt")

    state_wr("open_buyscansell", True)

    return BUY_PRICE

# - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

def process_sell(**kwargs):
    SELL_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    # * reset to original limits
    g.long_buys = 0
    g.dstot_Dadj = 0
    g.since_short_buy = 0
    g.short_buys = 0
    # * all cover costs incl sell fee were calculated in buy
    if g.cvars['display']:
        g.facecolor = "black"

    g.deltatime = (g.ohlc['Date'][-1] - g.session_first_buy_time).total_seconds()/86400

    # * first get latest conversion price
    g.conversion = get_last_price(g.spot_src)

    g.cooldown = 0                  # * reset cooldown
    g.buys_permitted = True  # * Allows buys again
    g.external_sell_signal = False  # * turn off external sell signal
    state_wr("last_buy_price", 1e+10)

    # * update buy counts
    g.tot_buys = g.tot_buys + g.curr_buys
    g.curr_buys = 0
    state_wr("tot_buys", g.tot_buys)

    # * reset ffmaps lo limit
    # * set new low threshholc
    g.ffmaps_lothresh = g.cvars['ffmaps_lothresh']
    state_wr("buyseries", [])

    # * calc new data.  g.subtot_qty is total holdings set in BUY routine
    g.subtot_value = g.subtot_qty * SELL_PRICE

    # * calc pct gain/loss relative to invesment, NOT capital
    g.last_pct_gain = ((g.subtot_value - g.subtot_cost) / g.subtot_cost) * 100

    g.curr_run_ct = 0  # + * clear current count

    # * recalc max_qty, comparing last to current, and saving max, then reset
    this_qty = state_r("max_qty")
    state_wr("max_qty", max(this_qty, g.subtot_qty))
    state_wr("curr_qty", 0)

    # * update buysell record
    tv = df['Timestamp'].iloc[-1]

    g.df_buysell['subtot'].iloc[0] = (g.subtot_cost)
    g.df_buysell['qty'].iloc[0] = g.subtot_qty
    g.df_buysell['pnl'].iloc[0] = g.pnl_running
    g.df_buysell['pct'].iloc[0] = g.pct_running
    g.df_buysell['sell'].iloc[0] = SELL_PRICE
    g.df_buysell['Timestamp'].iloc[0] = tv

    # * record last sell time as 'to' field
    state_wr("to", f"{tv}")

    # * turn off 'can sell' flag, as we have nothing more to see now
    state_wr("open_buyscansell", False)

    # * record total number of sell and latest sell price
    g.tot_sells = g.tot_sells + 1
    state_wr("tot_sells", g.tot_sells)
    state_wr("last_sell_price", SELL_PRICE)

    # * create SELL order
    order = {}
    order["type"] = "sellall"
    # = order["funds"] = False
    order["side"] = "sell"
    order["size"] = truncate(g.subtot_qty, 5) #! JWFIX replace with ccxt 'toprecision'
    order["price"] = SELL_PRICE #! JWFIX check for ccxt 'toprecision'
    # = order["stop_price"] = CLOSE * 1 / cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["pair"] = g.cvars["pair"]
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    order["uid"] = g.uid  # g.gcounter #get_seconds_now() #! we can use g.gcounter as there is only 1 DB trans per loop
    state_wr("order", order)

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    rs = binance_orders(order) # * SELL
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    # rs = coinbase_orders(order)
    # * order failed
    if not rs:
        return float("Nan")
    # * sell all (the default sell strategy) and clear the counters
    state_wr('open_buys', [])
    state_wr('qty_holding', [])

    # * cals final cost and sale of session
    purchase_price = g.subtot_cost
    sold_price = g.subtot_qty * SELL_PRICE

    g.margin_interest_cost          = ((g.cvars['margin_int_pt'] * g.deltatime) * g.subtot_cost)
    g.total_margin_interest_cost    = g.total_margin_interest_cost + g.margin_interest_cost

    cmd = f"UPDATE orders set mxint = {g.margin_interest_cost}, mxinttot={g.total_margin_interest_cost} where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # * calc running total (incl fees)
    g.running_total = get_running_bal(version=3, ret='one')
    s_running_total = f"{g.running_total:,.2f}"

    # * (INCL FEES)

    # - EXAMPLE... buy at 10, sell at 20, $1 fee
    # - (20-(10+1))/20
    # - (20-11)/20
    # - 9/20
    # - 0.45  = 45% = profit margin
    # - 20 * (1+.50) = 29 = new amt cap
    g.pct_return = (sold_price - (purchase_price + g.covercost)) / sold_price  # ! x 100 for actual pct value
    if math.isnan(g.pct_return):
        g.pct_return = 0

    # * print to console
    g.running_buy_fee               = g.subtot_cost * g.cvars['buy_fee']
    g.est_sell_fee                  = g.subtot_cost * g.cvars['sell_fee']
    sess_gross                      = (SELL_PRICE - g.avg_price) * g.subtot_qty
    sess_net                        = sess_gross - (g.running_buy_fee + g.est_sell_fee)
    total_fee                       = g.running_buy_fee + g.est_sell_fee
    g.covercost                     = (total_fee * (1 / g.subtot_qty)) +g.margin_interest_cost
    g.coverprice                    = g.covercost + g.avg_price

    g.total_reserve     = (g.capital * g.this_close)
    g.pct_cap_return    = (g.running_total / (g.total_reserve))#! JWFIX (sess_net / (g.cvars['reserve_cap'] * SELL_PRICE))


    # print(f"{g.pct_cap_return} = {g.running_total} / ({g.total_reserve}")

    g.pct_capseed_return    = (g.running_total/ (g.cvars['reserve_seed'] * g.this_close))#(sess_net / (g.cvars['reserve_cap'] * SELL_PRICE))

    s_size  = f"{order['size']:,.5f}"
    s_price = f"{SELL_PRICE:,.2f}"
    s_tot   = f"{g.subtot_qty * SELL_PRICE:,.2f}"

    # * update DB with pct
    cmd = f"UPDATE orders set pct = {g.pct_return}, cap_pct = {g.pct_cap_return} where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # * DEBUG - print to console
    # g.running_buy_fee = g.subtot_cost * cvars.get('buy_fee')
    # g.est_sell_fee = g.subtot_cost * cvars.get('sell_fee')
    # sess_gross = (SELL_PRICE -g.avg_price) * g.subtot_qty
    # sess_net =  sess_gross - (g.running_buy_fee+g.est_sell_fee)
    # total_fee = g.running_buy_fee+g.est_sell_fee
    # g.covercost = total_fee * (1/g.subtot_qty)
    # g.coverprice = g.covercost + g.avg_price

    # print("..........................................")
    # print(f"running total buy fee: {g.running_buy_fee}")
    # print(f"total sell fee: {g.est_sell_fee}")
    # print(f"total fee: {total_fee}")
    # print(f"purch qty: {g.subtot_qty}")
    # print(f"current average: {g.avg_price}")
    # print(f"virt covercost: {g.covercost}")
    # print(f"coverprice: {g.coverprice}")
    # print(f"close: {SELL_PRICE}")
    # print(f"avg price: {g.avg_price}")
    # print(f"gross profit: {sess_gross}")
    # print(f"net profit: {sess_gross - total_fee}")
    # print("------------------------------------------")
    # waitfor()

    dtime = (timedelta(seconds=int((get_now() - g.last_time)/1000)))

    str = []
    str.append(f"[{g.gcounter:05d}]")
    str.append(f"[{order['order_time']}]")
    str.append(Fore.GREEN + f"Sold    " + f"{s_size} @ ${s_price} = ${s_tot}")
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price:,.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"Fee: " + Fore.CYAN + Style.BRIGHT + f"${g.est_sell_fee:,.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessGross: " + Fore.CYAN + Style.BRIGHT + f"${sess_gross:,.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessFee: " + Fore.CYAN + Style.BRIGHT + f"${g.covercost:,.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessNet: " + Fore.CYAN + Style.BRIGHT + f"${sess_net:,.2f}" + Style.RESET_ALL)
    str.append(Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)
    log2file(iline,"ansi.txt")


    # \f"[{g.gcounter:05d}] [{order['order_time']}] "+
    # =      Fore.GREEN + f"Sold {s_size} @ ${s_price} = ${s_tot}    PnL: ${(g.subtot_qty * SELL_PRICE) - g.subtot_cost:06.4f}  Fee: ${est_fee:3.2f}  TFee: ${total_fees_to_cover:3.2f}  AVG: ${g.avg_price:6.2f} "+Fore.RESET)

    # g.capital = g.capital + (g.capital * (g.pct_cap_return))
    # print(f"{g.capital}  * 1+{g.pct_cap_return}")

    # g.capital = g.capital * (1 + g.pct_cap_return) # ! JWFIX cap return is wrong? use reserve / running totel

    # total_reserve = (g.cvars['reserve_cap'] * g.this_close)
    # pctr = (g.running_total/total_reserve)*100

    g.cap_seed =  g.cap_seed + (sess_net/g.this_close)
    g.capital= g.cap_seed * g.cvars['margin_x']

    new_cap = g.running_total
    new_cap_mx = new_cap * g.cvars['margin_x']

    # g.capital = g.capital + new_cap_mx
    # g.capital = g.capital * (1 + (g.pct_cap_return)) # ! JWFIX cap return is wrong? use reserve / running totel


    str = []
    str.append(f"{Back.YELLOW}{Fore.BLACK}")
    str.append(f"[{dfline['Date']}]")
    str.append(f"({g.session_name}/{dtime})")
    str.append(f"NEW CAP AMT: " + Fore.BLACK + Style.BRIGHT + f"{g.capital:6.5f} ({g.cap_seed:6.4f})" + Style.NORMAL)
    str.append(f"Running Total:" + Fore.BLACK + Style.BRIGHT + f" ${s_running_total}" + Style.NORMAL)

    str.append(f"{Back.RESET}{Fore.RESET}")
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)
    log2file(iline,"ansi.txt")

    # * reset average price
    g.avg_price = float("Nan")

    g.bsuid         = g.bsuid + 1
    g.subtot_qty    = 0

    return SELL_PRICE

def trigger(ax):
    cols = g.ohlc['ID'].max()
    g.current_close = g.ohlc.iloc[len(g.ohlc.index)-1]['Close']

    def tfunc(dfline, **kwargs):
        action = kwargs['action']
        df = kwargs['df']
        g.idx = dfline['ID']
        CLOSE = dfline['Close']

        # + -------------------------------------------------------------------
        # + BUY
        # + -------------------------------------------------------------------
        is_a_buy = True
        is_a_sell = True

        if action == "buy":
            if g.idx == cols:  # * idx is the current index of rfow, cols is max rows... so only when arrived at last row
                # * load the test class
                importlib.reload(lib_v2_tests_class)
                tc = lib_v2_tests_class.Tests(g.cvars, dfline, df, idx=g.idx)

                PASSED = tc.buytest(g.cvars['testpair'][0])

                is_a_buy = is_a_buy and PASSED or g.external_buy_signal
                is_a_buy = is_a_buy and g.buys_permitted       # * we haven't reached the maxbuy limit yet

                # * BUY is approved, so check that we are not runnng hot
                g.uid = uuid.uuid4().hex

                # * make sure we have enough to cover
                checksize = g.subtot_qty + g.purch_qty
                havefunds = checksize < g.reserve_cap
                can_cover = True
                if not havefunds:
                    can_cover = False
                    print(f"Insuficient Funds")

                is_a_buy = is_a_buy and (havefunds or can_cover)
                is_a_buy = is_a_buy and (g.gcounter >= g.cooldown and g.gcounter > 12)

                if is_a_buy:
                    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

                    if g.buymode == 'S':
                        g.purch_qty = g.cvars['short_purch_qty']

                    if g.buymode == 'L':
                        g.purch_qty = g.cvars['long_purch_qty'] * 1.618**g.long_buys

                        # * set cooldown by setting the next gcounter number that will freeup buys
                        # ! cooldown is calculated by adding the current g.gcounter counts and adding the g.cooldown
                        # ! value to arrive a the NEXT g.gcounter value that will allow buys.
                        # ! g.cooldown holds the number of buys
                        g.cooldown = g.gcounter + (
                                    g.cvars['cooldown_mult'] * (g.long_buys + 1))

                    state_wr("purch_qty", g.purch_qty)

                    BUY_PRICE = process_buy(ax=ax, CLOSE=CLOSE, df=df, dfline=dfline)
                    # * update state file
                    state_wr("purch_qty", g.purch_qty)

                # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

                else:
                    BUY_PRICE = float("Nan")

            else:
                BUY_PRICE = float("Nan")
            return BUY_PRICE

        # + -------------------------------------------------------------------
        # + SELL
        # + -------------------------------------------------------------------
        if action == "sell":
            if g.idx == cols and state_r("open_buyscansell"):
                # * first we check is we need to apply stop-limit rules
                limitsell = False
                # print(f":: {CLOSE} - {g.stoplimit_price}")
                if CLOSE <= g.stoplimit_price and g.cvars['maxbuys'] == 1:
                    print(f"STOP LIMIT OF {g.stoplimit_price}!")
                    limitsell = True
                    g.external_sell_signal = True
                # * next we check if if we have reached any sell conditions
                # if g.since_short_buy > g.cvars['first_short_buy_release_pts']:
                #     g.external_sell_signal = True

                importlib.reload(lib_v2_tests_class)
                tc = lib_v2_tests_class.Tests(g.cvars, dfline, df, idx=g.idx)

                PASSED = tc.selltest(g.cvars['testpair'][1])
                is_a_sell = is_a_sell and PASSED or g.external_sell_signal

                if is_a_sell:
                    g.uid = uuid.uuid4().hex
                    if limitsell:
                        SELL_PRICE = process_sell(ax=ax, CLOSE=g.stoplimit_price, df=df, dfline=dfline)
                        g.stoplimit_price = 1e-10
                    else:
                        SELL_PRICE = process_sell(ax=ax, CLOSE=CLOSE, df=df, dfline=dfline)
                    os.system("touch /tmp/_sell")
                    g.covercost = 0
                    g.running_buy_fee = 0
                    update_db_tots()  # * update 'fintot' and 'runtotnet' in db
                else:
                    SELL_PRICE = float("Nan")
            else:
                SELL_PRICE = float("Nan")

            return SELL_PRICE
        return float("Nan")

    if len(g.ohlc) != len(g.df_buysell.index):
        waitfor([f"End of data (index mismatch.  expecting {len(g.ohlc)}, got {len(g.df_buysell.index)})"])

    g.ohlc['ID'] = range(len(g.ohlc))
    g.df_buysell['ID'] = range(len(g.ohlc))

    g.ohlc["bb3avg_buy"] = float("Nan")
    g.ohlc["bb3avg_sell"] = float("Nan")

    g.df_buysell = g.df_buysell.shift(periods=1)

    try:
        g.df_buysell.index = pd.DatetimeIndex(pd.to_datetime(g.df_buysell['Timestamp'], unit = g.units))
    except:
        g.df_buysell.index = pd.DatetimeIndex(pd.to_datetime(g.df_buysell['Timestamp']))

    g.df_buysell.index.rename("index", inplace = True)


    # ! add new data to first row
    g.ohlc['bb3avg_sell'] = g.ohlc.apply(lambda x: tfunc(x, action="sell", df=g.ohlc, ax=ax), axis=1)
    g.ohlc['bb3avg_buy'] = g.ohlc.apply(lambda x: tfunc(x, action="buy", df=g.ohlc, ax=ax), axis=1)

    state_wr("avgprice",g.avg_price),
    state_wr("coverprice",g.avg_price + g.covercost),
    state_wr("buyunder",g.next_buy_price),

    if g.avg_price > 0:
        if g.cvars['display'] and not g.headless:
            ax.axhline(
                g.avg_price,
                color       = g.cvars['styles']['avgprice']['color'],
                linewidth   = g.cvars['styles']['avgprice']['width'],
                alpha       = g.cvars['styles']['avgprice']['alpha']
            )
            ax.axhline(
                g.avg_price + g.covercost,
                color       = g.cvars['styles']['coverprice']['color'],
                linewidth   = g.cvars['styles']['coverprice']['width'],
                alpha       = g.cvars['styles']['coverprice']['alpha']
            )
            if g.next_buy_price < 1000000 and g.next_buy_price > 0:
                ax.axhline(
                    g.next_buy_price,
                    color       = g.cvars['styles']['buyunder']['color'],
                    linewidth   = g.cvars['styles']['buyunder']['width'],
                    alpha       = g.cvars['styles']['buyunder']['alpha']
                )

    tmp = g.df_buysell.iloc[::-1].copy() # ! here we have to invert the array to get the correct order
    #XXX


    # tmp.set_index(['Timestamp'], inplace=True)

    bDtmp = tmp[tmp['mclr']!=0]
    bLtmp = tmp[tmp['mclr']!=1]

    colors = ['blue' if val == 1 else 'red' for val in tmp["mclr"]]
    tmp['color'] = colors

    save_df_json(bLtmp,"_bLtmp.json")
    save_df_json(bDtmp,"_bDtmp.json")  # ! short

    if g.cvars['display'] and not g.headless:
        ax.plot(bDtmp['buy'], color=g.cvars['buy_marker']['S']['color'], markersize=g.cvars['buy_marker']['S']['size'], alpha=g.cvars['buy_marker']['S']['alpha'],  marker=6)  # + ^
        ax.plot(bLtmp['buy'], color=g.cvars['buy_marker']['L']['color'], markersize=g.cvars['buy_marker']['L']['size'], alpha=g.cvars['buy_marker']['L']['alpha'],  marker=6)  # + ^
        ax.plot(tmp['sell'],  color="green",                             markersize=20,                                 alpha=1.0,                                  marker=7)  # + v

    #* aet rid of everything we are not seeing
    g.df_buysell = g.df_buysell.head(len(g.ohlc))

    return