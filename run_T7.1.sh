#!/usr/bin/bash

# ! D: BACKTEST, 6-bit perf (ver. 1), leveraged amounts
# + R: (ravish) 01-01-2021 to 05-30-2021 = $159.768 (526%)
# = X: ./soundex.py -c 5m -f 0 -b 6 -p BTC/USDT -s data/BTCUSDT_5m.json -v1 # outpout = data/perf_6_BTCUSDT_5m_0f.json

#cd data
#rm data/perf_6_BTCUSDT_5m_0f.json
#ln -fs perf_6_BTCUSDT_5m_0f_VER1.json perf_6_BTCUSDT_5m_0f.json
#cd -

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

cat << EOF
+-------------+-----------+------------+
| count(size) | size      | order_time |
+-------------+-----------+------------+
|        4329 |  0.414000 | BTC/USDT   |
|         845 |  0.669852 | BTC/USDT   |
|         267 |  1.083820 | BTC/USDT   |
|         577 |  1.083852 | BTC/USDT   |
|         100 |  1.753621 | BTC/USDT   |
|         167 |  2.167672 | BTC/USDT   |
|          43 |  2.837359 | BTC/USDT   |
|          57 |  3.921294 | BTC/USDT   |
|          21 |  4.590848 | BTC/USDT   |
|          22 |  6.758653 | BTC/USDT   |
|          12 |  7.427992 | BTC/USDT   |
|           9 | 11.349502 | BTC/USDT   |
|           3 | 12.018491 | BTC/USDT   |
|           9 | 18.777494 | BTC/USDT   |
|           1 | 19.445919 | BTC/USDT   |
|           2 | 30.795984 | BTC/USDT   |
|           1 | 31.463497 | BTC/USDT   |
|           1 | 81.705399 | BTC/USDT   |
+-------------+-----------+------------+
EOF