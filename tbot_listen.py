#!/usr/bin/python -W ignore

from telethon import TelegramClient
from telegram import Update #upm package(python-telegram-bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext  #upm package(python-telegram-bot)
import os
import lib_v2_globals as g
import lib_v2_ohlc as o
import psutil

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
token = g.keys['telegram']['v2bot_cmd_token']
session_location = g.keys['telegram']['session_location']
sessionfile = f"{session_location}/v2bot_cmd.session"
print(f"loading: {sessionfile}")
client = TelegramClient(sessionfile, api_id, api_hash)

# client.send_message(5081499662, f'listeningv...')

def help_command(update: Update, context: CallbackContext) -> None:
    htext = '''
/dbstat - DB status
/restartdb - RestartDB
/stopbot - Stop bot
/startbot - Start bot
/df - df report
'''
    update.message.reply_text(htext)

def dbstat_command(update: Update, context: CallbackContext) -> None:
    os.system("systemctl status mariadb|grep Active > /tmp/_dbstat")
    with open('/tmp/_dbstat', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def restartdb_command(update: Update, context: CallbackContext) -> None:
    htext = 'Restarting MariaDB'
    update.message.reply_text(htext)

def botstat_command(update: Update, context: CallbackContext) -> None:
    htext = statProcessRunning("v2.py")
    update.message.reply_text(htext)

def stopbot_command(update: Update, context: CallbackContext) -> None:
    htext = killProcessRunning("v2.py")
    update.message.reply_text(htext)

def startbot_command(update: Update, context: CallbackContext) -> None:
    os.system("nohup ./v2.py &")
    htext = "Bot started"
    update.message.reply_text(htext)

def isrunning_command(update: Update, context: CallbackContext) -> None:
    htext = statProcess("v2.py")
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
    update.message.reply_text(htext)

def tail_command(update: Update, context: CallbackContext) -> None:
    os.system("tail nohup.out|grep -v '\r' > /tmp/_tail")
    with open('/tmp/_tail', 'r') as file: htext = file.read()
    update.message.reply_text(htext)

def main():
    updater = Updater(token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", help_command))
    dispatcher.add_handler(CommandHandler("h", help_command))
    dispatcher.add_handler(CommandHandler("dbstat", dbstat_command))
    dispatcher.add_handler(CommandHandler("restartdb", restartdb_command))
    dispatcher.add_handler(CommandHandler("stopbot", stopbot_command))
    dispatcher.add_handler(CommandHandler("startbot", startbot_command))
    dispatcher.add_handler(CommandHandler("bs", botstat_command))
    dispatcher.add_handler(CommandHandler("df", df_command))
    dispatcher.add_handler(CommandHandler("isr", isrunning_command))
    dispatcher.add_handler(CommandHandler("sus", suspend_command))
    dispatcher.add_handler(CommandHandler("res", resume_command))
    dispatcher.add_handler(CommandHandler("tail", tail_command))

    updater.start_polling()

    # updater.idle()

# with client:
#     client.loop.run_until_complete(main())


if __name__ == '__main__':
    main()