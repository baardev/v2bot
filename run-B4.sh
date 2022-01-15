#!/usr/bin/bash

# ! D: BACKTEST, 6-bit perf, leveraged amounts
# + R: (memorable) 01-01-2021 to 05-30-2021 = $390,611.74 (987%)
# = X: ./soundex.py -c 5m -f 0 -b 6 -p BTC/USDT -s data/BTCUSDT_5m.json -v2 # outpout = data/perf_6_BTCUSDT_5m_0f.json

#cd data
#rm data/perf_6_BTCUSDT_5m_0f.json
#ln -fs perf_6_BTCUSDT_5m_0f_VER1.json perf_6_BTCUSDT_5m_0f.json
#cd -

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

cat << EOF
+-------------+-----------+------------+
| count(size) | size      | order_time |
+-------------+-----------+------------+
|        5840 |  0.414000 | BTC/USDT   |
|        1190 |  0.669852 | BTC/USDT   |
|         373 |  1.083820 | BTC/USDT   |
|         817 |  1.083852 | BTC/USDT   |
|         147 |  1.753621 | BTC/USDT   |
|         226 |  2.167672 | BTC/USDT   |
|          59 |  2.837359 | BTC/USDT   |
|          88 |  3.921294 | BTC/USDT   |
|          31 |  4.590848 | BTC/USDT   |
|          28 |  6.758653 | BTC/USDT   |
|          17 |  7.427992 | BTC/USDT   |
|          14 | 11.349502 | BTC/USDT   |
|           5 | 12.018491 | BTC/USDT   |
|          12 | 18.777494 | BTC/USDT   |
|           1 | 19.445919 | BTC/USDT   |
|           4 | 30.795984 | BTC/USDT   |
|           1 | 31.463497 | BTC/USDT   |
|           1 | 81.705399 | BTC/USDT   |
+-------------+-----------+------------+
EOF