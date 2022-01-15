#!/usr/bin/bash

# ! D: BACKTEST, 16-bit perf, leveraged amounts (insufficient funds 5/19 - 8/09)
# + R: (Arcadia) 01-01-2021 to 05-30-2021 =
# = X: ./soundex.py -c 5m -f 0 -b 16 -p BTC/USDT -s data  /BTCUSDT_5m.json # outpout = data/perf_16_BTCUSDT_5m_0f.json


./creplace.py -s datatype   -r "'backtest'"
./creplace.py -s startdate  -r "'2021-01-01 00:00:00'"
./creplace.py -s enddate    -r "'2022-01-01 00:00:00'"

# * perf paramws (on)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '16'

./creplace.py -s backtest.testpair        -r "['BUY_perf','SELL_tvb3']"
./creplace.py -s backtest.short_purch_qty -r "0.414"
./creplace.py -s backtest.long_purch_qty  -r "0.414"
#./creplace.py -s backtest.next_buy_increments -r '0.003414'
./creplace.py -s backtest.purch_mult -r "1.414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'

cat << EOF

EOF