#!/usr/bin/python

from telethon import TelegramClient

from telegram import Update # * upm package(python-telegram-bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext  #upm package(python-telegram-bot)
import os
import lib_v2_globals as g
import lib_v2_ohlc as o
import psutil
import time, datetime
import subprocess
from subprocess import Popen


g.issue = o.get_issue()

lary = [
    ["h",       "help_command",         "Help"],
    ["start",   "help_command",         "Help"],
    ["#",       "------------",         "------"],
    ["dbs",     "dbstat_command",       "DB status"],
    ["rdb",     "restart_db_command",   "Restart DB"],
    ["bs",      "botstat_command",      "Bot status"],
    ["sus",     "suspend_command",      "Suspend bot"],
    ["res",     "resume_command",       "Resume bot"],
    ["sbot",    "stopbot_command",      "Stop bot"],
    ["kbot",    "startbot_command",     "Start bot"],
    ["rlis",    "restart_lis_command",     "Restart listener"],
    ["klis",    "kill_lis_command",     "Kill listener"],
    ["#",       "------------",         "------"],
    ["df",      "df_command",           "'df -h'"],
    ["tail",    "tail_command",         "Tail nohup"],
    ["tl",      "tail_listener_command","Tail listener.log"],
    ["#", "------------", "------"],
    ["btb",     "bt_bal_command", "BT Bal"],
    ["bsa",     "bt_sallall_command", "BT sell all BTC"],
    ["#", "------------", "------"],
    ["vvp",     "b_plotvolprice_command", "Plot vol/price"],
    ["vdp",     "b_plotdepth_command", "Plot depth"],
    ["vp",      "b_plotprofit_command", "Plot profit"],
]

def loqreq(msg):
    with open("logs/listener.log", 'a+') as file:
        file.write(f"[{get_timestamp()}] {msg}\n")

def get_timestamp():
    tt = datetime.datetime.fromtimestamp(time.time())
    ts = tt.strftime("%b %d %Y %H:%M:%S")
    return f"{ts}"

def getsecs():
    tt = datetime.datetime.fromtimestamp(time.time())
    secs = int(tt.strftime("%S"))
    return 60-secs

def touch(fn):
    with open(fn, 'w') as file:
        file.write("")

def checkIfProcessRunning(processName):
    for proc in psutil.process_iter():
        try:
            for i in proc.cmdline():
                if i.find(processName) != -1:
                    return i
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def killProcessRunning(processName):
    for proc in psutil.process_iter():
        try:
            for i in proc.cmdline():
                if i.find(processName) != -1:
                    proc.kill()
                    return f"{proc.pid} killed"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def statProcess(processName):
    for proc in psutil.process_iter():
        try:
            for i in proc.cmdline():
                if i.find(processName) != -1:
                    id = proc.pid
                    nm = proc.name()
                    ir = proc.is_running()
                    return f"{id}: {nm} up:{ir}"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def suspendProcess(processName):
    for proc in psutil.process_iter():
        try:
            for i in proc.cmdline():
                if i.find(processName) != -1:
                    proc.suspend()
                    nm = proc.name()
                    return f"SUSPENDED: {nm}"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def resumeProcess(processName):
    for proc in psutil.process_iter():
        try:
            for i in proc.cmdline():
                if i.find(processName) != -1:
                    proc.resume()
                    nm = proc.name()
                    return f"RESUMED: {nm}"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

g.keys = o.get_secret()
api_id = g.keys['telegram']['api_id']
api_hash = g.keys['telegram']['api_hash']
session_location = g.keys['telegram']['session_location']

#* for LOCAL
sessionfile = f"{session_location}/v2bot_cmd.session"
token = g.keys['telegram']['v2bot_cmd_token']
if g.issue == "REMOTE":
    sessionfile = f"{session_location}/v2bot_remote_cmd.session"
    token = g.keys['telegram']['v2bot_remote_cmd_token']

print(f"loading: {sessionfile}")
client = TelegramClient(sessionfile, api_id, api_hash)

# client.send_message(5081499662, f'listeningv...')

