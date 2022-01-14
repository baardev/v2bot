#!/usr/bin/bash

# ! D: BACKTEST, no-perf, testnet amounts
# + R: Returned 84.44 over year

./creplace.py -s datatype   -r "'backtest'"
./creplace.py -s startdate  -r "'2021-01-01 00:00:00'"
./creplace.py -s enddate    -r "'2022-01-01 00:00:00'"

# * perf params  (off)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '0'

./creplace.py -s backtest.testpair        -r "['BUY_tvb3','SELL_tvb3']"
./creplace.py -s backtest.short_purch_qty -r "0.000414"
./creplace.py -s backtest.long_purch_qty  -r "0.000414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'