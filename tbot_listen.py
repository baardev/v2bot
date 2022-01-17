#!/usr/bin/python

from telethon import TelegramClient

from telegram import Update # * upm package(python-telegram-bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext  #upm package(python-telegram-bot)
import os
import lib_v2_globals as g
import lib_v2_ohlc as o
import psutil
import time, datetime

g.issue = o.get_issue()

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
    htext = '''
/rdb      - Restart DB
/dbstat   - DB status

/stopbot  - Stop bot
/startbot - Start bot
/sus      - Suspend bot
/res      - Resume bot

/start | /h | /bs Bot status | /tail nohup.out | /tl tail listener log | /df HD report
'''

    update.message.reply_text(htext)
    # update.message.reply_markdown(htext)

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
    dispatcher.add_handler(CommandHandler("start", help_command))
    dispatcher.add_handler(CommandHandler("h", help_command))
    dispatcher.add_handler(CommandHandler("dbstat", dbstat_command))
    dispatcher.add_handler(CommandHandler("rdb", restart_db_command))
    dispatcher.add_handler(CommandHandler("stopbot", stopbot_command))
    dispatcher.add_handler(CommandHandler("startbot", startbot_command))
    dispatcher.add_handler(CommandHandler("bs", botstat_command))
    dispatcher.add_handler(CommandHandler("df", df_command))
    dispatcher.add_handler(CommandHandler("sus", suspend_command))
    dispatcher.add_handler(CommandHandler("res", resume_command))
    dispatcher.add_handler(CommandHandler("tail", tail_command))
    dispatcher.add_handler(CommandHandler("tl", tail_listener_command))

    updater.start_polling()

    # updater.idle()

# with client:
#     client.loop.run_until_complete(main())


if __name__ == '__main__':
    main()