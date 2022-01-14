#!/usr/bin/bash

# ! D: BACKTEST, 3-bit perf, leveraged amounts, DSTOT
# + R: (neoteny) 01-01-2021 to 01-01-2022 - $26,733.97 (67%)
cat << EOF
+-------------+----------+------------+
| count(size) | size     | order_time |
+-------------+----------+------------+
|         913 | 0.414000 | BTC/USDT   |
|          71 | 0.669852 | BTC/USDT   |
|          59 | 0.828000 | BTC/USDT   |
|          16 | 1.083820 | BTC/USDT   |
|          17 | 1.083852 | BTC/USDT   |
|          11 | 1.242000 | BTC/USDT   |
|           4 | 1.497852 | BTC/USDT   |
|           2 | 1.656000 | BTC/USDT   |
|           6 | 1.753621 | BTC/USDT   |
|           5 | 1.753704 | BTC/USDT   |
|           1 | 1.911852 | BTC/USDT   |
|           5 | 2.167672 | BTC/USDT   |
|           1 | 2.167704 | BTC/USDT   |
|           3 | 2.423556 | BTC/USDT   |
|           2 | 2.581704 | BTC/USDT   |
|           1 | 2.837524 | BTC/USDT   |
|           1 | 2.898000 | BTC/USDT   |
|           1 | 3.251493 | BTC/USDT   |
|           1 | 3.507376 | BTC/USDT   |
|           1 | 3.726000 | BTC/USDT   |
|           1 | 3.921376 | BTC/USDT   |
|           1 | 4.335294 | BTC/USDT   |
|           1 | 4.591146 | BTC/USDT   |
|           1 | 5.419146 | BTC/USDT   |
|           1 | 7.428537 | BTC/USDT   |
+-------------+----------+------------+
EOF > /dev/null

./creplace.py -s datatype   -r "'backtest'"
./creplace.py -s startdate  -r "'2021-01-01 00:00:00'"
./creplace.py -s enddate    -r "'2022-01-01 00:00:00'"

# * perf paramws (on)
./creplace.py -s perf_filter  -r '0'
./creplace.py -s perf_bits    -r '3'

./creplace.py -s backtest.testpair        -r "['BUY_perf_tvb3','SELL_tvb3']"
./creplace.py -s backtest.short_purch_qty -r "0.414"
./creplace.py -s backtest.long_purch_qty  -r "0.414"

# * optimise
./creplace.py -s display  -r 'false'
./creplace.py -s save     -r 'false'
./creplace.py -s headless -r 'true'
