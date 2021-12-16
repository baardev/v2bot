#!/usr/bin/python3.9
import matplotlib
matplotlib.use("Qt5agg")
import sys
import getopt
import pandas as pd
from matplotlib.widgets import MultiCursor
import mplfinance as mpf
import lib_panzoom as c
# import lib_v2_ohlc as o
import matplotlib.dates as mdates

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hf:c:", ["help","file=","chart="])
except getopt.GetoptError as err:
    sys.exit(2)

chart = "Close"

input_filename = "_allrecords.csv" #False

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-f, --file   read from last data file")
        print("-c, --chart  'Close'")
        print("-t, --tabloo   use tabloo (def: pandasgui)")
        sys.exit(0)

    if opt in ("-c", "--chart"):
        chart = arg
    if opt in ("-f", "--file"):
        input_filename = arg
    else:
        print("You must enter a file to read")

if not input_filename:
    print("Missing -f <input_filename>")
    exit(1)

print(f"Loading from {input_filename}")

df = pd.read_csv(input_filename, sep='\t', lineterminator='\n')
df.index = pd.DatetimeIndex(df['Timestamp'])

# dfbs = pd.read_json("_buysell.json")
# dfbs.index = pd.DatetimeIndex(df['Timestamp'])



fig = c.figure_pz(figsize=[18,8], dpi=96)
fig.add_subplot(111)
ax = fig.get_axes()

ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))
for label in ax[0].get_xticklabels(which='major'):
    label.set(rotation=7, horizontalalignment='right')

multi = MultiCursor(fig.canvas, ax, color='r', lw=1, horizOn=True, vertOn=True)

plot = mpf.make_addplot(df['Close'], ax=ax[0], type="line", color="blue", width=1, alpha=1)
p1 = mpf.make_addplot(df['bb3avg_buy'], ax=ax[0], scatter=True, color="red", markersize=200, alpha=1,marker=6)  # + ^
p2 = mpf.make_addplot(df['bb3avg_sell'], ax=ax[0], scatter=True, color="green", markersize=200, alpha=1, marker=7)  # + v
plots = [plot, p1, p2]
mpf.plot(df, type="line", ax=ax[0], addplot=plots, returnfig=True)
mpf.show()


# plots = o.add_plots(plots,close_plot)
