# INSTALL

Install requited software

To install python3.9 -> https://www.vultr.com/docs/update-python3-on-debian

Install the following apps

```bash
apt install git
apt install wget
apt install qtcreator
apt install qtdeclarative5-dev
apt install gnumeric
apt install unzip
```

Create if necessary, and move to the root directory where you will install the bot, for example

```bash
mkdir ~/src
cd ~/src
```

Install src

```bash
git clone git@github.com:baardev/v2bot.git
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

Download data file into into the project data directoty, and unzip

https://mega.nz/file/F2x0WIqS#AcJZvEACTIYqo92PnKaCpjdpHm8hGk2H29dzUbtFl0g

```bash
cd ~/src/v2bot/data
wget -O data.zip  https://mega.nz/file/F2x0WIqS\#AcJZvEACTIYqo92PnKaCpjdpHm8hGk2H29dzUbtFl0g
unzip data.zip

```

Create a MySql database called ‘jmcap’, along with a user name and password.

Create an alias, replacing <uname> witjh a username and <pw> with a password

```bash
alias MSE="mysql -ujmc -pjmcpw jmcap -e "
alias MSX="mysql -ujmc -pjmcpw jmcap < "
```

The run the following tp create the database:

```sql
MSE "create database jmcap"
MSE "Grant ALL PRIVILEGES ON jmcap.* TO '<uname>'@'localhost' IDENTIFIED BY '<pw>';"
MSE "FLUSH PRIVILEGES;"

MSX schema.sql
 
```

Create a folder in your home directoty named `~/.secrets`

Inside the folder, create a file called `keys.toml`

For security reasons, you should run the following command to set the permissions of this files, especially as they will hold the API and secret keys of the  exchange.

`chmod -R  400 ~/.secrets`

The file must have at least the following:

```toml
[database]
	[database.jmcap]
		username = "<your database user name>"
		password = "<your database password>"
```

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

- If you open a new terminal to run the program, you must always run teh folloing first:

  ```bash
  cd ~/src/v2bot
  source venv/bin/activate
  ```

- Edit runtime parameters in `config.toml`

- Each time you run the program it creates  a session.  Each session is assigned a name.  Unless you delete the file `_session_name.txt`, you will always have the same session name.  Each time you start a session, all database entries for that session are deleted.

- All files that begin with an underscore are temporary

- If the ‘`save = true`’ option is on in `config.toml`, all transactions are saved to `_allrecords.csv`, `_allrecords.json` (which seems broken), and `_buy_sell.json`



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

Time/date striung format for using https://www.utilities-online.info/epochtime 

2021-09-05T03:19:00 = 1630822740
2021-09-06T00:04:00 = 1630897440

More info on time conversions...
    https://esqsoft.com/javascript_examples/date-to-epoch.htm

## Backdata wrapper

This correctly formats dates and automatially requests the data in 1000 lines per file request, with a 10 second pause, in the loop, then merges those files together.  Currently defaults to “ETH/BTC”.  To change, edit code.

```
./backdata.py -i 40 -d "2021-09-06 00:00:00" -o ETH1
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

```
pip install MySQLdb
pip install coinbase_python3
```
# rsync

To cope everything to remote server

```
rsync -avr --exclude 'safe/*' --exclude 'venv/*' /home/jw/src/jmcap/ohlc/ jw@duncanstroud.com:/home/jw/src/jmcap/ohlc/
```

# Remote running/viewing

Note: Setting ‘display = false’  in config.toml stops all GUI output, and only outputs ANSI console data.

## remote connecting

Docs: https://en.wikipedia.org/wiki/Xvfb#Usage_examples

On Arch Linx, I needed to symlink v0 module to v1
`sudo ln -s /usr/lib/x86_64-linux-gnu/libxcb-util.so.0 /usr/lib/x86_64-linux-gnu/libxcb-util.so.1`

## run virtual screen manager on server
```
export DISPLAY=:1
Xvfb :1 -screen 0 1910x1280x24 &
fluxbox &
x11vnc -display :1 -bg -nopw -listen localhost -xkb
```
## tunnel to localhost locally
`ssh -N -T -L 5900:localhost:5900 jw@duncanstroud.com`

## view locally 
```
vncviewer -geometry 1920x1280 localhost:5900
vncviewerlocalhost:5900

```

## To shutdown vncserver
```
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
```
auth_client.py
public_client.py
cb_cltool.py
cb_order.py
cbtest.py
```
### Modules
```
lib_v2_cvars.py
lib_v2_globals.py
lib_v2_ohlc.py
lib_panzoom.py
lib_v2_tests_class.py
lib_v2_listener.py
```
### Folders
```
data
logs

```
### OHLC utils
```
v2.py
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
config.toml
remote_config.json
state.json
```
### Output
```
_allrecords.csv
_allrecords.json
_buysell.json
_session_name.txt
```
### Docs
```
README.md
```

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



# Bibox info


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
