#!/usr/bin/python -W ignore

import lib_v2_globals as g
import lib_v2_ohlc as o
import pandas as pd
import toml
import os, sys, getopt, json
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-h", ["help"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        sys.exit(0)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn(dictionary = True)


full_vals = []
half_vals = []

base = 8
arange = 2**(base*2)
print(f"A-RANGE: [{arange}]")
for d in range(arange):
    full_vals.append(d)
    # print(d)

brange = 2**base
print(f"B-RANGE: [{brange}]")
for d in range(brange):
    half_vals.append(d)


# exit()

data = []
tavg = 0
for d in half_vals:
    hx = '%X' % (d)
    cmd = f"""
    SELECT hex, CONV(hex,16,10) as dex,avg(perf) AS avg_perf, avg(vffd) AS avg_vffd, avg(pffd) AS avg_pffd 
    -- SELECT hex, avg(perf) AS avg_perf, avg(vffd) AS avg_vffd, avg(pffd) AS avg_pffd 
    FROM rootperf{g.cvars['trademodel_version']} 
    WHERE 
    hex LIKE '{hx}__'
    -- LIMIT 10080
    """
    rs = o.sqlex(cmd)
    rs[0]['root']= bin(int(hx, 16))[2:].zfill(base)
    if rs[0]['avg_pffd'] != None:
        data.append(rs[0])
        tavg += rs[0]['avg_pffd']

keyeddata = {}
ticks = []
for j in data:
    # print(j)
    hx2 = int(j['hex'][:-2],16)
    ticks.append(hx2)
    keyeddata[j['root']] = {
        'hex':j['hex'],
        'dex':int(str(hx2),16),
        'avg_perf':j['avg_perf'],
        'avg_vffd':j['avg_vffd'],
        'avg_pffd':j['avg_pffd']
    }

print(f"FOUND [{len(data)}] out of [{len(half_vals)}] = {o.truncate(tavg,2)}%")
df = pd.DataFrame(data)

# df['dex'] = df['dex'].astype(int)
df['ticks'] = ticks

df.sort_values(by=['avg_pffd'], inplace=True)
# df.sort_values(by=['hex'], inplace=True) # crazy
# df.sort_values(by=['dex'], inplace=True) # crazy

print(f'{"INDEX":<6} {"HEX":<6} {"DECIMAL":<6} {"PCT CHANGE":<20}')
i=0
for idx, row in df.iterrows():
    # print(hx2)
    hx2 = row['hex'][:-2]
    print(f"{i:<6} {hx2:<6} {int(hx2,16):<6} {row['avg_pffd']:<20}")
    # print(f"{i} {row['hex']} {row['dex']} {row['avg_pffd']}")
    i += 1

# print(df)

with open(f"data/_perf{g.cvars['trademodel_version']}.json", 'w') as outfile:
    outfile.write(json.dumps(keyeddata,indent=4))
print(f"JSON file saved as: data/_perf4.json")

dfcsv = df.to_csv()
csvfile = f"_tmp_test{g.cvars['trademodel_version']}.csv"
with open(csvfile, 'w') as outfile:
    outfile.write(dfcsv)
print(f"CSV file saved as: {csvfile}")

df.plot(x="hex", y="avg_pffd", kind="line")
df.plot(x="ticks", y="avg_pffd", kind="line")
plt.xticks(rotation=90)
plt.hlines(y=0, xmin=0,xmax=df.index.max(),alpha=0.3)


# fig, ax = plt.subplots()
# loc = plticker.MultipleLocator(base=5.0)
# ax.xaxis.set_major_locator(loc)
# ax.hlines(y=0, xmin=0,xmax=df.index.max(), alpha=0.3)
# ax.plot(df['hex'], df['avg_pffd'])

plt.show()