def help_command(update: Update, context: CallbackContext) -> None:
    htext = ""
    for i in range(len(lary)):
        if lary[i][0] != "#":
            htext += f"/{lary[i][0]} {lary[i][2]}\n"
        else:
            htext += "\n"
    update.message.reply_text(htext)

def bt_bal_command(update: Update, context: CallbackContext) -> None:
    command = "./b_balances.py > /tmp/_b_bal"
    os.system(command)
    with open('/tmp/_b_bal', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def bt_sallall_command(update: Update, context: CallbackContext) -> None:
    command = "./b_sellallbtc.py > /tmp/_b_sellall"
    os.system(command)
    with open('/tmp/_b_sellall', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def b_plotvolprice_command(update: Update, context: CallbackContext) -> None:
    command = "./b_plot_volprice.py > /dev/null 2>&1"
    os.system(command)
    update.message.reply_document(document=open("images/plot_volprice.png",'rb'))
    os.remove("images/plot_volprice.png")

def b_plotdepth_command(update: Update, context: CallbackContext) -> None:
    command = "./b_plot_depth.py > /dev/null 2>&1"
    os.system(command)
    update.message.reply_document(document=open("images/plot_depth.png",'rb'))
    os.remove("images/plot_depth.png")

def b_plotprofit_command(update: Update, context: CallbackContext) -> None:
    command = "./j_plot_profit.py > /dev/null 2>&1"
    os.system(command)
    update.message.reply_document(document=open("images/plot_profit.png",'rb'))
    os.remove("images/plot_profit.png")

def dbstat_command(update: Update, context: CallbackContext) -> None:
    if g.issue == "LOCAL":
        os.system("systemctl status mariadb|grep Active > /tmp/_dbstat")
    if g.issue == "REMOTE":
        os.system("systemctl status mysql|grep Active > /tmp/_dbstat")
    with open('/tmp/_dbstat', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def restart_db_command(update: Update, context: CallbackContext) -> None:
    touch("/tmp/_rl_restart_mysql")
    htext = f'Restarting MariaDB in {getsecs()} secs.'
    update.message.reply_text(htext)

def botstat_command(update: Update, context: CallbackContext) -> None:
    htext = statProcess("v2.py")
    update.message.reply_text(htext)

def stopbot_command(update: Update, context: CallbackContext) -> None:
    htext = killProcessRunning("v2.py")
    update.message.reply_text(htext)

def startbot_command(update: Update, context: CallbackContext) -> None:
    os.system("nohup ./v2.py &")
    htext = "Bot started"
    update.message.reply_text(htext)

def kill_lis_command(update: Update, context: CallbackContext) -> None:
    killProcessRunning("tbot_listener.py")

def restart_lis_command(update: Update, context: CallbackContext) -> None:
    os.system("restart_listener.sh")
    # htext = "Bot started"
    # update.message.reply_text(htext)

def suspend_command(update: Update, context: CallbackContext) -> None:
    htext = suspendProcess("v2.py")
    update.message.reply_text(htext)

def resume_command(update: Update, context: CallbackContext) -> None:
    htext = resumeProcess("v2.py")
    update.message.reply_text(htext)

def df_command(update: Update, context: CallbackContext) -> None:
    os.system(" df -h|grep -v loop|grep -v tmp|grep -v run|grep dev > /tmp/_dstats")
    with open('/tmp/_dstats', 'r') as file: htext = file.read()
    loqreq("/df")
    update.message.reply_text(htext)

def tail_command(update: Update, context: CallbackContext) -> None:
    os.system("tail nohup.out|grep -v '\r' > /tmp/_tail")
    with open('/tmp/_tail', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def tail_listener_command(update: Update, context: CallbackContext) -> None:
    os.system("nl logs/listener.log|tail > /tmp/_tail_listener")
    with open('/tmp/_tail_listener', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def main():
    updater = Updater(token)
    dispatcher = updater.dispatcher
    for i in range(len(lary)):
        if lary[i][0] != "#":
            dispatcher.add_handler(CommandHandler(lary[i][0], eval(lary[i][1])))
    updater.start_polling()
    print("Listening...")
    # updater.idle()

if __name__ == '__main__':
    main()