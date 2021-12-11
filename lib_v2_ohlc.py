


import json
import os
import random
import calendar
import uuid
import sys
# import toml
import numpy as np
import pandas as pd
import pandas_ta as ta
# import talib as talib
# from lib_v2_cvars import Cvars  # ! used in ohlc.py, not here
# import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import MySQLdb as mdb
import math
# import datetime as dt
# from lib_tests_class import Tests
import lib_v2_tests_class
# import csv
import lib_v2_globals as g
# from shutil import copyfile
import subprocess
from subprocess import Popen
from colorama import Fore, Back, Style  # ! https://pypi.org/project/colorama/
import traceback
from scipy import signal
import time
import importlib
import collections
from datetime import datetime
from datetime import timedelta
# cvars = Cvars(g.cfgfile)

def adj_startdate(startdate):
    # * adjust startdate so that last date in the array is the startdate
    points = g.cvars['datawindow']
    hours = (points * 5) / 60

    listed_time = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
    virtual_time = listed_time - timedelta(hours=hours)

    return virtual_time.strftime('%Y-%m-%d %H:%M:%S')


def get_secret(**kwargs):
    exchange = kwargs['provider']
    apitype = kwargs['apitype']
    # + item = kwargs['item']

    with open("/home/jw/.secrets/keys.json") as json_file:
        data = json.load(json_file)

    return data[exchange][apitype]


def load(filename, **kwargs):
    df = pd.read_json(filename, orient='split', compression='infer')
    try:
        g.logit.debug(f"Trimming df to {kwargs['maxitems']}")
        newdf = df.head(g.cvars("datalength"))
        del df
        return newdf
    except:
        pass

    return df

def getdbconn(**kwargs):
    host = "localhost"

    try:
        host = kwargs["host"]
    except:
        pass
    dbconn = mdb.connect(user="jmc", passwd="6kjahsijuhdxhgd", host=host, db="jmcap")
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
    pair = kwargs['pair']
    timeframe = kwargs['timeframe']
    livect = f"({g.gcounter}/{g.cvars['datalength']})"

    # ft = f"{g.current_close:6.2f} INS=?"
    ft = f"{g.current_close:6.2f} {g.session_name} "

    # # + BACkTEST
    # if cvars.get("datatype") == "backtest":
    #     metadatafile = f"{cvars.get('datadir')}/{cvars.get('backtestmeta')}"
    #     metadata = cvars.cload(metadatafile)
    #     # + atype = metadata['type']
    #     atype = g.datasetname
    #     pair = metadata['pair']
    #     timeframe = metadata['t_frame']
    #     # + fromdate = metadata['fromdate']
    #     fromdate = state_r("from")
    #     # + todate = metadata['todate']
    #     todate = state_r("to")
    #
    #     deltadays = days_between(fromdate.replace("_", " "), todate)
    #     state_wr("delta_days", f"{deltadays}")
    #     ft = f"{g.current_close:6.2f} INS={g.instance_num}/{g.session_name} ({deltadays})[{atype}] {pair} {timeframe} {livect} FROM:{fromdate}  TO:{todate}"
    #
    # # + LIVE
    # if cvars.get("datatype") == "live":
    #     atype = "LIVE"
    #     count = "N/A"
    #     exchange = "Binance"
    #     fromdate = "Ticker"
    #     todate = "Live"
    #     deltadays = days_between(fromdate, todate)
    #
    #     ft = f"{g.current_close:6.2f} INS={g.instance_num}/{g.session_name} ({deltadays})[{atype}] {pair} {timeframe} FROM:{fromdate}  TO:{todate}"
    #
    # # + RANDOM
    # if cvars.get("datatype") == "random":
    #     atype = "Random"
    #     count = "N/A"
    #     exchange = "N/A"
    #     fromdate = "N/A"
    #     todate = "N/A"
    #     deltadays = days_between(fromdate, todate)
    #
    #     ft = f"{g.current_close:6.2f} INS={g.instance_num}/{g.session_name} {livect} pts:{count}"

    # + g.subtot_cost, g.subtot_qty, g.avg_price = itemgetter(0, 1, 2)(list_avg(state_r('open_buys'),state_r('qty_holding')))
    # + g.subtot_qty = trunc(g.subtot_qty)
    # + g.subtot_cost = trunc(g.subtot_cost)

    # g.pnl_running = truncate(state_r('pnl_running'), 5)
    # g.pct_running = truncate(state_r('pct_running'), 5)

    rpt = f" {g.subtot_qty:8.2f} @ ${g.subtot_cost:8.2f}  ${g.running_total:6.2f}"

    ft = f"{ft} !! {rpt}"
    return ft

def get_latest_time(ohlc):
    return (ohlc['Date'][int(len(ohlc.Date) - 1)])

