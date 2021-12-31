# INSTALL

Install requited software

To install python3.9 -> https://www.vultr.com/docs/update-python3-on-debian

Install the following apps

```bash
apt-get install -y git
apt-get install -y wget
apt-get install -y x11vnc xvfb
apt-get install -y qtcreator
apt-get install -y gnumeric
apt-get install -y unzip
apt-get install -y mariadb-server
apt-get install -y mariadb-client
```

Create if necessary, and move to the root directory where you will install the bot, for example

```bash
mkdir ~/src
cd ~/src
```

Install src

```bash
git clone https://github.com/baardev/v2bot.git 
```

Install C library of tech analysis code.  Follow instructions at https://mrjbq7.github.io/ta-lib/install.html

Create and activate a virtual environment (recomended, but not necessary)

```bash
cd ~/src/v2bot
pip install virtualenv
virtualenv ~/src/v2bot/venv
source venv/bin/activate

```

Install required modules

```bash
cd ~/src/v2bot
pip install virtualenv
virtualenv ~/src/v2bot/venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a MySql database called ‘jmcap’, along with a user name and password.

For convenience, create an alias, replacing <uname> witjh a username and <pw> with a password

```bash
alias MSE="mysql -ujmc -pjmcpw jmcap -e "
alias MSX="mysql -ujmc -pjmcpw jmcap < "
```

The run the following tp create the database:

```bash
MSE "create database jmcap"
MSE "Grant ALL PRIVILEGES ON jmcap.* TO '<uname>'@'localhost' IDENTIFIED BY '<pw>';"
MSE "FLUSH PRIVILEGES;"

MSX schema.sql
 
```

Create a folder in your home directoy named `~/.secrets`

Inside the folder, create a file called `keys.toml`

For security reasons, you should run the following command to set the permissions of this files, especially as they will hold the API and secret keys of the  exchange.

`chmod -R  400 ~/.secrets`

The file must have at least the following:

```bash
[database]
	[database.jmcap]
		username = "<your database user name>"
		password = "<your database password>"
