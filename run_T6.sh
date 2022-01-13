#!/usr/bin/bash

# ! Standard params for 5m backtest data

# * turn performance filter off
./creplace.py -s perf_filter -r '0'     # * not used as bit = 0, but set to create proper filename
./creplace.py -s perf_bits -r '0'

./creplace.py -s backtest.testpair -r "['BUY_tvb3','SELL_tvb3']"

./creplace.py -s backtest.short_purch_qty -r "0.414"
./creplace.py -s backtest.long_purch_qty -r "0.414"

./creplace.py -s display -r 'false'
./creplace.py -s save -r 'false'
./creplace.py -s headless -r 'true'
./creplace.py -s datatype -r "'backtest'"