def state_wr(name, v):
    # * if supposed to be a number, but it Nan...
    try:
        if math.isnan(v):
            return  #* just leave if value is Nan
    except:
        pass

    if g.cvars['state_mem']:  # ! array in mem exists - currently not in use
        g.state[name] = v
    else:
        try:
            with open(g.statefile) as json_file:
                data = json.load(json_file)
        except Exception as ex:
            handleEx(ex, f"Check the file '{g.statefile}' (for ex. at 'https://jsonlint.com/)'")
            exit(1)
        data[name] = v
        try:
            with open(g.statefile, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        except Exception as ex:
            handleEx(ex, f"Check the file '{g.statefile}' (for ex. at 'https://jsonlint.com/)'")
            exit(1)
        data[name] = v

def state_ap(listname, v):
    if math.isnan(v):
        return  #* just leave if value is Nan
    if g.cvars['state_mem']:  # ! array in mem exists - currently not in use
        g.state[listname].append(v)
    else:
        with open(g.statefile) as json_file:
            data = json.load(json_file)
        data[listname].append(v)
        with open(g.statefile, 'w') as outfile:
            json.dump(data, outfile, indent=4)

def state_r(name, **kwargs):
    if g.cvars['state_mem']: # ! array in mem exists... currently not in use
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
    state_wr('session_name', "noname")
    state_wr('ma_low_holding', False)
    state_wr('ma_low_sellat', 1e+10)
    state_wr("open_buyscanbuy", True)
    state_wr("open_buyscansell", False)



    state_wr("from", False)
    state_wr("to", False)
    state_wr("tot_buys", 0)
    state_wr("tot_sells", 0)
    state_wr("max_qty", 0)
    state_wr("first_buy_price", 0)
    state_wr("last_buy_price", 1e+10)
    state_wr("next_buy_price", 1e+10)

    state_wr("largest_run_count", 0)
    state_wr("last_run_count", 0)
    state_wr("current_run_count", 0)
    state_wr("pnl_running", 0)
    state_wr("pct_running", 0)
    state_wr("order", {})
    state_wr("last_sell_price", 0)
    state_wr("last_avg_price", 0)

    state_wr("curr_qty", 0)
    state_wr("delta_days", 0)
    state_wr("purch_qty", False)
    state_wr("run_counts", [])

    state_wr('open_buys', [])
    state_wr('qty_holding', [])
    state_wr('buyseries', [])


    # state_wr("pct_gain_list", [])
    # state_wr("pct_record_list", [])
    # state_wr("pnl_record_list", [])
    # state_wr("running_tot", [])

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

    g.current_run_count = state_r("current_run_count")
    print("g.current_run_count", g.current_run_count)

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
    try:
        g.cursor.execute("SET AUTOCOMMIT = 1")
        g.cursor.execute(cmd)
        g.dbc.commit()
        if ret == "all":
            rs = g.cursor.fetchall()
        if ret == "one":
            rs = g.cursor.fetchone()

    except Exception as ex:
        handleEx(ex, cmd)
        exit(1)

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

def get_ohlc(ticker_src, spot_src, **kwargs):
    pair = g.cvars["pair"]
    timeframe = g.cvars["timeframe"]
    since = kwargs['since']
    data = []
    # + * -------------------------------------------------------------
    # + *  LIVE DATA
    # + * -------------------------------------------------------------
    if g.cvars["datatype"] == "live":
        ohlcv = ticker_src.fetch_ohlcv(symbol=pair, timeframe=timeframe, since=since, limit=g.cvars['datawindow'])
        df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['orgClose'] = df['Close']
        df["Date"] = pd.to_datetime(df.Timestamp, unit='ms')
        df.index = pd.DatetimeIndex(df['Timestamp'])
        g.ohlc = df.loc[:, ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'orgClose']]
        g.ohlc['ID'] = range(len(df))
        g.ohlc["Date"] = pd.to_datetime(g.ohlc.Timestamp, unit='ms')
        g.ohlc.index = pd.DatetimeIndex(df['Timestamp'])
        g.ohlc.index = g.ohlc['Date']
    # + -------------------------------------------------------------
    # + BACKTEST DATA
    # + -------------------------------------------------------------
    if g.cvars['datatype'] == "backtest":

        # df.rename(columns={'Date': 'Timestamp'}, inplace=True)
        # df['orgClose'] = df['Close']

        date_mask = (g.bigdata['Timestamp'] > g.startdate)
        conv_mask = (g.df_priceconversion_data['Timestamp'] > g.startdate)

        df = g.bigdata.loc[date_mask]

        g.df_conv = g.df_priceconversion_data[conv_mask]
        g.df_conv = g.df_conv.tail(len(df.index))

        # df["Date"] = pd.to_datetime(df['Timestamp'], unit='ms')
        # df.index = pd.DatetimeIndex(df['Timestamp'])


        _start = (g.datawindow) + g.gcounter
        _end = _start + (g.datawindow)


        # print(_start,_end)

        # _start = (g.cvars['datawindow']) + g.gcounter
        # _start = g.gcounter
        # _end = _start + (g.cvars['datawindow'])

        g.ohlc = df.iloc[_start:_end]

        # print(g.ohlc)

        g.ohlc_conv = g.df_conv.iloc[_start:_end]

        # + ! copying a df generated complained that I am trying to modiofy a copy, so this is to create
        # + ! a copy that has no record that it si a copy. tmp fix, find a better way
        fn = f"_tmp1.json"
        save_df_json(g.ohlc, fn)
        del g.ohlc
        g.ohlc = load_df_json(fn)
        os.remove(fn)
        g.ohlc['ID'] = range(len(g.ohlc))

        g.ohlc['Open'] = g.ohlc['Open'] * g.ohlc_conv['Open']
        g.ohlc['High'] = g.ohlc['High'] * g.ohlc_conv['High']
        g.ohlc['Low'] = g.ohlc['Low'] * g.ohlc_conv['Low']
        g.ohlc['Close'] = g.ohlc['Close'] * g.ohlc_conv['Close']

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

def make_mav(ohlc, **kwargs):
    mav = kwargs["mav"]
    ohlc[f'MAV{mav}'] = ohlc["Close"].rolling(mav).mean().values

def make_rohlc(ohlc, **kwargs):
    ohlc["rohlc"] = ohlc["Close"].max() - ohlc["Close"]
    ohlc["rohlc"] = normalize_col(ohlc["rohlc"],ohlc["Close"].min(),ohlc["Close"].max())

def make_sigffmb(ohlc):
    N = g.cvars['mbpfilter']['N']
    Wn_ary = g.cvars['mbpfilter']['Wn']

    for band in range(len(Wn_ary)):
        colname = f'sigffmb{band}'
        Wn = Wn_ary[band]
        ohlc[colname] = 0
        b, a = signal.butter(N, Wn, btype="bandpass", analog=False)  # * get filter params
        sig = ohlc['Close']  # * select data to filter
        sigff = signal.lfilter(b, a, signal.filtfilt(b, a, sig))  # * get the filter
        g.bag[f'sigfft{band}'].append(sigff[len(sigff) - 1])  # * store results in temp location
        ohlc[colname] = backfill(g.bag[f'sigfft{band}'])  # * fill data to match df shape
        ohlc[colname] = normalize_col(ohlc[colname])  # * set all bands to teh same data range