```

NOTE: There is a `.secrets/keys.toml` file in the git repo as well that is prefilled specifically to be used for docker, if you choose that option (see below).  The program will first look in your home dir for the `.secrets/ketys.toml`, and if none is found, it will look in the v2bot working directory. You can choose to create a home directory file, or edit the working directory file… but if you do, docker will fail. It’s recomended to use the home directory file for system install, and the working directory file for docker.

Make the program executable

```bash
cd ~/src/v2bot
chmod 755 ./v2.py
```

Run the program

```bash
./v2.py
```

NOTES:

- If you open a new terminal to run the program, you must always run the folloing first:

  ```bash
  cd ~/src/v2bot
  source venv/bin/activate
  ```

- Edit runtime parameters in `config.toml`

- Each time you run the program it creates  a session.  Each session is assigned a name.  Unless you delete the file `_session_name.txt`, you will always have the same session name.  Each time you start a session, all database entries for that session are deleted.

- All files that begin with an underscore are temporary

- If the ‘`save = true`’ option is on in `config.toml`, all transactions are saved to `_allrecords.csv`, `_allrecords.json` (which seems broken), and `_buy_sell.json`

## Docker

To install via docker to avoid any system incompatibilites or to keep the v2bot modules from being installed into your existing environment: (NOTE: There is no GUI or graphs in the docker versions.  For that you need to install usign the above method)

Install docker

Presumeable you have alread git cloned the repo if you are reading this.  If not, you cen eiother do so…

```bash
git clone https://github.com/baardev/v2bot.git 
```

or just download the `Dockerfile` (you may need to install `wget`)

```bash
wget \ https://raw.githubusercontent.com/baardev/v2bot/main/Dockerfile
```

In any case, if the docker file exists, run:

```bash
docker build --tag v2bot ./
```

After some minutes of docker downloading and installing all the necessary software, you’ll see a something like the following at the end of the install.

```bash
Successfully built 4d5872a4c572  <- copy this number
Successfully tagged v2bot:latest
```

Now run the command, using the build number from above.

```bash
docker run -it 4d5872a4c572 bash
```

This will open a shell inside the docker container with a prompt like…

```bash
root@a9f429cecc85:/v2bot#
```

Here you need to run the command `DSTART` to initialize thne database.

```bash
./DSTART
```

One finished, you can run the bot which will user backtest data of 5min ETH/BTC transactions from Binance from january 1, 00:00, 2021 to Dec 11, 2021

```bash
./v2.py -n
```

the `-n/–nohead` switch turns off the GUI, which will not run insoide a docker container.

To delete all installed docker volumes and images:

```bash
docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)
```


## Binance notes
trade vals -> https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#new-order--trade

API how-to link -> https://algotrading101.com/learn/binance-python-api-guide/
Binance testnet -> https://testnet.binance.vision/
Spot Test API docs -> https://binance-docs.github.io/apidocs/spot/en/#change-log
CCXT Binance module -> https://github.com/ccxt/ccxt/blob/master/python/ccxt/binance.py#L88
Binance REST API v3 -> https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
Binance limit order -> https://www.r-bloggers.com/2021/11/binance-spot-trading-limit-orders/
exchange object/properties -> https://docs.ccxt.com/en/latest/manual.html

## Todo

Check JWFIX notes

## Process to generate backdata

Run generator with -d as the starting epoch stamp, and -i as the starting counter
`./ohlc_backdata.py -d 1514812800000 -i 0`

Optionally view the data
`./view.py -f data/backdata_ETH+BTC.5m.2018-01-01_13:20:00...2018-01-05_02:35:00.1000_binance_0.json`

Merge all the parts together with -f as the unique filename globber
`./merge.py -f backdata_ETH+BTC.5m. -i 9 -b 2021-10-03 -e 2021-11-05 -o bb `


To convert date string to epoch -> https://esqsoft.com/javascript_examples/date-to-epoch.htm

Sample data with from-to epoch times
- Oct  03, 2020 - Oct 19, 2020  1633230000 - 1634612400 (bear) 
- Oct 19, 2020 - Nov  02, 2020 1634612400 - 1634612400  (bull)
- Oct  03, 2020 - Nov  02, 2020 1633230000 - 1634612400 (bull and bear)

Time/date string format for using https://www.utilities-online.info/epochtime 

2021-09-05T03:19:00 = 1630822740
2021-09-06T00:04:00 = 1630897440

More info on time conversions...
    https://esqsoft.com/javascript_examples/date-to-epoch.htm

## Backdata wrapper

This correctly formats dates and automatially requests the data in 1000 lines per file request, with a 10 second pause, in the loop, then merges those files together.  Currently defaults to “ETH/BTC”.  To change, edit code.

```bash
./backdata.py -i 130 -d "2020-12-01 00:00:00" -o ETH1
```

-i = number of time to consequtively request data.  40 is roughly 6 months of 5m-interval data
-d = start date
-o = name of final file.  Creates 2 file… <name>.json and <name>_data.json


## References:

Examples of plots for matplotlib
https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html

Info on mplfinance vs matplotlib graphing
https://github.com/matplotlib/mplfinance/wiki/Acessing-mplfinance-Figure-and-Axes-objects

## python packages needed 

see ‘requirements.txt’

(can't install on 3.5 duncanstroud.com)

```bash
pip install MySQLdb
pip install coinbase_python3
```
## rsync

To cope everything to remote server

```bash
rsync -avr --exclude 'safe/*' --exclude 'venv/*' /home/jw/src/jmcap/ohlc/ jw@duncanstroud.com:/home/jw/src/jmcap/ohlc/
```

## Remote running/viewing

Note: Setting ‘display = false’  in config.toml stops all GUI output, and only outputs ANSI console data.

## remote connecting

Docs: https://en.wikipedia.org/wiki/Xvfb#Usage_examples

On Arch Linx, I needed to symlink v0 module to v1
`sudo ln -s /usr/lib/x86_64-linux-gnu/libxcb-util.so.0 /usr/lib/x86_64-linux-gnu/libxcb-util.so.1`

## run virtual screen manager on server
```bash
export DISPLAY=:1
Xvfb :1 -screen 0 1910x1280x24 &
fluxbox &
x11vnc -display :1 -bg -nopw -listen localhost -xkb
```
## tunnel to localhost locally
`ssh -N -T -L 5900:localhost:5900 jw@duncanstroud.com`

## view locally 
```bash
vncviewer -geometry 1920x1280 localhost:5900
vncviewerlocalhost:5900

