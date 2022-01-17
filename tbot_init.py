#!/usr/bin/python

from telethon import TelegramClient
import lib_v2_globals as g
import lib_v2_ohlc as o

g.keys = o.get_secret()
api_id = g.keys['telegram']['api_id']
api_hash = g.keys['telegram']['api_hash']
# v2bot_token = g.keys['telegram']['v2bot_token']
# v2bot_remote_token = g.keys['telegram']['v2bot_remote_token']
session_location = g.keys['telegram']['session_location']
sessionfile = f"{session_location}/v2bot_remote_cmd.session"

# token = g.keys['telegram']['v2bot_remote_token']
# with open('issue', 'r') as f:
#     g.issue = f.readline().strip()
# if g.issue == "LOCAL":
#     token = g.keys['telegram']['v2bot_token']

phone = '+12675510003'

client = TelegramClient(sessionfile, api_id, api_hash)
# client.connect()
client.start(phone=phone)

print(f"Telegram Session Initialised (session file = {sessionfile}")

client.disconnect()
