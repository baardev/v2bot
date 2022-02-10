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

cmd = f"select order_time,fintot,binlive from orders where session = '{g.session_name}' and side = 'sell' and binlive is not null"
print(f"SQL: {cmd}")
rs = o.sqlex(cmd, ret="all")
dt = 0
with open("/tmp/_pchart.csv", 'w') as file:
    # print(rs[0][2])
    base = rs[0][2]
    for i in range(1, len(rs)):
        # d = rs[i][2] - rs[i - 1][2]
        # dt += d
        d = rs[i][2] - base
        # dt += d
        file.write(f"{rs[i][0]},{rs[i][1]},{d}\n")
# exit()


df_dbx = pd.read_csv("/tmp/_pchart.csv", names=['date', 'ptot', 'atot'], sep=',', lineterminator='\n')
df_dbx.index = pd.DatetimeIndex(pd.to_datetime(df_dbx['date']))

# df_orx = pd.read_csv("_profit_record_Arcadia.csv", names=['date','pair','price'], sep=',', lineterminator='\n')
# df_orx.index = pd.DatetimeIndex(pd.to_datetime(df_dbx['date']))

# if len(df_orx.index) > 1:
#     for index, row in df_dbx.iterrows():
#         print(row['ptot'],row['atot'])
# exit()
# print(df_dbx)
# df_dbx.index = df_dbx.set_index(['date'])
# exit()

fig, ax = plt.subplots(1, 1, figsize=(20, 8), dpi=80)
ax.grid(True, color='grey', alpha=0.3)

ax.plot(df_dbx['ptot'], label='Binance', color='g')
ax.plot(df_dbx['atot'], label='Binance', color='r')

format_str = '%-m/%-d'
# format_str = '%M-%D-%Y'
format_ = mdates.DateFormatter(format_str)
ax.xaxis.set_major_formatter(format_)

for label in ax.get_xticklabels(which='major'):
    label.set(rotation=90, horizontalalignment='right')

t = o.get_datetime_str()
ax.set_title(f"{g.cvars['pair']}\nProfit in $ for session '{g.session_name}'")

if o.X_is_running():
    if isX:
        plt.show()

fig.savefig('images/plot_profit.png')

print("Image: images/plot_profit.png")
print("CSV: /tmp/_pchart.csv")
# exit()
