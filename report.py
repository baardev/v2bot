#!/usr/bin/python -W ignore
import lib_v2_globals as g
import lib_v2_ohlc as o
import logging
import getopt
import sys
from colorama import init
from colorama import Fore, Back, Style  # ! https://pypi.org/project/colorama/
import toml

init()
g.cvars = toml.load(g.cfgfile)
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
csv = ""
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hs:v:t:f:c", ["help","session=","version=","table=" ,"form=" ,"csv"])
except getopt.GetoptError as err:
    sys.exit(2)

session_name = ""
tablename = "orders"
form = "short"
version = 1

vtext=[
    False,
    "buys/sell only",
    "sum(netcredits)",
    "sum(credits) - sum(fees) - sum(mxint)",
    "sum(fees)+sum(mxint)"
]

def showhelp():
    print("-s, --session   session name")
    print("-v, --version   1|2|3 (calc row | db sum | ?)")
    print("-t, --table   table name")
    print("-f, --form   'long' | 'short' | 'all'")
    print("-c, --csv   csv format")
    print("EXAMPLES:")
    print("\t./report.py -t orders -s purpose -f long|sort -n -k 5  (show running profits)")
    exit(0)

if not opts:
    showhelp()

for opt, arg in opts:
    if opt in ("-h", "--help"):
        showhelp()

    if opt in ("-s", "--session"):
        session_name = arg
    if opt in ("-v", "--version"):
        version=int(arg)
    if opt in ("-t", "--table"):
        tablename = arg
    if opt in ("-f", "--form"):
        form = arg
    if opt in ("-c", "--csv"):
        csv = "\t"

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.logit = logging
g.logit.basicConfig(
    filename="logs/ohlc.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=g.cvars['logging']
)
stdout_handler = g.logit.StreamHandler(sys.stdout)
g.dbc, g.cursor = o.getdbconn()

if form == "short":
    rs = o.get_running_bal(version=version, table=tablename, session_name=session_name)
    print(f"v{version}\t{vtext[version]}\t${rs:,.2f}")

firstBuy = 0
finalSell = False
dates = []
# * get start/end time for each session
rsf = list(o.sqlex(f"SELECT bsuid,min(order_time) from {tablename} where session = '{session_name}' group by bsuid"))
rst = list(o.sqlex(f"SELECT bsuid,max(order_time) from {tablename} where session = '{session_name}' group by bsuid"))

fary = {}
tary = {}
for r in rsf:
    fary[r[0]]=r[1]
for r in rst:
    tary[r[0]]=r[1]
delta = {}
for key in tary:
    delta[key] = f"{(tary[key] - fary[key])}"

