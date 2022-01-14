#!/usr/bin/bash

# ! D: STREAM, 3-bit perf, testnet amounts
# + R: ---

./creplace.py -s datatype   -r "'stream'"

# * perf paramws (on)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '3'

./creplace.py -s stream.testpair        -r "['BUY_perf','SELL_tvb3']"
./creplace.py -s stream.short_purch_qty -r "0.000414"
./creplace.py -s stream.long_purch_qty  -r "0.000414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'
