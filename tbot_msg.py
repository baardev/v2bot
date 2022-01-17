#!/usr/bin/python -W ignore

from telethon import TelegramClient
import lib_v2_globals as g
import lib_v2_ohlc as o
import time

g.keys = o.get_secret()
api_id = g.keys['telegram']['api_id']
api_hash = g.keys['telegram']['api_hash']
v2bot_remote_token = g.keys['telegram']['v2bot_cmd_token']
session_location = g.keys['telegram']['session_location']
sessionfile = f"{session_location}/v2bot_cmd.session"

name = g.keys['telegram']['v2bot_cmd_name']

# if g.issue == "LOCAL":
#     name = g.keys['telegram']['v2bot_name']


print(f"loading: {sessionfile}")
client = TelegramClient(sessionfile, api_id, api_hash)

async def main():
    await client.send_message(name, f'v2bot test message ({time.time()})...')
    # await client.send_message(5081499662, f'v2bot test message ({time.time()})...')

with client:
    client.loop.run_until_complete(main())