def make_sigffmb(ohlc, **kwargs):
    inverted = False
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

        # ohlc['ffmaps'] = ohlc['ffmap2'] - ohlc['ffmap']
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=7).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=7).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=7).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=4).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=8).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=8).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=8).mean()
        # ohlc['ffmaps'] = ohlc['ffmaps'].ewm(span=16).mean()

def make_dstot(ohlc):

    # print(f"g.dstot_Dadj: [{g.dstot_Dadj}]   g.long_buys: [{g.long_buys}]")
    # print(f"[{g.dstot_Dadj}] [{g.long_buys}]")

    def davg(ohlc,span):
        do = ohlc['Dstot'].tail(span).tolist()
        dos = 0
        for d in do:
            dos += abs(d)
        dstot_o = (dos / span) * (1+g.dstot_Dadj)
        return(dstot_o)

    tval = 0
    for i in range(len(g.cvars['mbpfilter']['Wn'])):
        tval = tval + ohlc[f"Dsigffmb{i}"][-1]



    g.dstot_ary.insert(0,tval)
    g.dstot_ary = g.dstot_ary[:288]
    ohlc['Dstot'] = g.dstot_ary[::-1]

    span=g.cvars['dstot_span']
    dsloamp = davg(ohlc,span)*-1

    g.dstot_lo_ary.insert(0,dsloamp)
    g.dstot_lo_ary = g.dstot_lo_ary[:g.cvars['datawindow']]
    ohlc['Dstot_lo'] = g.dstot_lo_ary[::-1]
    ohlc['Dstot_lo'] = ohlc['Dstot_lo'].ewm(span=span).mean()

    g.dshiamp = davg(ohlc,span)
    g.dstot_hi_ary.insert(0,g.dshiamp)
    g.dstot_hi_ary = g.dstot_hi_ary[:g.cvars['datawindow']]
    ohlc['Dstot_hi'] = g.dstot_hi_ary[::-1]
    ohlc['Dstot_hi'] = ohlc['Dstot_hi'].ewm(span=span).mean()



def make_lowerclose(ohlc):
    ohlc['lowerClose'] = ohlc['Close'].ewm(span=12).mean() * (1 - g.lowerclose_pct)

# def make_sigffmb2(ohlc):
#     plots = kwargs['plots']
#     ax = kwargs['ax']
#     patches = kwargs['patches']
#
#     N = cvars.get("mbpfilter")['N']
#     Wn_ary = cvars.get("mbpfilter")['Wn']
#     mx = cvars.get("mbpfilter")['mx']
#
#     if not cvars.get("plots_sigffmb2_hide"):
#         for j in range(len(Wn_ary)):
#             plots = add_plots(plots, get_sigffmb2(ohlc, N=N, Wn=Wn_ary[j], band=j, ax=ax))
#             label = f"rFFmap {N},{Wn_ary[j]})"
#             patches.append(mpatches.Patch(color=cvars.get('sigffmbstyle')['color'][j], label=label))
#     else:  # + * JUST GET THE DATA, DONT PLOT
#         for j in range(len(Wn_ary)):
#             get_sigffmb2(ohlc, N=N, Wn=Wn_ary[j], band=j, ax=ax)
#
#     # * we now have all the bands in cols 'sigffmb2<band number>'
#
#     for j in range(len(Wn_ary)):
#         # ohlc[f'sigffmb2{j}'] = ohlc[f'sigffmb2{j}']
#         ohlc[f'sigffmb2{j}'] = normalize_col(ohlc[f'sigffmb2{j}'])
#
#
#     return plots

