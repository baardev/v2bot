#!/usr/bin/python
import getopt
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import toml

import lib_v2_globals as g
import lib_v2_ohlc as o

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
isX = False
try:
    opts, args = getopt.getopt(argv, "-hX", ["help", "isX"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-X, --isX (has X11 def=False)")
        sys.exit(0)

    if opt in ("-X", "--isX"):
        isX = True

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
g.display = g.cvars['display']
g.headless = g.cvars['headless']
g.dbc, g.cursor = o.getdbconn()

g.session_name = o.get_current_session()
# g.session_name = "Rome"

try:
    import matplotlib

    matplotlib.use("Qt5agg")
    import matplotlib.animation as animation
    # import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure
    import lib_v2_listener as kb

    # import matplotlib.dates as mdates
    g.headless = False
except:
    # * assume this is headless if er end up here as the abive requires a GUI
    g.headless = True



df_dbx = pd.read_csv("/home/jw/src/coinbasepro/tickerhist.csv", names=['total', 'date'], sep=',', lineterminator='\n')
format = "'%H:%M:%S - %b %d %Y'"
df_dbx.index = pd.DatetimeIndex(pd.to_datetime(df_dbx['date'], format=format))


fig, ax = plt.subplots(1, 1, figsize=(20, 8), dpi=80)
ax.grid(True, color='grey', alpha=0.3)

ax.plot(df_dbx['total'], label='Binance', color='g')

format_str = '%-m/%-d'
format_ = mdates.DateFormatter(format_str)
ax.xaxis.set_major_formatter(format_)

for label in ax.get_xticklabels(which='major'):
    label.set(rotation=90, horizontalalignment='right')

t = o.get_datetime_str()
ax.set_title(f"My Sad Portfolio\n${df_dbx['total'][-1]}")

if o.X_is_running():
    if isX:
        plt.show()

fig.savefig('images/plot_port.png')
# exit()
