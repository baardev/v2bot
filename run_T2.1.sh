#!/usr/bin/bash

# ! D: BACKTEST, 3-bit perf (V1), leveraged amounts
# + R: (auxin) 01-01-2021 to 05-30-2021 = $154674.31 (6.66%) ... I.F. errors

rm data/perf_3_BTCUSDT_5m_0f.json
ln -fs data/perf_3_BTCUSDT_5m_0f_VER1.json data/perf_3_BTCUSDT_5m_0f.json


./creplace.py -s datatype   -r "'backtest'"
./creplace.py -s startdate  -r "'2021-01-01 00:00:00'"
./creplace.py -s enddate    -r "'2022-01-01 00:00:00'"

# * perf paramws (on)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '3'

./creplace.py -s backtest.testpair        -r "['BUY_perf','SELL_tvb3']"
./creplace.py -s backtest.short_purch_qty -r "0.414"
./creplace.py -s backtest.long_purch_qty  -r "0.414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'