def plot_close(ohlc,**kwargs):
    ax = kwargs['ax']
    panel = kwargs['panel']
    ax_patches = kwargs['patches']
    ax[panel].plot(
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
    ax[panel].plot(
        ohlc['MAV40'],
        color=g.cvars['mavs'][1]['color'],
        linewidth=g.cvars['mavs'][1]['width'],
        alpha=g.cvars['mavs'][1]['alpha'],
    )
    ax_patches[0].append(mpatches.Patch(
        color=g.cvars['mavs'][1]['color'],
        label="MAV40"))

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
    # ax[1].axhline(y= g.dstot_buy, color="cyan", linewidth=g.cvars['styles']['Dstot']['width'], alpha=g.cvars['styles']['Dstot']['alpha'])
    # ax[1].axhline(y= g.dstot_sell, color="magenta", linewidth=g.cvars['styles']['Dstot']['width'],alpha=g.cvars['styles']['Dstot']['alpha'])
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
    file1 = open(f"logs/{filename}","a")
    file1.write(data+"\n")
    file1.close()


def get_last_price(exchange, **kwargs):
    quiet = False
    try:
        quiet = kwargs['quiet']
    except:
        pass
    pair = g.cvars['price_conversion']
    if not quiet:
        log2file("Remote connecting...(fetching ticker price)...", "counter.log")
    g.last_conversion = g.conversion
    if g.cvars['convert_price']:                      # * are we choosing to see the price in dollars?
        if g.cvars['offline_price']:                  # * do we want tegh live (slow) price can we live with the fixed (fast) price?
            if not quiet:
                g.logit.info(f"Using fixed conversion rate: {g.conversion}")

            offprice = g.cvars['offline_price']

            # offprice = g.df_priceconversion_data.loc[date]['Close']
            # print("date,offprice: ",date,offprice)
            return offprice           # * if so, retuirn fixed price
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


    # print(f"Calced subtot_qty = {tot_qty}")
    # print(f"Calced subtot_cost = {tot_cost}")
    return tot_cost, tot_qty, avg, adj_tot_cost, adj_avg

def get_running_bal(**kwargs):
    table = "orders"
    version = 2
    ret = "all"
    sname = g.session_name
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

    if version == 1:
        # g.dbc, g.cursor = getdbconn()
        cmd = f"select * from {table} where session = '{sname}'"
        rs = sqlex(cmd, ret=ret)

        # print("-----------------------------------")
        # print("rs",rs)
        # print("-----------------------------------")

        # g.cursor.close()  # ! JWFIX - open and close here?

        c_id = 0
        c_uid = 1
        c_pair = 2
        c_fees = 3
        c_price = 4
        c_stop_price = 5
        c_upper_stop_price = 6
        c_size = 7
        c_funds = 8
        c_record_time = 9
        c_order_time = 10
        c_side = 11
        c_type = 12
        c_state = 13
        c_session = 14
        c_pct = 15
        c_cap_pct = 16
        c_credits = 17
        c_netcredits = 18
        c_runtot = 19
        c_runtotnet = 20
        c_bsuid = 21
        c_fintot = 22

        buys = []
        sells = []

        tot_profit = 0
        i = 1
        res = False
        for r in rs:
            # print("-----------------------------------")
            # print("r", r)
            # print("-----------------------------------")
            aclose = r[c_price]
            aside = r[c_side]
            aqty = r[c_size]
            adate = r[c_order_time]
            acredits = r[c_credits]
            anetcredits = r[c_netcredits]
            afintot = r[c_fintot]
            v =aqty*aclose
            if aside == "buy":
                # print(Fore.RED + f"Bought {aqty:3.2f} @ {aclose:6.4f} =  {(aqty*aclose):=6.4f}"+Fore.RESET)
                buys.append(v)
            if aside == "sell":
                # print(Fore.GREEN + f"  Sold {aqty:3.2f} @ {aclose:6.4f} = {(aqty*aclose):6.4f}"+Fore.RESET)
                sells.append(v)
                profit = sum(sells) - sum(buys)
                # print("-----------------------------------")
                # print("profit", profit)
                # print("-----------------------------------")
                # print(Fore.YELLOW+f"PROFIT:------------------ {sum(sells)} - {sum(buys)} = {profit}"+Fore.RESET)
                res = Fore.CYAN + f"[{i:04d}] {Fore.CYAN}{adate} {Fore.YELLOW}${profit:6.2f}" + Fore.RESET
            i += 1
        # print("-----------------------------------")
        # print("res", res)
        # print("-----------------------------------")

        return float(profit)

    # * get the last runtotnet (rename? as ths is GROSS , not NET? - JWFIX)
    if version == 2:
        # profit = sqlex(f"SELECT t.runtotnet as profit FROM (select * from orders where side='sell' and session = '{sname}') as t order by id desc limit 1", ret=ret)[0]
        profit = sqlex(f"SELECT sum(netcredits) as profit FROM {table} where session='{sname}'", ret=ret)[0]
        return profit


    if version == 3:
        # * don;t need lastid, as we are in teh 'sold' space, whicn means teh last order was a sell
        # lastid = sqlex(f"select id from orders where session = '{sname}' order by id desc limit 1 ", ret=ret)[0]
        # profit = sqlex(f"select sum(credits)-sum(fees) from orders where session = '{sname}' and id <= {lastid}", ret=ret)[0]
        profit = sqlex(f"select sum(credits)-sum(fees) from {table} where session = '{sname}'", ret=ret)[0]
        return profit

def tosqlvar(v):
    if not v:
        v = None
    v = f"'{v}'"
    return v

def update_db(tord):
    argstr = ""
    # print(tord)
    # waitfor()
    for key in tord:
        vnp = f"{key} = {tosqlvar(tord[key])}"
        argstr = f"{argstr},{vnp}"

    # g.dbc, g.cursor = getdbconn()
    uid = tord['uid']
    cmd = f"insert into orders (uid, session) values ('{uid}','{g.session_name}')"
    sqlex(cmd)
    g.logit.debug(cmd)
    cmd = f"UPDATE orders SET {argstr[1:]} where uid='{uid}' and session = '{g.session_name}'".replace("'None'", "NULL")
    sqlex(cmd)

    cmd = f"UPDATE orders SET bsuid = '{g.bsuid}' where uid='{uid}' and session = '{g.session_name}'"
    sqlex(cmd)

    credits = tord['price'] * tord['size']
    if tord['side'] == "buy":
        credits = credits * -1
    cmd = f"UPDATE orders SET credits = {credits} where uid='{uid}' and session = '{g.session_name}'"
    sqlex(cmd)
    cmd = f"UPDATE orders SET netcredits = credits-fees where uid='{uid}' and session = '{g.session_name}'"
    sqlex(cmd)


    cmd = f"select sum(credits) from orders where bsuid = {g.bsuid} and session = '{g.session_name}'"
    sumcredits = sqlex(cmd)[0][0]

    cmd = f"select sum(fees) from orders where bsuid = {g.bsuid} and  session = '{g.session_name}'"
    sumcreditsnet = sumcredits - sqlex(cmd)[0][0]

    cmd = f"UPDATE orders SET runtot = {sumcredits}, runtotnet = {sumcreditsnet} where uid='{uid}' and session = '{g.session_name}'"
    sqlex(cmd)

    # cmd = f"UPDATE orders SET runtot = {sumcredits} where uid='{uid}' and session = '{g.session_name}'"
    # sqlex(cmd)


    g.logit.debug(cmd)

    # g.cursor.close()  # ! JWFIX - open and close here?

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



def filter_order(order):
    tord = {}
    supported_actions = ['market', 'sellall']

    if supported_actions.count(order['order_type']) == 0:
        print(f"{order['order_type']} not yet supported")
        exit(1)
    else:
        tord['type'] = tryif(order, 'order_type', False)
        tord['side'] = tryif(order, 'side', False)
        tord['pair'] = tryif(order, 'pair', False)
        tord['size'] = tryif(order, 'size', 0)
        tord['price'] = tryif(order, 'price', False)
        tord['stop_price'] = tryif(order, 'stop_price', 0)
        tord['upper_stop_price'] = tryif(order, 'upper_stop_price', 0)

        tord['funds'] = False
        tord['uid'] = tryif(order, 'uid', -1)

    tord['state'] = tryif(order, 'state', "UNKNOWN")
    tord['order_time'] = tryif(order, 'order_time', get_datetime_str())

    tord['pair'] = tord['pair'].replace("/", "-")  # ! adjust for coinbase name
    # * this converts the field names into the command line switcheS -P, -z, etc
    argstr = ""
    for key in tord:
        if tord[key]:
            try:
                try:  # ! skip over missing g.cflds fields, lile 'state' and 'record_time'
                    argstr = argstr + f" {g.cflds[key]} {tord[key]}"
                except Exception as ex:
                    pass
            except KeyError as ex:
                handleEx(ex, f"{tord}\n{key}")
                exit(1)
            except Exception as ex:
                handleEx(ex, f"{tord}\n{key}")
                exit(1)

    argstr = f"/home/jw/src/jmcap/ohlc/cb_order.py {argstr}"
    return tord, argstr

def calcfees(rs_ary):
    fees = 0
    # print(rs_ary) #XXX
    # waitfor()
    try:
        for fn in rs_ary['resp']:
            rrec = pd.read_pickle(fn)

            # + pp.pprint(rrec)
            fees = fees + float(rrec['fill_fees'])
    except:
        pass

    return fees

def orders(order, **kwargs):
    # nsecs = get_seconds_now()
    tord, argstr = filter_order(order)  # * filters out the unnecessary fields dependinG on order type

    # * submit order to remote proc, wait for replays

    if g.cvars['offline']:
        tord['fees'] = 0
        # ! these vals are takes from the empircal number of the CB dev sandbox transactions
        if order['side'] == "buy":
            tord['fees'] = (order['size'] * order['price']) * g.buy_fee  # * sumulate fee

        if order['side'] == "sell":
            tord['fees'] = (order['size'] * order['price']) * g.sell_fee  # * sumulate fee

        tord['session'] = g.session_name
        tord['state'] = True
        tord['record_time'] = get_datetime_str()
    else:
        g.logit.info(pcTOREM() + argstr + pcCLR(), extra={'mod_name': 'lib_olhc'})
        sys.stdout.flush()

        # - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

        # ! This is where the data from cb_order.py is returned as an array (json serialized)...
        # ! in cb_order.py teh array is called 'rs_ary', and it si the last output of the program
        # = Because the objecss returned from coinbase, or any array that has Decimal types, can't be serialized,
        # = the pickled objects are saved as files, and these input_filenames are return in rs_ary
        # - {
        # -     "message": "Settled after 1 attempt",
        # -     "settled": true,
        # -     "order": "records/B_1635517292.ord",
        # -     "resp": [
        # -         "records/B_1635517292.ord.r_0"
        # -     ]
        # - }

        ufn = exec_io(argstr)
        if not ufn:
            return False

        # - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

        g.logit.info(pcFROREM() + ufn + pcCLR(), extra={'mod_name': 'lib_olhc'})
        cclr()
        try:
            rs_ary = json.loads(ufn)  # * load the array of pickled files
            rs_order = pd.read_pickle(rs_ary['order'])
            fees = 0
            for r in rs_ary['resp']:
                rs_resp = pd.read_pickle(r)
                try:
                    fees = fees + float(rs_resp['fill_fees'])
                except Exception as ex:
                    pass
            tord['fees'] = calcfees(rs_ary)
            tord['session'] = g.session_name
            tord['state'] = rs_order["settled"]
            tord['record_time'] = get_datetime_str()
        except Exception as ex:
            handleEx(ex, f"len(ufn)={len(ufn)}")
            g.logit.info(pcFROREM() + ufn + pcCLR())

    # update_db(tord, nsecs)
    update_db(tord)
    return True


#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

def process_buy(is_a_buy, **kwargs):
    ax = kwargs['ax']
    BUY_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    def tots(dfline, **kwargs):
        rs = float("Nan")
        m = float("Nan")
        # * if there is a BUY and not a SELL, add the subtot as a neg value
        if not math.isnan(dfline['buy']) and math.isnan(dfline['sell']):
            m = dfline['buy'] * -1
            # * if there is a SELL and not a BUY, add the subtot as a pos value
        if not math.isnan(dfline['sell']) and math.isnan(dfline['buy']):
            m = dfline['sell']

        rs = m * dfline['qty']
        return (rs)

    if g.purch_qty * g.purch_qty_adj_pct > g.cvars['reserve_cap']:
        g.purch_qty = g.cvars['reserve_cap'] - g.purch_qty
    else:
        g.purch_qty = g.purch_qty * g.purch_qty_adj_pct

    g.stoplimit_price = BUY_PRICE * (1 - g.cvars['sell_fee'])  # /0.99
    # print(f"stoplimit_price set to {g.stoplimit_price}  ({BUY_PRICE} * {1-cvars.get('sell_fee')})")

    # * show on chart we have something to sell
    if g.cvars['display']:
        g.facecolor = g.cvars['styles']['buyface']['color']
        # ax.set_facecolor(g.cvars['styles']['buyface']['color'])
    # * first get latest conversion price
    g.conversion = get_last_price(g.spot_src, quiet=True)

    # !FILTERS

    if g.market == 'bull':
        g.cooldown_count = 0
        g.purch_qty_adj_pct = 1
        # g.dstot_Dadj = g.cvars['dstot_Dadj'][0]

    if g.market == 'bear':  # ! set NEXT cooldown
        # * 0.7 - 1/14, 14 = max number of buys of 7 @ 0.5 each
        # g.dstot_Dadj = g.cvars['dstot_Dadj'][g.long_buys]

        # * set cooldown by setting the next gcounter number that will freeup buys
        # ! cooldown is calculated by adding the current g.gcounter counts and adding the g.cooldown
        # ! value to arrive a the NEXT g.gcounter value that will allow buys.
        # !g.cooldown holds the number of buys

        g.cooldown =  g.gcounter + (state_r('current_run_count') * g.cvars['cooldown_mult'])
        g.purch_qty_adj_pct = 1

    # * we are in, so reset the buy signal for next run
    g.external_buy_signal = False
    # ! check there are funds?? JWFIX

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
    g.df_buysell['subtot'] = g.df_buysell.apply(lambda x: tots(x),
                                                axis=1)  # * calc which col we are looking at and apply accordingly
    # g.df_buysell['pct'].fillna(method='ffill', inplace=True)                # * create empty holder for pct and pnl
    # g.df_buysell['pnl'].fillna(method='ffill', inplace=True)
    # g.df_buysell['pct'] = g.df_buysell.apply(lambda x: fillin(x, g.df_buysell), axis=1)

    # * 'convienience' vars,
    bv = df['bb3avg_buy'].iloc[-1]  # * gets last buy
    sv = df['bb3avg_sell'].iloc[-1]  # * gets last sell
    tv = df['Timestamp'].iloc[-1]  # * gets last timestamp

    # * insert latest data into df, and outside the routibe we shift busell down by 1, making room for next insert as loc 0
    g.df_buysell['buy'].iloc[0] = BUY_PRICE
    g.df_buysell['qty'].iloc[0] = g.purch_qty
    g.df_buysell['Timestamp'].iloc[0] = tv  # * add last timestamp tp buysell record

    # * increment run counter and make sure the historical max is recorded
    g.current_run_count = g.current_run_count + 1
    state_wr("current_run_count", g.current_run_count)

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

    # * create a new order
    order = {}
    order["pair"] = g.cvars["pair"]
    # = order["funds"] = False
    order["side"] = "buy"
    order["size"] = truncate(g.purch_qty, 5)
    order["price"] = BUY_PRICE
    order["order_type"] = "market"
    # = order["stop_price"] = CLOSE * 1/cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["uid"] = g.uid  # g.gcounter #get_seconds_now() #! we can use g.gcounter as there is only 1 DB trans per loop
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    state_wr("order", order)

    rs = orders(order)
    # * order failed
    if not rs:
        return float("Nan")

    #  calc total cost this run
    qty_holding_list = state_r('qty_holding')
    open_buys_list = state_r('open_buys')

    # * calc current total cost of session
    sess_cost = 0
    for i in range(len(qty_holding_list)):
        sess_cost = sess_cost + (open_buys_list[i] * qty_holding_list[i])

    # * make pretty strings
    s_size = f"{order['size']:6.3f}"
    s_price = f"{BUY_PRICE:6.2f}"
    s_cost = f"{order['size'] * BUY_PRICE:6.2f}"

    g.est_buy_fee = (g.purch_qty * BUY_PRICE) * g.cvars['buy_fee']
    g.running_buy_fee = g.running_buy_fee + g.est_buy_fee
    g.est_sell_fee = g.subtot_cost * g.cvars['sell_fee']
    total_fee = g.running_buy_fee + g.est_sell_fee
    g.covercost = total_fee * (1 / g.subtot_qty)
    g.coverprice = g.covercost + g.avg_price

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
    if g.buymode == "L":
        state_ap("buyseries", 0)
        g.long_buys += 1
        g.dstot_Dadj = g.cvars['dstot_Dadj'][g.long_buys]

    # * print to console
    str = []
    str.append(f"[{g.gcounter:05d}]")
    str.append(f"[{order['order_time']}]")
    try:
        str.append(f"[{g.ohlc_conv.iloc[-1]['Close']}]")
    except:
        pass
    str.append(Fore.RED + f"Hold [{g.buymode}] " + Fore.CYAN + f"{s_size} @ ${s_price} = ${s_cost}" + Fore.RESET)
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price:6.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"COV: " + Fore.CYAN + Style.BRIGHT + f"${g.coverprice:6.2f}" + Style.RESET_ALL)
    str.append(Fore.RED + f"Fee: " + Fore.CYAN + f"${g.est_buy_fee:3.2f}" + Fore.RESET)
    str.append(Fore.RED + f"QTY: " + Fore.CYAN + f"{g.subtot_qty:3.2f}" + Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)

    # if g.buymode != "D":
    # * adjust purch_qty according to rules, and make number compatible with CB api
    if g.needs_reload:
        g.purch_qty = state_r("purch_qty")
    # else:
    # g.purch_qty = g.purch_qty * (1 + (g.purch_qty_adj_pct / 100))
    # g.purch_qty = int(g.purch_qty * 1000) / 1000  # ! Smallest unit allowed (on CB) is 0.00000001

    # * update state file
    state_wr("purch_qty", g.purch_qty)
    state_wr("open_buyscansell", True)

    # * set new low threshholc
    # g.ffmaps_lothresh = min(dfline['ffmaps'], g.ffmaps_lothresh)

    return BUY_PRICE


