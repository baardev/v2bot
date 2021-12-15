
https://biboxcom.github.io/v3/spot/en/#spot-trade-need-apikey

https://biboxcom.github.io/v3/spot/en/#place-an-order

# error codes (outdated and/or wrong)
https://biboxcom.github.io/en/error_code.html#%E9%94%99%E8%AF%AF%E7%A0%81


3025: Signature verification failed (签名验证失败)
2027: Insufficient available balance (可用余额不足)
2048: Illegal operation  (操作非法)

## Todo
Check JWFIX notes
_lastloaded saving to ohlc dir
rohlc legend color

## Process to generate backdata

run generator with -d as the starting epoch stamp, and -i as the starting counter
`./ohlc_backdata.py -d 1514812800000 -i 0`

optionally view the data
`./view.py -f data/backdata_ETH+BTC.5m.2018-01-01_13:20:00...2018-01-05_02:35:00.1000_binance_0.json`

merge all the parts together with -f as the unique filename globber
`./merge.py -f backdata_ETH+BTC.5m. -i 9 -b 2021-10-03 -e 2021-11-05 -o bb `


to convert date string to epoch -> https://esqsoft.com/javascript_examples/date-to-epoch.htm

sample data
- oct  3 - oct 19 (bb_bear) 1633230000 - 1634612400
- oct 19 - nov  2 (bb_bull) 1634612400 - 1634612400
- oct  3 - nov  2 (bb)      16332300pip install mysqlclient00 - 1634612400

2021-09-05T03:19:00 for https://www.utilities-online.info/epochtime = 1630822740
2021-09-06T00:04:00 for https://www.utilities-online.info/epochtime = 1630897440

more info...
    https://esqsoft.com/javascript_examples/date-to-epoch.htm


## Backdata wrapper
./backdata.py -i 40 -d "2021-09-06 00:00:00" -o ETH1


## References:

examples of plots for matplotlib
https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html

mpf and mpl
https://github.com/matplotlib/mplfinance/wiki/Acessing-mplfinance-Figure-and-Axes-objects


## python packages needed 

# on Debian (duncanstroud.com)...
to install python3.9 -> https://www.vultr.com/docs/update-python3-on-debian

```
apt install qtcreator
apt install qtdeclarative5-dev
apt install gnumeric
```
(may need to use 'pip3' on Debian)

