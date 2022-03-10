#!/usr/bin/python
import getopt
import os
import sys, json
import toml
import lib_v2_globals as g
import lib_v2_ohlc as o

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
cfgfile = "C_data_ETHBTC.toml"

try:
    opts, args = getopt.getopt(argv, "-h",["help","cfgfile="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        sys.exit(0)
    if opt in ("-c", "--cfgfile <fn>"):
        cfgfile = arg
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

g.cvars = toml.load(g.cfgfile)
g.dbc, g.cursor = o.getdbconn()
g.cdata = toml.load(cfgfile)

def defc(cmd):
    print(cmd)
    try:
        o.sqlex(cmd)
    except:
        pass

for i in range(g.cdata['runlevels']):
    print(i)

    # cmd = f"ALTER TABLE orders{i} DROP pk"
    # cmd = f"ALTER TABLE orders{i} ADD abspct float(6,3)"
    cmd = f"ALTER TABLE orders{i} DROP COLUMN p_ToPr"
    defc(cmd)
    cmd = f"ALTER TABLE orders{i} ADD p_CuSePr float(16,8)"
    defc(cmd)
    cmd = f"ALTER TABLE orders{i} ADD p_ToCaPr float(16,8)"
    defc(cmd)
    cmd = f"ALTER TABLE orders{i} ADD p_ToPr float(16,8)"
    defc(cmd)