```

## To shutdown vncserver
```bash
x11vnc -R stop (doesn't always work)
ps -ef |grep x11vnc|grep -v grep|awk '{print "kill -9 "$2}'|sh
ps -ef |grep fluxbox|grep -v grep|awk '{print "kill -9 "$2}'|sh
ps -ef |grep /usr/bin/terminator|grep -v grep|awk '{print "kill -9 "$2}'|sh
```
## Speed tests

with save-to-file option ON  =   16.05s user 6.54s system 45% cpu 49.787 total
with save-to-file option OFF =  16.14s user 6.42s system 53% cpu 42.476 total

Save ‘state’ to mem = 16.21s user 6.61s system 54% cpu 42.095 total
Save ‘state’ to file     = 15.96s user 6.46s system 56% cpu 39.530 total  (it’s actually faster!?!)


## coinbase specific utils
```bash
coinbase/auth_client.py     # * private API functions
coinbase/public_client.py   # * public API functions
coinbase/cb_order.py        # * CB order tests
```
### Modules
```bash
lib_v2_globals.py     # * global vars used across all code and modules
lib_v2_ohlc.py        # * functions for v2bot 
lib_panzoom.py        # * allows for the zoom function of the matpoltlib figures
lib_v2_tests_class.py # * Defines the logic tests for buy/sell
lib_v2_listener.py    # * keypoard listener, for interactive control at runtime
```
### Folders
```bash
data      # * dols backtest files, and word list
logs      # * all log get written to here
coinbase  # * all coinbase specific code

```
### OHLC utils
```bash
v2.py             # * the main routine
ohlc_backdata.py  # * grat a block of historical data and save locally
merge.py          # * merges data block from 'ohlc_backtest.py'
backdata.py       # * wrapper for ohlc_backtest.py and merge.py

INS.sh            # * shell script to copy critical files to run run in other dir
view.py           # * view dataframe (uses PandaGUI and/or Tabloo)
gview.py          # * graphican view of all transactions 
liveview.py       # * graphical view of all transactions in a loop
```
### Config files
```bash
config.toml       # * loads into g.cvars[] inside the loop
config_*.toml     # * saved versions of config files
state.json        #* files that hold values of runtime vars
```
### Output
```bash
_allrecords.csv   # * CSV version of all trx
_allrecords.json  # * JSON version of all trx.  DOESN'T LOQD CORRECTLY INTO DATAFRAME
_buysell.json     $ * recortd of buys/sells limited to the datrawindows size
_session_name.txt
```
### Docs
```bash
README.md
```

# Tables

[91301] [2021-11-14 00:20:00] Sold      0.46 @ $4,678.15 = $2,160.37 AVG: $4,668.48 Fee: $2.16 SessGross: $4.47 SessFee: $9.48 SessNet: $0.16 
 [2021-11-14 00:20:00] (composite/6:54:38) NEW CAP AMT: 6037.41698 (60.3742) Running Total: $ 8,823.90
[91308] [2021-11-14 00:55:00] [64990.53] Hold [S] 0.20 @ $4,676.52 = $935.30 AVG: $4,676.52 COV: $4,685.88 Fee: $0.94 QTY: 0.20
[91314] [2021-11-14 01:25:00] [64877.98] Hold [S] 0.20 @ $4,666.48 = $933.30 AVG: $4,671.50 COV: $4,680.84 Fee: $0.93 QTY: 0.40



## gaslight
Uses stepped next_buys to slow dip runs, no limit
```bash
pair:     BTC/USDT 
trx:      97117
start:    2021-01-01 00:00:00
lastsell: 2021-12-01 15:50:00
runtime:  4:20:35 
NEWCAP:   5358 (53.58) 
Total:    $ 169,879

MSE "select count(size),size from orders where session = 'gaslight' group by size order by size"

     2	5277	0.414000	BTC-USDT
     3	261	0.669850	BTC-USDT
     4	415	0.828000	BTC-USDT
     5	98	1.083820	BTC-USDT
     6	57	1.083850	BTC-USDT
     7	16	1.242000	BTC-USDT
     8	98	1.497850	BTC-USDT
     9	40	1.753620	BTC-USDT
    10	8	1.911850	BTC-USDT
    11	10	2.167670	BTC-USDT
    12	41	2.581670	BTC-USDT
    13	24	2.837350	BTC-USDT
    14	7	2.995670	BTC-USDT
    15	3	3.921290	BTC-USDT
    16	13	4.335290	BTC-USDT
    17	13	4.590840	BTC-USDT
    18	1	6.758650	BTC-USDT
    19	7	7.172650	BTC-USDT
    20	3	7.586650	BTC-USDT
    21	10	11.763500	BTC-USDT
    22	2	12.177500	BTC-USDT


next_buy_increments     = 0.00292                     # used to limit growing purchages
short_purch_qty         = 0.0414
long_purch_qty          = 0.0414
```
## composite
Uses stepped next_buys to slow dip runs, no limit
```bash
pair:     ETH/BTH 
trx:      91314
from:     2021-01-01 00:00:00
to:       2021-11-14 00:20:00 
runtime:  6:54:38
NEWCAP:   6037.41698 (60.3742) 
Total:    $ 8,823

MSE "select count(size),size from orders where session = 'composite' group by size order by size"|nl

largest qty:
    40	4	4.735620
    41	3	4.935620
    42	2	5.135620
    43	5	7.599870
    44	2	7.638640
    45	7	7.838640
    46	1	12.296600
    47	2	12.335720
    48	1	19.735600
    49	2	19.935600
    50	1	20.135599
    51	1	32.432201

```
- next_buy_increments = 0.001 
- g.next_buy_price = o.state_r('last_buy_price')* (1 - g.cvars['next_buy_increments'] * (o.state_r('curr_run_ct')*2))





## laminar 
Uses stepped next_buys to slow dip runs, no limit
```bash
pair:     BTC/USDT 
trx:      103327
from:     2021-01-01 00:00:00
to:       2021-12-25 18:30:00 
runtime:  4:56:48 
NEWCAP:   492.23567 (4.9224) 
Total:    $ 11,518 

MSE "select count(size),size from orders where session = 'laminar' group by size order by size"|nl

largest qty: 
    41	1	0.513560
    42	3	0.759980
    43	2	0.763860
    44	1	1.229660
    45	1	1.233570
    46	3	1.253570
    47	1	1.989590
    48	1	1.993560
    49	1	2.013560
    50	1	5.232810
```
- next_buy_increments = 0.001 
- g.next_buy_price = o.state_r('last_buy_price')* (1 - g.cvars['next_buy_increments'] * (o.state_r('curr_run_ct')*2))

## Binghamton
BTCUSDT 
max total purchase limit: none (up to 93)
next_buy_price 'nmod' = 1
```./report.py -s Binghamton -t 6_Binghamton -v 3 -f short``` = $64,495.93




## Recovery instruction for fubared boot
https://superuser.com/questions/111152/whats-the-proper-way-to-prepare-chroot-to-recover-a-broken-linux-installation

### VCE
https://code.visualstudio.com/docs/getstarted/keybindings



### TESTS



```
MSE "SELECT sum(runtot/(price*7))*100 as APR from purpose where side='sell'"
+---------------+
| APR           |
+---------------+
| 14.4668265292 |  << percent against the entire capital reserve
+---------------+
```

```
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
```

```
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
```

To update after merging

```

MSE "UPDATE orders SET netcredits = credits - fees "
MSE "UPDATE orders SET runtotnet = credits - fees"

SET @tots:= 0;
UPDATE orders SET fintot=null WHERE session='sessionname';
UPDATE orders SET runtotnet = credits - fees;
UPDATE orders SET fintot = (@tots := @tots + runtotnet) WHERE session = 'sessionname';
```



## Bibox info


https://biboxcom.github.io/v3/spot/en/#spot-trade-need-apikey

https://biboxcom.github.io/v3/spot/en/#place-an-order

# error codes (outdated and/or wrong)
https://biboxcom.github.io/en/error_code.html#%E9%94%99%E8%AF%AF%E7%A0%81


3025: Signature verification failed (签名验证失败)
2027: Insufficient available balance (可用余额不足)
2048: Illegal operation  (操作非法)


with 'display' on
    65.87s user 51.34s system 201% cpu 58.231 total
with 'display' oFF
    16.43s user 1.75s system 5% cpu 5:09.19 total



_buysell.json timestamp

1640796194431

_ohlcdata.jspon timestamp

1640795598229
