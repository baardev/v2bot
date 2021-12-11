#!/usr/bin/python3.9
# + matplotlib.use("Qt5agg")
# + matplotlib.use('Tkagg')
import matplotlib
import logging
matplotlib.use('Tkagg')
import lib_v2_globals as g
import lib_v2_ohlc as o
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor
import lib_panzoom as c
import pandas as pd
import getopt, sys, os

fromdate = False
todate = False

g.gcounter = 0
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

def days_between(d1, d2):
    try:
        d1 = dt.datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
        d2 = dt.datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
        return abs((d2 - d1))# + .days)
    except Exception as e:
        print(f"[3]Error:{e}...` continuing")
        return False


argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hs:c:i:", ["help","session=","colname=","interval="])
except getopt.GetoptError as err:
    sys.exit(2)

g.session_name = False
colname = False
interval = 1000
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-s, --session  session name")
        print("-c, --col  column name")
        print("-i, --interval")
        sys.exit(0)

    if opt in ("-i", "--interval"):
        interval = arg
    if opt in ("-s", "--session"):
        g.session_name = arg
    if opt in ("-c", "--colname"):
        colname = arg

if not colname or not g.session_name:
    print('''
    Missing colname or input_filename... examples
        ./dbview.py -s orthodontist -c rtot &
    ''')
    exit(1)
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.logit = logging
g.logit.basicConfig(
    filename="logs/ohlc.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=o.cvars.get('logging')
)
stdout_handler = g.logit.StreamHandler(sys.stdout)
g.dbc, g.cursor = o.getdbconn()

fig = c.figure_pz(figsize=(18, 2.5), dpi=96)

x1 = fig.add_subplot(111)  # + OHLC - top left
ax = fig.get_axes()
multi = MultiCursor(fig.canvas, ax, color='r', lw=1, horizOn=True, vertOn=True)

g.cwd = os.getcwd().split("/")[-1:][0]
def get_df():
    profit = []

    # * get id of sells
    rs = o.sqlex(f"SELECT t.runtotnet,order_time,price as profit FROM (select * from orders where side='sell' and session = '{g.session_name}') as t", ret="all")
    rtall = []
    rt=0
    # * make cumulative totals
    for i in range(len(rs)):
        rt = rt + rs[i][0]
        date = rs[i][1]
        close = rs[i][2]
        rtall.append( [ rt, date, close ])

    df = pd.DataFrame(rtall,columns=["profit","date","price"]) # * return the column data as a df
    df['price'] = o.normalize_col(df['price'], df['profit'].min(), df['profit'].max())
    df.set_index("date")
    return df

def animate(k):
    num_axes = len(ax)
    df = get_df()

    title = f'{g.cwd}/{g.session_name} -> {colname} ({g.gcounter})'
    if isinstance(df,pd.DataFrame):
        ax[0].clear()
        ax[0].set_title(title)
        ax[0].grid(True, color='grey', alpha=0.3)
            # + ax[i].axhline(y=0.0, color='black')
        ax_patches = []
        for i in range(num_axes):
            ax_patches.append([])
        plt.plot(df['date'], df[colname])
        plt.plot(df['date'], df['price'])
        # print("─────────────────────────────────────────────────")

    plt.ion()
    test = True
    if g.gcounter > 0:
        while(test):
            if os.path.isfile("/tmp/_sell"):
                test=False
            else:
                plt.gcf().canvas.start_event_loop(1)
        os.system("rm /tmp/_sell")
    g.gcounter = g.gcounter + 1

ani = animation.FuncAnimation(fig=fig, func=animate, frames=86400, interval=interval, blit = False, repeat=True)
plt.show()