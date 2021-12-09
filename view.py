#!/usr/bin/python3.9
import getopt, sys
import pandas as pd
import tabloo
import pandasgui

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hf:t", ["help","file=","tabloo"])
except getopt.GetoptError as err:
    sys.exit(2)

input_filename = False
usetabloo = False
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this info")
        print("-f, --file   read from last data file")
        print("-t, --tabloo   use tabloo (def: pandasgui)")
        sys.exit(0)

    if opt in ("-f", "--file"):
        input_filename = arg
    else:
        print("You must enter a file to read")

    if opt in ("-t", "--tabloo"):
        usetabloo = True

if not input_filename:
    print("Missing -f <input_filename>")
    exit(1)
# + input_filename = "/home/jw/src/jmcap/ohlc/_ohlcdata.json"
print(f"Loading from {input_filename}")

df = pd.read_json(input_filename, orient='split', compression='infer')

if usetabloo:
    tabloo.show(df)
else:
    pandasgui.show(df)

