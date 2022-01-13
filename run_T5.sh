#!/usr/bin/bash

# ! Standard T6 tested against6 a 3-bit performce spec

./creplace.py -s perf_filter -r '0'
./creplace.py -s perf_bits -r '3'

./creplace.py -s backtest.testpair -r "['BUY_perf','SELL_tvb3']"
./creplace.py -s display -r 'false'
./creplace.py -s save -r 'false'
./creplace.py -s headless -r 'true'
./creplace.py -s datatype -r "'backtest'"
./creplace.py -s stream.short_purch_qty -r "0.414"
./creplace.py -s stream.long_purch_qty -r "0.414"

