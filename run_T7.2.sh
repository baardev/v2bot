#!/usr/bin/bash

# ! D: BACKTEST, 6-bit perf (V2), leveraged amounts
# + R: (Alison) 01-01-2021 to 05-30-2021 =

cd data
rm perf_6_BTCUSDT_5m_0f.json
ln -fs perf_6_BTCUSDT_5m_0f_VER2.json perf_6_BTCUSDT_5m_0f.json
cd -

./creplace.py -s datatype   -r "'backtest'"
./creplace.py -s startdate  -r "'2021-01-01 00:00:00'"
./creplace.py -s enddate    -r "'2022-01-01 00:00:00'"

# * perf paramws (on)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '6'

./creplace.py -s backtest.testpair        -r "['BUY_perf','SELL_tvb3']"
./creplace.py -s backtest.short_purch_qty -r "0.414"
./creplace.py -s backtest.long_purch_qty  -r "0.414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'
