#!/usr/bin/python -W ignore

from telethon import TelegramClient
import lib_v2_globals as g
import lib_v2_ohlc as o
import time
import toml

g.cvars = toml.load(g.cfgfile)

g.keys = o.get_secret()
api_id = g.keys['telegram']['api_id']
api_hash = g.keys['telegram']['api_hash']
bot_remote_token = g.keys['telegram'][f"{g.cvars['name']}_cmd_token"]
session_location = g.keys['telegram']['session_location']
sessionfile = f"{session_location}/{g.cvars['name']}_cmd.session"

name = g.keys['telegram'][f"{g.cvars['name']}_cmd_name"]


print(f"loading: {sessionfile}")
client = TelegramClient(sessionfile, api_id, api_hash)

async def main():
    await client.send_message(name, f"{g.cvars['name']} test message ({time.time()})...")

with client:
    client.loop.run_until_complete(main())
