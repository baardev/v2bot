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
    opts, args = getopt.getopt(argv, "-hc:s:", ["help","cfgfile=","session="])
except getopt.GetoptError as err:
    print("opts err")
    sys.exit(2)

tablename = "all_orders"
g.cdata = False
cfgfile = "C_data_ETHBTC.toml"
g.session_name = False

def showhelp():
    print("-h, --help")
    print("-c, --cfgfile")
    print("-s, --session")
    exit(0)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        showhelp()

    if opt in ("-c", "--cfgfile"):
        g.cdata = toml.load(arg)

    if opt in ("-s", "--session"):
        g.session_name = arg


# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

tablename = "all_orders"

g.dbc, g.cursor = o.getdbconn(dictionary=True)
g.cdata = toml.load(cfgfile)

def sex(cmd):
    try:
        # print(cmd)
        rs = o.sqlex(cmd)
        return rs
    except:
        return False
# * get start/end time for each session

try:
    rs = sex(f"delete from {tablename}")
    rs = sex("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='orders0'")
    oldcol = []
    newcol = []
    for r in rs:
        if r['COLUMN_NAME'] != "id":
            oldcol.append(r['COLUMN_NAME'])

    oldcols = ",".join(oldcol)

    sex(f"drop table {tablename}")
except:
    pass

sex(f"CREATE TABLE {tablename} LIKE orders0")
sex(f"alter table {tablename} DROP PRIMARY KEY,change id id int;")
sex(f"alter table {tablename} DROP id")
sex(f"alter table {tablename} ADD pk INT(11) DEFAULT 0 NOT NULL")

# ({i}*10000)+bsuid
for i in range(g.cdata['runlevels']):
    newcol = oldcol
    for n in range(len(newcol)):
        if newcol[n] == "bsuid":
            newcol[n]=f"({i}*10000)+bsuid"
    newcols = ",".join(newcol)
    cmd = f"""
    INSERT INTO {tablename} ({oldcols})
    SELECT {newcols} FROM orders{i}
    """
    # print(cmd)
    sex(cmd)

# o.sqlex("ALTER TABLE all_orders ADD PRIMARY KEY (pk);")

cmd = f"select * from {tablename} order by order_time"
rs = sex(cmd)
i=1
for i in range(len(rs)):
    cmd = f"UPDATE {tablename} SET pk = {i+1} where uid = '{rs[i]['uid']}'"
    sex(cmd)

sex(f"alter table {tablename} ADD PRIMARY KEY (pk)")
sex(f"ALTER TABLE `{tablename}` CHANGE `pk` `id` INT(11) NOT NULL AUTO_INCREMENT ")



# o.sqlex("ALTER TABLE `jmcap`.`all_orders` DROP PRIMARY KEY, ADD PRIMARY KEY (`pk`);")


import pandas as pd
import pyodbc

sql=f"""
select id,order_time,price,fees,size,side,level,stot,fintot 
from all_orders 
where side='sell' and session = '{g.session_name}' 
order by order_time
"""
sql_query = pd.read_sql(sql,g.dbc)

df = pd.DataFrame(sql_query)
df.to_csv (r'./allorders.csv', index = False) # place 'r' before the path name



exit()