```
pip install PyQt5
pip install ccxt
pip install matplotlib
pip install mplfinance
pip install pandas-ta 
pip install ta-lib (req. ta-lib src from https://mrjbq7.github.io/ta-lib/install.html)
pip install pynput
pip install pandas
pip install tabloo
pip install coinbasepro
pip install coinbase
pip install colorama
pip install xlsxwriter
pip install mysqlclient (may have needed 'sudo apt-get install libmysqlclient-dev')
pip install scipy
pip install pandasgui   
pip install simplejson
```
(can't install on 3.5 duncanstroud.com)

```
pip install MySQLdb
pip install coinbase_python3
```
# rsync
`rsync -avr --exclude 'safe/*' --exclude 'venv/*' /home/jw/src/jmcap/ohlc/ jw@duncanstroud.com:/home/jw/src/jmcap/ohlc/`

## remote connecting

Docs: https://en.wikipedia.org/wiki/Xvfb#Usage_examples

needed to ...
`sudo ln -s /usr/lib/x86_64-linux-gnu/libxcb-util.so.0 /usr/lib/x86_64-linux-gnu/libxcb-util.so.1`

# run virtual screen manager on server
```
export DISPLAY=:1
Xvfb :1 -screen 0 1910x1280x24 &
fluxbox &
x11vnc -display :1 -bg -nopw -listen localhost -xkb
```
# tunnel to localhost locally
`ssh -N -T -L 5900:localhost:5900 jw@duncanstroud.com`

#view locally 
```
vncviewer -geometry 1920x1280 localhost:5900
vncviewer -encodings 'copyrect tight zrle hextile' localhost:5900 (args didn't work for me)
```

# To shutdown vncserver
```
x11vnc -R stop (doesn;t always work)
ps -ef |grep x11vnc|grep -v grep|awk '{print "kill -9 "$2}'|sh
ps -ef |grep fluxbox|grep -v grep|awk '{print "kill -9 "$2}'|sh
ps -ef |grep /usr/bin/terminator|grep -v grep|awk '{print "kill -9 "$2}'|sh
```
## Speed tests

with save = 16.05s user 6.54s system 45% cpu 49.787 total
w/o save =  16.14s user 6.42s system 53% cpu 42.476 total

with mem-state = 16.21s user 6.61s system 54% cpu 42.095 total
with file-state: 15.96s user 6.46s system 56% cpu 39.530 total  (faster!?!)


## coinbase specific utils
```
auth_client.py
public_client.py
cb_cltool.py
cb_order.py
cbtest.py
```
### Modules
```
lib_cvars.py
lib_globals.py
lib_ohlc.py
lib_panzoom.py
lib_tests_class.py
lib_listener.py
```
### Folders
```
assets
configs
data
logs
records
safe
```
### OHLC utils
```
RUN
ohlc.py
merge.py
mkLIVE
pread.py
view.py
gview.py
ohlc_backdata.py
backdata.py
liveview.py
```
### Misc utils
```
test_cb.sh
rep
```
### Config files
```
config_0.hcl
remote_config.json
state_0.json
```
### Output
```
results.csv
results.xls
```
### Docs
```
README.md
```

### Backups
```
ohlc.zip
../ORG
```

## Recovery instruction for fubared boot
https://superuser.com/questions/111152/whats-the-proper-way-to-prepare-chroot-to-recover-a-broken-linux-installation

### VCE
https://code.visualstudio.com/docs/getstarted/keybindings



### TESTS
 ~/src/jmcap/purpose


MSE "SELECT sum(runtot/(price*7))*100 as APR from purpose where side='sell'"
+---------------+
| APR           |
+---------------+
| 14.4668265292 |  << percent against the entire capital reserve
+---------------+
 
SELECT 
    g1.order_time from_date,
    g2.order_time to_date,
    TIMEDIFF(g2.order_time,g1.order_time) as delta
FROM
    purpose g1
        INNER JOIN
    purpose g2 ON g2.bsuid = g1.bsuid + 1
WHERE
    g1.side = 'sell';

...
2021-11-12 18:05:00	2021-11-15 12:55:00	66:50:00
2021-11-15 12:55:00	2021-11-15 14:05:00	01:10:00
2021-11-15 12:55:00	2021-11-15 14:20:00	01:25:00
...

MSE "select count(t.ct) as total_per, t.ct as per from (SELECT count(*) as ct from purpose group by bsuid order by ct) as t group by per order by total_per" 
+-----------+-----+
| total_per | per |
+-----------+-----+
|         1 |  11 |
|         1 |   1 |
|         1 |  12 |
|         1 |   8 |
|         1 |   9 |
|         1 |  10 |
|         2 |  13 |
|         3 |   7 |
|         6 |   6 |
|        18 |   5 |
|        26 |   4 |
|        82 |   3 |
|       374 |   2 |
+-----------+-----+

To update after merging

alias MSE="mysql -ujmc -p6kjahsijuhdxhgd jmcap -e "
alias MSX="mysql -ujmc -p6kjahsijuhdxhgd jmcap < "

MSE "UPDATE orders SET netcredits = credits - fees "
MSE "UPDATE orders SET runtotnet = credits - fees"

SET @tots:= 0;
UPDATE orders SET fintot = null WHERE session = '{g.session_name}';
UPDATE orders SET runtotnet = credits - fees;
UPDATE orders SET fintot = (@tots := @tots + runtotnet) WHERE session = '{g.session_name}';