#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#   - ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

def process_sell(is_a_sell, **kwargs):
    ax = kwargs['ax']
    SELL_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    # * reset to original limits
    g.dstot_buy = g.cvars['dstot_buy']
    g.long_buys = 0
    g.dstot_Dadj = g.cvars['dstot_Dadj'][g.long_buys]

    # * all cover costs incl sell fee were calculated in buy
    if g.cvars['display']:
        g.facecolor = "black"
        # ax.set_facecolor("#000000")  # * make background white when nothing to sell

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

    # * save current run count, incremented in BUY, then reset
    state_ap("run_counts", g.current_run_count)
    g.current_run_count = 0  # + * clear current count

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

    # # * record pct gain/loss of this session
    # state_ap("pct_record_list", g.pct_running)

    # * turn off 'can sell' flag, as we have nothing more to see now
    state_wr("open_buyscansell", False)

    # * record total number of sell and latest sell price
    g.tot_sells = g.tot_sells + 1
    state_wr("tot_sells", g.tot_sells)
    state_wr("last_sell_price", SELL_PRICE)

    # * create new order
    order = {}
    order["order_type"] = "sellall"
    # = order["funds"] = False
    order["side"] = "sell"
    order["size"] = truncate(g.subtot_qty, 5)

    order["price"] = SELL_PRICE
    # = order["stop_price"] = CLOSE * 1 / cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["pair"] = g.cvars["pair"]
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    order["uid"] = g.uid  # g.gcounter #get_seconds_now() #! we can use g.gcounter as there is only 1 DB trans per loop
    state_wr("order", order)

    rs = orders(order)
    # * order failed
    if not rs:
        return float("Nan")
    # * sell all (the default sell strategy) and clear the counters
    state_wr('open_buys', [])
    state_wr('qty_holding', [])

    # * cals final cost and sale of session
    purchase_price = g.subtot_cost
    sold_price = g.subtot_qty * SELL_PRICE

    # * calc gross value
    rp1 = get_running_bal(version=1, ret='all')
    s_rp1 = f"{rp1:6.2f}"

    # * cals net vals (-fees)
    rp2 = get_running_bal(version=2, ret='one')
    s_rp2 = f"{rp2:6.2f}"

    # * calc running total (incl fees)
    g.running_total = get_running_bal(version=3, ret='one')
    s_running_total = f"{g.running_total:6.2f}"

    # * pct of return relatve to holding (NOT INCL FEES)
    # g.pct_return = ((sold_price - purchase_price)/purchase_price) # ! x 100 for actual pct value
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

    # * pct relative to capital, whuch SHOULD be (current price * 'capital')  (NOT INCL FEES)
    # g.pct_cap_return = (sold_price - purchase_price)/(SELL_PRICE * cvars.get('capital'))

    # * print to console
    g.running_buy_fee = g.subtot_cost * g.cvars['buy_fee']
    g.est_sell_fee = g.subtot_cost * g.cvars['sell_fee']
    sess_gross = (SELL_PRICE - g.avg_price) * g.subtot_qty
    sess_net = sess_gross - (g.running_buy_fee + g.est_sell_fee)
    total_fee = g.running_buy_fee + g.est_sell_fee
    g.covercost = total_fee * (1 / g.subtot_qty)
    g.coverprice = g.covercost + g.avg_price

    # g.pct_cap_return = g.pct_return/(g.capital/g.subtot_qty) # x cvars.get('capital'))

    g.pct_cap_return = (sess_net / (g.cvars['reserve_cap'] * SELL_PRICE))

    # print(sess_net,g.pct_cap_return, cvars.get('reserve_cap'), SELL_PRICE)
    # print(f"g.pct_return: {g.pct_return}")
    # print(f"g.pct_cap_return: {g.pct_cap_return}")

    s_size = f"{order['size']:6.2f}"
    s_price = f"{SELL_PRICE:6.2f}"
    s_tot = f"{g.subtot_qty * SELL_PRICE:6.2f}"

    # * update DB with pct
    cmd = f"UPDATE orders set pct = {g.pct_return}, cap_pct = {g.pct_cap_return} where uid = '{g.uid}' and session = '{g.session_name}'"

    # ! JWFIX RELOAD EERROR sending nans

    sqlex(cmd)

    # # * print to console
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
    str = []
    str.append(f"[{g.gcounter:05d}]")
    str.append(f"[{order['order_time']}]")
    str.append(f"[{g.ohlc_conv.iloc[-1]['Close']}]")
    str.append(Fore.GREEN + f"Sold    " + f"{s_size} @ ${s_price} = ${s_tot}")
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price:6.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"Fee: " + Fore.CYAN + Style.BRIGHT + f"${g.est_sell_fee:3.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessGross: " + Fore.CYAN + Style.BRIGHT + f"${sess_gross:06.4f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessFee: " + Fore.CYAN + Style.BRIGHT + f"${g.covercost:3.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessNet: " + Fore.CYAN + Style.BRIGHT + f"${sess_net:6.2f}" + Style.RESET_ALL)
    str.append(Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)

    # \f"[{g.gcounter:05d}] [{order['order_time']}] "+
    # =      Fore.GREEN + f"Sold {s_size} @ ${s_price} = ${s_tot}    PnL: ${(g.subtot_qty * SELL_PRICE) - g.subtot_cost:06.4f}  Fee: ${est_fee:3.2f}  TFee: ${total_fees_to_cover:3.2f}  AVG: ${g.avg_price:6.2f} "+Fore.RESET)

    # g.capital = g.capital + (g.capital * (g.pct_cap_return))
    # print(f"{g.capital}  * 1+{g.pct_cap_return}")

    g.capital = g.capital * (1 + g.pct_cap_return)

    # state_ap("running_tot",rp1)

    # * this shows the number before fees

    str = []
    str.append(f"{Back.YELLOW}{Fore.BLACK}")
    str.append(f"[{dfline['Date']}]")
    str.append(f"NEW CAP AMT: " + Fore.BLACK + Style.BRIGHT + f"{g.capital:6.5f}" + Style.NORMAL)
    str.append(f"Running Total:" + Fore.BLACK + Style.BRIGHT + f" ${s_running_total}" + Style.NORMAL)
    str.append(f"{Back.RESET}{Fore.RESET}")
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)

    # * update available capital according to last gains/loss
    g.purch_qty = (g.capital * g.purch_pct)
    # * reset average price
    g.avg_price = float("Nan")

    g.bsuid = g.bsuid + 1
    g.subtot_qty = 0
    return SELL_PRICE


