#!/usr/bin/python -W ignore
# + matplotlib.use("Qt5agg")
# + matplotlib.use('Tkagg')
import matplotlib
matplotlib.use('Tkagg')
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor
import mplfinance as mpf
import lib_v2_ohlc as o
# + from lib_cvars import Cvars
# + from lib_cvars import Gvars
import lib_panzoom as c
import pandas as pd
import json
import getopt, sys, os
import lib_v2_globals as g
import toml
import matplotlib.patches as mpatches
import gc
fromdate = False
todate = False

# def days_between(d1, d2):
#     try:
#         d1 = dt.datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
#         d2 = dt.datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
#         return abs((d2 - d1))# + .days)
#     except Exception as e:
#         print(f"[3]Error:{e}...` continuing")
#         return False

g.cvars = toml.load(g.cfgfile)

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hf:c:s:lw:", ["help","file=","colname=","session=","list","window="])
except getopt.GetoptError as err:
    sys.exit(2)

input_filename = "_allrecords.csv"
colname = "Close"f
session_name = "N/A"
listdata = False
window = False
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-f, --file <json file of df>")
        print("-c, --col <column name>")
        print("-s, --session <session name>")
        print("-l, --list  list details (colums names)")
        print("-w, --window <n> window size")
        sys.exit(0)

    if opt in ("-f", "--file"):
        input_filename = arg
    if opt in ("-c", "--colname"):
        colname = arg

    if opt in ("-w", "--window"):
        window = int(arg)

    if opt in ("-s", "--session"):
        session_name = arg

    if opt in ("-l", "--list"):
        listdata = True

# if not colname or not input_filename or not session_name:
#     print('''
#     Missing colname or input_filename... examples
#         ./liveview.py -f _allrecords.csv -c Close -s gallon
#     ''')
#     exit(1)

fig = c.figure_pz(figsize=(18, 6), dpi=96)
fig.patch.set_facecolor('black')
x1 = fig.add_subplot(111)  # + OHLC - top left
ax = fig.get_axes()
multi = MultiCursor(fig.canvas, ax, color='r', lw=1, horizOn=True, vertOn=True)

def animate(k):
    gc.collect()
    global session_name
    global input_filename
    num_axes = len(ax)


    if (input_filename.find('csv') != -1):
        df = pd.read_csv(input_filename, sep='\t', lineterminator='\n')
        # df = pd.read_csv(input_filename)
        df.index = pd.DatetimeIndex(df['Timestamp'])
    else:
        df = pd.read_json(input_filename)
        df.index = pd.DatetimeIndex(df['Timestamp'])

    df.set_index("ID")

    # print(len(df.index))
    if window:
        df = df.tail(window).copy()
    #     print(len(df.index))
    # exit()
    if listdata:
        keylist = list(df.keys())
        for i in range(len(keylist)):
            print(i,keylist[i])
        exit()
    dataState = True
    try:
        with open("state.json") as json_file:
            data = json.load(json_file)
    except:
        dataState = False


    if isinstance(df,pd.DataFrame):
        usecolor="olive"
        for i in range(num_axes):
            ax[i].clear()
            # ax[i].set_title(f'{g.session_name}/{input_filename} -> {colname}  {fromdate} - {todate} (DAYS: {deltadays})')
            ax[i].set_title(f'{g.session_name}/{input_filename} -> {colname}  {fromdate} - {todate} ')
            ax[i].grid(True, color='grey', alpha=0.3)
            ax[i].set_facecolor("black") #g.cvars['styles']['buyface']['color'])
            ax[i].xaxis.label.set_color(usecolor)
            ax[i].yaxis.label.set_color(usecolor)

            ax[i].tick_params(axis='x', colors=usecolor)
            ax[i].tick_params(axis='y', colors=usecolor)

            ax[i].spines['left'].set_color(usecolor)
            ax[i].spines['top'].set_color(usecolor)
            # + ax[i].axhline(y=0.0, color='black')
        ax_patches = []
        for i in range(num_axes):
            ax_patches.append([])

        ax[i].plot(
            df[colname],
            color=g.cvars['styles']['close']['color'],
            linewidth=1,
            alpha=g.cvars['styles']['close']['alpha'],
        )
        ax_patches[i].append(mpatches.Patch(
            color=g.cvars['styles']['close']['color'],
            label="Close"
        ))


        ax[i].plot(
            df['bb3avg_buy'],
            color="red",
            markersize=5,
            alpha=1.0,
            marker=6
        )
        # ax.plot(bLtmp['buy'], color=g.cvars['buy_marker']['L']['color'], markersize=g.cvars['buy_marker']['L']['size'], alpha=g.cvars['buy_marker']['L']['alpha'],  marker=6)  # + ^
        ax[i].plot(
            df['bb3avg_sell'],
            color="#00FF00",
            markersize=5,
            alpha=1.0,
            marker=7
        )

        if dataState:
            if data['avgprice'] > 0:
                ax[i].axhline(
                    data['avgprice'],
                    color       = g.cvars['styles']['avgprice']['color'],
                    linewidth   = g.cvars['styles']['avgprice']['width'],
                    alpha       = 0.5 # g.cvars['styles']['avgprice']['alpha']
                )
                ax[i].axhline(
                    data['coverprice'],
                    color       = "lime", #g.cvars['styles']['coverprice']['color'],
                    linewidth   = g.cvars['styles']['coverprice']['width'],
                    alpha       = 0.5 #g.cvars['styles']['coverprice']['alpha']
                )
                if data['buyunder'] < df['Close'][-1]*2 and data['buyunder'] > df['Close'][-1]/2:
                    ax[i].axhline(
                        data['buyunder'],
                        color       = "red", #g.cvars['styles']['buyunder']['color'],
                        linewidth   = 2, #g.cvars['styles']['buyunder']['width'],
                        alpha       = 0.5 #g.cvars['styles']['buyunder']['alpha']
                    )


        # plot = mpf.make_addplot(df['Close'], ax=ax[0], type="line", color="blue", width=1, alpha=1)
        # p1 = mpf.make_addplot(df['bb3avg_buy'], ax=ax[0], scatter=True, color="red", markersize=100, alpha=1, marker=6)  # + ^
        # p2 = mpf.make_addplot(df['bb3avg_sell'], ax=ax[0], scatter=True, color="green", markersize=100, alpha=1, marker=7)  # + v
        # plots = [plot, p1, p2]
        # mpf.plot(df, type="line", ax=ax[0], addplot=plots, returnfig=True)

ani = animation.FuncAnimation(fig=fig, func=animate, frames=86400, interval=1000, blit = False, repeat=True)
plt.show()
