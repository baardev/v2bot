
## Todo

Check JWFIX notes

add subdir to /tmp/ files



# INSTALL

## Assumtions

The code expect epochs in milliseconds (from time.time()), for example, 1641838978722, which is 1641838978.722 seconds.  If you system does not support millisecond epochs your times will be FUBARed.

## Installation

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

NOTE: There is a `.secrets/keys.toml` file in the git repo as well that is prefilled specifically to be used for docker, if you choose that option (see below).  The program will first look in your home dir for the `.secrets/keys.toml`, and if none is found, it will look in the v2bot working directory. You can choose to create a home directory file, or edit the working directory file… but if you do, docker will fail. It’s recomended to use the home directory file for system install, and the working directory file for docker.

Make the program executable

```bash
cd ~/src/v2bot
chmod 755 ./v2.py
```

### The following files and conditions must exist before running:

`issue` : This is a text file with either word LOCAL or REMOTE in it, no carrianeg return, all caps.  This tells the bot which machine it is running on, REMOTE being the live server.

Only `testpairs` (variable in `config.toml`) that d NOT contain teh word “perf” in them can be used prior to buildign the n-bit performance databases.



Run the program

```bash
./v2.py
```

NOTES:

- ~~If you open a new terminal to run the program, you must always run the following first:~~

  ~~cd ~/src/v2bot~~
  ~~source venv/bin/activate~~


- Edit runtime parameters in `config.toml`

- Each time you run the program it creates  a session.  Each session is assigned a name.  Unless you delete the file `_session_name.txt`, you will always have the same session name.  Each time you start a session, all database entries for that session are deleted.

- All files that begin with an underscore are temporary

- If the ‘`save = true`’ option is on in `config.toml`, all transactions are saved to `/tmp/<sessionname>/_allrecords.csv` and `/tmp/<sessionname>/_allrecords.json` (JSON verion might be broken), and `/tmp/<sessionname>/_buy_sell.json`

## Docker (outdated)

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

## Telegram

On Debian 9 server, needed to compile python 3.6 locally, with openssl and sqlite3 support

https://gist.github.com/bebosudo/7b1c0650e2f94d26afe830530764de65

To install modules, need to use pip3.6.  3.6 is installed in  `~/.local`

```
 ~/.local/bin/pip3.6 install telegram
```

Create a new bot buy going to ‘botfather’ telegram account, and typing “/newbot”

Run `tbot_init.py` to initialize the seesion file.  Edit `sessionfile` var in the code to match the correct file location/name.

```
sessionfile = f"{session_location}/v2bot_remote_cmd.session"
```

Update server with new  `tbot_init.py`  and with any changes to `~/.secrets/keys.toml`

On server, run the following. Get number form message to @telegram channel

```
./tbot_init.py 
Please enter the code you received: *****
Signed in successfully as Mishrasigni
Telegram Session Initialised (session file = /home/jw/v2bot_remote_cmd.session
```

command funtions require the following.

In root’s crontab:

```
* * * * * /home/jw/src/jmcap/v2bot/root_launcher.py > /tmp/_root_launcher.log 2>&1
```



## Local Bots

### @v2bot (v2jwbot)

- ~/v2bot.session
- `keys[‘telegram’]['v2bot_token']`

### @v2bot_cmd (v2jwcmdbot)

- ~/v2bot_cmd.session
- `keys[‘telegram’]['v2bot_cmd_token']`



## Remote Bots

### @v2bot_remote (v2jwremotebot)

- jw@108.161.133.254:~/v2bot.session
- `keys[‘telegram’]['v2bot_remote_token']`

### @v2bot_remote_cmd (v2jwremotecmdbot)

- jw@108.161.133.254~/v2bot_cmd.session
- `keys[‘telegram’]['v2bot_remote_cmd_token']`



## python packages needed 

see ‘requirements.txt’