def trigger(df, **kwargs):
    ax = kwargs['ax']
    cols = df['ID'].max()
    g.current_close = df.iloc[len(df.index)-1]['Close']

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
            # BUY_PRICE = None
            if g.idx == cols:  # * idx is the current index of rfow, cols is max rows... so only when arrived at last row
                # * load the test class
                # ! can do this outside loop? JWFIX
                # importlib.reload(lib_tests_class)
                # # from lib_tests_class import Tests
                importlib.reload(lib_v2_tests_class)
                tc = lib_v2_tests_class.Tests(g.cvars, dfline, df, idx=g.idx)



                # * run test, passing the BUY test algo, or run is alt-S, or another external trigger, has been activated
                is_a_buy = is_a_buy and tc.buytest(g.cvars['testpair'][0]) or g.external_buy_signal
                is_a_buy = is_a_buy and g.buys_permitted       # * we haven't reached the maxbuy limit yet
                # is_a_buy = is_a_buy and STEPSDN <= -2              # * at least 3 previous downs

                # * BUY is approved, so check that we are not runnng hot
                g.uid = uuid.uuid4().hex
                # if is_a_buy and (g.gcounter >= g.cooldown or CLOSE < dfline['lblow']):
                # if is_a_buy and (g.gcounter >= g.cooldown):


                # if cvars.get('xflag01'):
                #     is_a_buy = is_a_buy and (g.gcounter >= g.cooldown or CLOSE < dfline['lblow'])
                # else:
                #     is_a_buy = is_a_buy and (g.gcounter >= g.cooldown)

                # if cvars.get('xflag01'):
                #     is_a_buy = is_a_buy and (g.gcounter >= g.cooldown) # and (CLOSE < dfline['lowerClose'])

                # * make sure we have enough to cover
                checksize = g.subtot_qty + g.purch_qty
                reserve = g.cvars['reserve_cap']

                # print(f"cooldown: {g.cooldown} , count: {g.cooldown_count}, gcounter: {g.gcounter}")
                # print(f"xxxxxxxxxxx g.gcounter >= g.cooldown ({g.gcounter}>={g.cooldown}) = {g.gcounter >= g.cooldown}")

                is_a_buy = is_a_buy and checksize < reserve and g.gcounter >= g.cooldown
                if is_a_buy:
                    BUY_PRICE = process_buy(is_a_buy, ax=ax, CLOSE=CLOSE, df=df, dfline=dfline)


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

                importlib.reload(lib_v2_tests_class)
                tc = lib_v2_tests_class.Tests(g.cvars, dfline, df, idx=g.idx)

                # is_a_sell = is_a_sell and tc.selltest(g.cvars['testpair'][1] or g.external_sell_signal
                is_a_sell = is_a_sell and tc.selltest(g.cvars['testpair'][1]) or g.external_sell_signal

                #
                # g.subtot_cost, g.subtot_qty, g.avg_price, g.adj_subtot_cost, g.adj_avg_price = wavg(
                #     state_r('qty_holding'), state_r('open_buys'))
                #
                # g.est_buy_fee = g.subtot_cost * cvars.get('buy_fee')
                # g.est_sell_fee = g.subtot_cost * cvars.get('sell_fee')
                # total_fee = g.running_buy_fee + g.est_sell_fee
                # g.covercost = total_fee * (1 / g.subtot_qty)
                # g.coverprice = g.covercost + g.avg_price



                if is_a_sell:
                    g.uid = uuid.uuid4().hex
                    if limitsell:
                        SELL_PRICE = process_sell(is_a_sell, ax=ax, CLOSE=g.stoplimit_price, df=df, dfline=dfline)
                        g.stoplimit_price = 1e-10
                    else:
                        SELL_PRICE = process_sell(is_a_sell, ax=ax, CLOSE=CLOSE, df=df, dfline=dfline)
                    os.system("touch /tmp/_sell")
                    g.covercost = 0
                    g.running_buy_fee = 0


                else:
                    SELL_PRICE = float("Nan")
            else:
                SELL_PRICE = float("Nan")
            return SELL_PRICE
        return float("Nan")

    if len(df) != len(g.df_buysell.index):
        waitfor([f"End of data (index mismatch.  expecting {len(df)}, got {len(g.df_buysell.index)})"])

    df['ID'] = range(len(df))
    g.df_buysell['ID'] = range(len(df))

    df["bb3avg_buy"] = float("Nan")
    df["bb3avg_sell"] = float("Nan")

    g.df_buysell = g.df_buysell.shift(periods=1)


    # ! add new data to first row
    df['bb3avg_sell'] = df.apply(lambda x: tfunc(x, action="sell", df=df, ax=ax), axis=1)
    df['bb3avg_buy'] = df.apply(lambda x: tfunc(x, action="buy", df=df, ax=ax), axis=1)
    if g.avg_price > 0:
        if g.cvars['display']:
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

    tmp = g.df_buysell.iloc[::-1] # ! here we have to invert the array to get the correct order
    tmp.set_index(['Timestamp'], inplace=True)

    # for index, row in tmp.iterrows():
    #     row['mclr'] = 1 if row['buy'] > 0 else row['mclr']

    bDtmp = tmp[tmp['mclr']!=0]
    bLtmp = tmp[tmp['mclr']!=1]

    colors = ['blue' if val == 1 else 'red' for val in tmp["mclr"]]
    # print(colors)
    tmp['color'] = colors
    save_df_json(bLtmp,"_bLtmp.json")
    save_df_json(bDtmp,"_bDtmp.json")  # ! short

    # p1 = mpf.make_addplot(tmp['buy'], ax=ax, scatter=True, color=colors, markersize=200, alpha=0.4,  marker=6)  # + ^
    # p2 = mpf.make_addplot(tmp['sell'], ax=ax, scatter=True, color="green", markersize=200, alpha=0.4, marker=7)  # + v

    # print(ax)
    # exit()
    # ax.plot(tmp['buy'], color="red", markersize=20, alpha=0.7,  marker=6)  # + ^
    if g.cvars['display']:
        # ax.plot(bDtmp['buy'], color=g.cvars['buy_marker']['D']['color'], markersize=g.cvars['buy_marker']['D']['size'], alpha=g.cvars['buy_marker']['D']['alpha'],  marker=6)  # + ^
        ax.plot(bDtmp['buy'], color=g.cvars['buy_marker']['D']['color'], markersize=g.cvars['buy_marker']['D']['size'], alpha=g.cvars['buy_marker']['D']['alpha'],  marker=6)  # + ^
        ax.plot(bLtmp['buy'], color=g.cvars['buy_marker']['L']['color'], markersize=g.cvars['buy_marker']['L']['size'], alpha=g.cvars['buy_marker']['L']['alpha'],  marker=6)  # + ^
        # ax.plot(bLtmp['buy'], color="red", markersize=20, alpha=0.7,  marker=6)  # + ^
        ax.plot(tmp['sell'],  color="green",                             markersize=20,                                 alpha=1.0,                                  marker=7)  # + v

    #* aet rid of everything we are not seeing
    g.df_buysell = g.df_buysell.head(len(df))

    return