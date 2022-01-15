#!/usr/bin/python -W ignore
import os,sys,getopt,shutil, toml, re, time
import lib_v2_ohlc as o
import lib_v2_globals as g
import glob

def frepval(fn, sfind, sreplace):
    # * Check if any line in the file contains given string
    # * Open the file in read only mode
    tf = open("_tmpcf","w")
    line = False
    with open(fn, 'r') as read_obj:
        # * Read all lines in the file one by one
        for line in read_obj:
            # * For each line, check if line contains the string
            if sfind in line:
                if line[0] != "#":
                    spat = re.compile(r'.*(#.*)')
                    rpat = rf'{sreplace}\1'
                    # print(f"BEF: {line}")
                    line = spat.sub(rpat,line)
                    # print(f"AFT: {line}")
            tf.write(line)
    tf.close()


search = "perf_filter"
replace = "'xxx'"
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hs:r:R", ["help","search=","replace=", "recover"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-s, --search  keyword to find")
        print("-r, --replace  new value")
        print("-R, --recover  recover latest config.toml")
        sys.exit(0)

    if opt in ("-s", "--search"):
        search = arg

    if opt in ("-r", "--replace"):
        replace = f"{search:<19} = {arg.strip()}      "

    if opt in ("-R", "--recover"):
        newest = min(glob.iglob('safe/config.toml.*'), key=os.path.getctime)
        print(newest)
        os.remove("config.toml")
        shutil.copy(newest,"config.toml")
        print(f"config.toml recovered from {newest}")
        exit()

g.cvars = toml.load(g.cfgfile)

ts = time.time()
# bufile = f"safe/config.toml.{ts}"
# shutil.copy2("config.toml",bufile)

frepval('config.toml', search, replace)
print(f'Replaced: [{search}] -> [{replace}]')

shutil.copy2("_tmpcf","config.toml")
# os.system(f"diff config.toml {bufile}")
