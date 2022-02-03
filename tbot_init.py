#!/usr/bin/python

from telethon import TelegramClient
import lib_v2_globals as g
import lib_v2_ohlc as o
import toml

g.cvars = toml.load(g.cfgfile)
g.keys = o.get_secret()
api_id = g.keys['telegram']['api_id']
api_hash = g.keys['telegram']['api_hash']
session_location = g.keys['telegram']['session_location']
sessionfile = f"{session_location}/{g.cvars['name']}_remote_cmd.session"

phone = '+12675510003'

client = TelegramClient(sessionfile, api_id, api_hash)
# client.connect()
client.start(phone=phone)

print(f"Telegram Session Initialised (session file = {sessionfile}")

client.disconnect()
