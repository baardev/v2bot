#!/usr/bin/python
import os
import lib_v2_ohlc as o
import lib_v2_globals as g
import toml
import sys
import getopt

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()
g.cdata = toml.load(f"C_data_{str(g.cvars['pair']).replace('/','')}.toml")

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hc:",
                               [
                                    "help",
                                    "cfgfile=",
                               ])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-c, --cfgfile")
        sys.exit(0)


    if opt in ("-c", "--cfgfile"):
        g.cfgfile = arg
        g.cvars = toml.load(g.cfgfile)
        g.datatype = g.cvars["datatype"]
        if g.runlevel == 0:
            print(f"USING CONFIG: [{g.cfgfile}]")
    else:
        g.cfgfile = "config.toml"
        g.cvars = toml.load(g.cfgfile)

    g.cdata = toml.load(f"C_data_{str(g.cvars['pair']).replace('/','')}.toml")

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

state = ""
if os.path.isfile('_session_name.txt'):
    with open('_session_name.txt') as f:
        g.session_name = f.readline().strip()
        state = "EXISTING"
else:
    o.get_sessioname()
    state = "NEW"

g.tmpdir = f"/tmp/{g.session_name}"

if g.runlevel == 0:
    if os.path.isdir(g.tmpdir):
        # print(f"exists... deleting")
        print(f"rmdir {g.tmpdir}")
        os.system(f"rm -rf {g.tmpdir}")
    print(f"mkdir {g.tmpdir}")
    os.mkdir(g.tmpdir)

for g.runlevel in range(g.cdata['runlevels']):
    o.sqlex(f"delete from orders{g.runlevel} where session = '{g.session_name}'")
    o.sqlex(f"ALTER TABLE orders{g.runlevel} AUTO_INCREMENT = 1")

print(f"{state}: {g.session_name}")