if form == "long":
    rs = o.sqlex(f"SELECT * from {tablename} WHERE session = '{session_name}' ")
    cost = 0

    pstr = f"{'ID':>5}{csv} "
    pstr += f"{'DATETIME':>20}{csv} "
    pstr += f"{'PRO':>10}{csv} "
    pstr += f"{'COST':>10}{csv} "
    pstr += f"{'SP':>4}{csv} "
    pstr += f"{'CT':>2}{csv} "
    pstr += f"{'CAP':>6}%{csv} "
    pstr += f"{'LIM':>6}%{csv} "
    pstr += f"{'RES':>8}{csv} "
    pstr += f"{'TIME':>16}{csv} "
    print(pstr)

    for r in rs:
        aprice = r[g.c_price]
        aside = r[g.c_side]
        asize = r[g.c_size]
        aqty = r[g.c_size]
        adate = r[g.c_order_time]
        acredits = r[g.c_credits]
        anetcredits = r[g.c_netcredits]
        afintot = r[g.c_fintot]
        aorder_time = str(r[g.c_order_time])
        absuid = r[g.c_bsuid]

        if aside == "sell":
            # cmd = f"SELECT sum(credits), count(credits),bsuid from {tablename} WHERE session = '{session_name}' and bsuid = '{absuid}' and side = 'buy'"
            rs = list(o.sqlex(f"SELECT sum(credits), count(credits),bsuid from {tablename} WHERE session = '{session_name}' and bsuid = '{absuid}' and side = 'buy'", ret="one"))
            cost = abs(rs[0])
            count = rs[1]
            bsuid = rs[2]
            rs1 = list(o.sqlex(f"SELECT sum(credits) from {tablename} WHERE session = '{session_name}' and bsuid = '{absuid}'", ret="one"))
            profit = rs1[0]
            _reserve_seed = g.cvars[g.cvars['datatype']]['reserve_seed']
            _margin_x = g.cvars[g.cvars['datatype']]['margin_x']
            rescap = _reserve_seed * _margin_x
            resval = aprice*rescap
            # pctcap = afintot/resval
            timedelta = str(delta[absuid])
            timedelta = timedelta.replace(" ","_")
            timedelta = timedelta.replace(",","_")
            timedelta = timedelta.replace("__","_")
            pctlimcap = profit/cost

            pstr =  f"{bsuid:>6}{csv} "
            pstr +=  f"{aorder_time:>20}{csv} "
            # pstr += f"{afintot:10.2f}{csv} "
            pstr += f"{cost:10.2f}{csv} "
            pstr += Fore.GREEN + f"{profit:6.2f}{csv} "+Style.RESET_ALL
            pstr += f"{count:2d}{csv} "
            # pstr += f"{pctcap:6.4f}{csv} "
            pstr += f"{pctlimcap:6.4f}{csv} "
            pstr += f"{resval:8.2f}{csv} "
            pstr += f"{timedelta:>16}{csv} "

            print(pstr)

if form == "all":
    rs = o.sqlex(f"SELECT * from {tablename} WHERE session = '{session_name}' ")
    cost = 0

    # pstr = f"{'ID':>5}{csv} "
    # pstr += f"{'DATETIME':>20}{csv} "
    # pstr += f"{'PRO':>10}{csv} "
    # pstr += f"{'COST':>10}{csv} "
    # pstr += f"{'SP':>4}{csv} "
    # pstr += f"{'CT':>2}{csv} "
    # pstr += f"{'CAP':>6}%{csv} "
    # pstr += f"{'LIM':>6}%{csv} "
    # pstr += f"{'RES':>8}{csv} "
    # pstr += f"{'TIME':>16}{csv} "
    # print(pstr)

    for r in rs:
        aprice = r[g.c_price]
        aside = r[g.c_side]
        asize = r[g.c_size]
        adate = r[g.c_order_time]
        acredits = r[g.c_credits]
        anetcredits = r[g.c_netcredits]
        afintot = r[g.c_fintot]
        aorder_time = f"{r[g.c_order_time]}"
        absuid = r[g.c_bsuid]
        asl = r[g.c_sl]
        try:
            afees = f"{r[g.c_fees]:,.2f}"
        except:
            afees = 0.0

        str = []
        if aside == "buy":
            str.append(f"[{aorder_time}]")
            str.append(Fore.RED)
            str.append(f"Hold [{asl}] {asize:07.05f} @ ${aprice:,.2f} = ${asize * aprice:07.02f}")
            str.append(f"Fee: ${afees:,.2f}")
            str.append(Fore.RESET)
            iline = str[0]
            for s in str[1:]:
                iline = f"{iline} {s}"
            print(iline)

        if aside == "sell":
            str.append(f"[{aorder_time}]")
            str.append(Fore.GREEN )
            str.append(f"Sold        " + f"{asize:07.05f} @ ${aprice:,.2f} = ${asize * aprice:07.02f}")
            str.append(f"Fee: ${afees:,.2f}")
            str.append(f"SessNet: ${afintot}")
            str.append(Style.RESET_ALL)
            iline = str[0]
            for s in str[1:]:
                iline = f"{iline} {s}"
            print(iline)

