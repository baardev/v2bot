#!/usr/bin/bash

# ! D: STREAM, 16-bit perf, leveraged amounts
# + R: (Rome) steam - =
# = X: ./perfbits.py -c 0m -f 0 -b 16 -p BTC/USDT -s data/BTCUSDT_0m_0f.json  # outpout = data/perf_16_BTCUSDT_0m_0f.json

./creplace.py -s datatype   -r "'stream'"

# * perf paramws (on)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '16'

./creplace.py -s stream.testpair        -r "['BUY_perf','SELL_tvb3']"
./creplace.py -s stream.short_purch_qty -r "0.414"
./creplace.py -s stream.long_purch_qty  -r "0.414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'

cat << EOF

EOF