(can't install on 3.5 duncanstroud.com)

```bash
pip install MySQLdb
pip install coinbase_python3
```
### Performance

with 'display' on:    65.87s user 51.34s system 201% cpu 58.231 total
with 'display' off:   16.43s user 1.75s system 5% cpu 5:09.19 total

**Also, when running with display, the overhead slows the process enough to miss triggers**

# References

## Binance notes

trade vals -> https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#new-order--trade

API how-to link -> https://algotrading101.com/learn/binance-python-api-guide/
Binance testnet -> https://testnet.binance.vision/
Spot Test API docs -> https://binance-docs.github.io/apidocs/spot/en/#change-log
CCXT Binance module -> https://github.com/ccxt/ccxt/blob/master/python/ccxt/binance.py#L88
Binance REST API v3 -> https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
Binance limit order -> https://www.r-bloggers.com/2021/11/binance-spot-trading-limit-orders/
exchange object/properties -> https://docs.ccxt.com/en/latest/manual.html

## matplotlib

Examples of plots for matplotlib
https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html

Info on mplfinance vs matplotlib graphing
https://github.com/matplotlib/mplfinance/wiki/Acessing-mplfinance-Figure-and-Axes-objects

# Procedures/man

## ./b_wss.py
```bash
./b_wss.py -v -p BTC/USDT
./b_wss.py --verbose --pair BTC/USDT
```
background process to read and save WSS orderbook data from Binance.

`-v/--verbose`: Outputs each line to TTY (ANSI)
`-p/--pair`: Standards pair notation (defaults to config.toml)

Outputs:

Reads the config list var ‘wss_filters’ (ex. `[0,1,2,4,6]`), to determine what cumulative delta sums to filter on.

tmp file: `/tmp/_<PAIR>_<fFILTERVAL>m.tmp` 
final ‘live’ file:`/tmp/_<PAIR>_<fFILTERVAL>m.tmp` 

**‘Live’ files are those that are only good until the next wss input (about 1 sec), which is why they are stored in the low-overhead tmpfs /tmp folder**

***Both of these files are deleted as soon as they are used, as the program waits on a new file to trigger its loop***

Examples:

```
/tmp/_BTCUSDT_4f.jtmp
/tmp/_BTCUSDT_4f.json
```
historcal csv file: `data/<PAIR>_<FILTERVAL>.csv`
historcal json file: `data/<PAIR>_<FILTERVAL>`

Examples:

```bash
data/BTCUSDT_4f.csv
data/BTCUSDT_4f.json
```

*Note: The timestamps for streaming data is modifier to make each record on second apart.  This is to compensate for issues with trying to plot a non-linear x-axis*

## perfbits<234>.py

‘perfbits.py’ builds predictive performance specs bast on the previous *n* close values.  

Outputs:

The results are stoed in the SQL table ‘rootperf’ as well as a JSON which is loaded into an object at runtime and used (mainly) in teh test cases.

```bash
data/perf_<BITS>_<PAIR>_<CHART>.json
data/perf_6_BTCUSDT_0m.json
```

Example: 

```bash
./perfbits4.py -c 1m -f 0 -b 16 -p BTC/USDT -s data/BTCUSDT_1m_0f.json  
./perfbits.py -c 5m -b 6 -p BTC/USDT -s data/2_BTCUSDT.json
./perfbits.py --chart 5m --bits 6 --pair BTC/USDT --src data/2_BTCUSDT.json
```

`-c/--chart`: The same time value string used when creating teh data file, typically, ‘1m’,’5m’,’30m’, etc.  ‘0m’ means the data is WSS order-book data.
`-b/--bits`: The number of past values to analyze and reduce to a series or 1/0s
`-p/--pair`: Typical base/quote format
`-s/--src`: Path/Name of existing JSON file in format of a Binance OHLC download
`-n/--count`: (not shown) limit count ot *n*
`-f/--filter`: filter value (default = 0)
`-v/--version`: versions (currently not used)
`-y/--autoyes`: auto yes at each prompt

Example query of perf data:

```bash
MSE "select perf, bits, pair, chart from rootperf where bits = 16 and pair = 'BTC/USDT' and chart = '0m' order by perf"
MSE "select * from rootperf where bits = 6 and pair = 'BTC/USDT' and chart = '0m' order by perf"
```
Process wss data 
```bash
./perfbits.py -c 0m -f 4 -b 6 -p BTC/USDT -s data/BTCUSDT_0m_4f.json  # WSS data
./perfbits.py -c 5m -f 0 -b  6 -p BTC/USDT -s data/BTCUSDT_5m_0f.json # 5m OHLC data
```

## Use case example

To create a chart for streaming data that has been filter by 64 with a performance metrics:

Make sure you have a filter set in config.toml

```
wss_filters = [0,2,4,8,16,32,64]
```

Select a testing pair where the BUY test uses performace metrics in **config.toml**

```
stream.testpair     = ["BUY_perf","SELL_tvb3"]
```

create the performance metris on the filter=32 data

```
./soundex.py -c 0m -b 6 -p BTC/USDT -f 32 -s data/BTCUSDT_0m_32f.json
```

This creartes the file:

```
data/perf_6_BTCUSDT_0m_32f.json
```

This is the path/filename that is recreated by the valus of the folloing **config.toml** vars:

```
pair = "BTC/USDT"
perf_bits  = 6
perf_filter = 32
stream.timeframe = "0m"
```

**Make sure the filter val for `perf_filter` and `wss_data` match.**



## ~~filter_data.py (obfuscated)~~

~~Remove all data that is below the ‘limit’.  ‘limit’ is compared agains the cumulative sum of the differences of since the prevouus limit.~~

~~Currently, all vars are hardcoded~~

```
./filter_data.py -l 10 -p BTC/USDT -c 5m -s data/2_BTCUSDT.json
```

## Create perf data

Fill the `rootperf4` table with analysed data from raw dataset
```bash
./perfbits4.py -c 1m -f 0 -b 16 -p BTC/USDT -s data/BTCUSDT_1m_0f.json  
```
Build json object from DB perf data, save to ```data/_perv4.json```
```bash
./perf4gen.py
```



## Init and run Telegram bots






# How-To

## Create unfiltered backtest chart data

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

**Using Backdata wrapper**

This correctly formats dates and automatially requests the data in 1000 lines per file request, with a 10 second pause, in the loop, then merges those files together.  Currently defaults to “ETH/BTC”.  To change, edit code.

```bash
./backdata.py -i 130 -d "2020-12-01 00:00:00" -o ETH1
```

`-i/--index`: = number of time to consequtively request data.  40 is roughly 6 months of 5m-interval data
`-d/--date`:  start date
`-o/--outfile`:  name of final file.  Creates 2 file… <name>.json and <name>_data.json
`-m/--manual`: prompt fpr each load
`-p/--pair`:  BASE/QUOTE

Add output file name to config.toml in ‘backtest’ section



## ssh tunneling mysql

```bash
ssh -N -L 3336:127.0.0.1:3306 jw@108.161.133.254 &
https://thehypercommunity.net/index.html
```

or, after running `source ./aliases`

```bash
RMSE "select price from orders where session = 'Arcadia' and side = 'buy'"
```

## aliases

```bash
alias MSE="mysql -uroot -pedcrfv314 jmcap -e "
alias MSX="mysql -uroot -pedcrfv314 jmcap < "

alias RMSE="mysql -ujmc -p6kjahsijuhdxhgd -h 127.0.0.1 jmcap -e "
alias RMSX="mysql -ujmc -p6kjahsijuhdxhgd -h 127.0.0.1 jmcap < "

# user granted with:
# GRANT ALL PRIVILEGES ON *.* TO 'jmc'@'%' IDENTIFIED BY '6kjahsijuhdxhgd' WITH GRANT OPTION;
# FLUSH PRIVILEGES;
```

## rsync

To copy everything to remote server

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

## 

# Files

## coinbase specific utils

```bash
coinbase/auth_client.py     # * private API functions
coinbase/public_client.py   # * public API functions
coinbase/cb_order.py        # * CB order tests
```

## Modules

```bash
lib_v2_globals.py     # * global vars used across all code and modules
lib_v2_ohlc.py        # * functions for v2bot 
lib_panzoom.py        # * allows for the zoom function of the matpoltlib figures
lib_v2_tests_class.py # * Defines the logic tests for buy/sell
lib_v2_listener.py    # * keypoard listener, for interactive control at runtime
lib_v2_binance    # * binance-only functions
```

## Folders

```bash
data      # * dols backtest files, and word list
logs      # * all log get written to here
coinbase  # * all coinbase specific code
sql
tgz
images

```

## OHLC utils

```bash
v2.py             # * the main routine
ohlc_backdata.py  # * grat a block of historical data and save locally

merge.py          # * merges data block from 'ohlc_backtest.py'
backdata.py       # * wrapper for ohlc_backtest.py and merge.py
check_data.py

INS
INS.sh            # * shell script to copy critical files to run run in other dir

is_running.py
root_launcher.py

read_stream.py

creplace.py

PUSH
PUB

```
## Binance tools

```bash

b_wss.py
b_bal.py
b_monitor.py
b_openorders.py
b_sellallbtc.py
b_balances.py

b_api.py
b_bal_csv.py
b_bestpairs.py
b_buysell.py
b_depth.py
b_orderbook.py
b_plot_depth.py
b_plot_volprice.py

```
## Viewers
```bash
view.py              # * view dataframe (uses PandaGUI and/or Tabloo)
gview.py          	# * graphican view of all transactions 
liveview.py       	# * graphical view of all transactions in a loop
dbview.py
pread.py
j_plot_port.py  	# used for tbot 
j_plot_profit.py	# used for tbot
report.py

```
## Performance data

```bash
perfbits.py
perfbits2.py
perfbits3.py
perfbits4.py
plot_perfbits.py
perf4gen.py

```
## Bot
```bash
tbot_init.py
tbot_listen.py
tbot_msg.py
telegram_api_test.py

```

## Misc


```bash
ncurses.py
setup.py
test.py
x.py
```

### Config files

```bash
config.toml                    # * loads into g.cvars[] inside the loop
config_template.toml     # meant to be used as a base config for creplace.py
config_*.toml                 # * saved versions of config files
state.json                       #* files that hold values of runtime vars
```

### Output

```bash
_allrecords.csv   # * CSV version of all trx
_allrecords.json  # * JSON version of all trx.  DOESN'T LOAD CORRECTLY INTO DATAFRAME
_buysell.json     $ * recortd of buys/sells limited to the datrawindows size
_session_name.txt
```

### Docs

```bash
README.md
```

## File names
```bash
0_BTCUSD	            # BTC/USD data (used for price conversion for ???/BTC b)
BTCUSDT_5m              # 5 min OHLC data
BTCUSDT_0m 			    # stream data
BTCUSDT_0m_0f           # unfiltered stream data  
BTCUSDT_0m_4f  	        # stream data with a cum-delta filer of 4 
perf_6_BTCUSDT_0m.json  # performance data (6 bit patterns on stream data)
```

# Run Scenarios



| Location         | Name    | Data      |Amts   |Algo           |Specs   |Return             | %     |Issues|Length|
| ----------------- |:---------:|:---------:|:-------:|:-------------:|:-------:|:-----------------:|------:|-------:|-------:|
|whalebone        |**B1**| backtest| lev      | BUY_perf/16 |   | \$178,823  | 557  | I.F. 5/19 - 8/09|5m/1yr|
|auxin          |**B2**| backtest| lev | BUY_perf/3  |    | \$172,937 | 420|x|5m/1yr|
|Arcadia      |**B3**| backtest| lev | BUY_perf/16 |mult=1.414       | $237,873 | 594 | I.F. 5/19 - 8/09|5m/1yr|
|memorable|**B4**| backtest| lev  | BUY_perf/6 |     |  \$390,611 | 987 | x|5m/1yr|



| Location         | Name    | Data      |Amts   |Algo           |Specs   |Return             | %     |Issues|Length|
| ----------------- |:---------:|:---------:|:-------:|:-------------:|:-------:|:-----------------:|------:|-------:|-------:|
|Rome         |**S1**| stream| lev | BUY_perf/16 |  |  n/a | n/a | PENDING | realtime|
|Cody               |**S2**| stream| testnet | BUY_perf/16 |  |  n/a | n/a | PENDiNG | realtime|



### Cleanign junk data from json files

```
perl -pi -e 's/\\u0000//gmi' data/BTCUSDT_0m_0f.json               
perl -pi -e 's/\\x00//gmi' data/BTCUSDT_0m_0f.json 
```

### 
