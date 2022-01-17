#!/usr/bin/python -W ignore
from telethon import TelegramClient
import lib_v2_globals as g
import lib_v2_ohlc as o
import time

# *  Remember to use your own values from my.telegram.org!

g.keys = o.get_secret()
api_id = g.keys['telegram']['api_id']
api_hash = g.keys['telegram']['api_hash']
v2bot_token = g.keys['telegram']['v2bot_token']
v2bot_remote_token = g.keys['telegram']['v2bot_remote_token']
session_location = g.keys['telegram']['session_location']
sessionfile = f"{session_location}/v2bot.session"

client = TelegramClient('session', api_id, api_hash)

async def main():
    # *  Getting information about yourself
    me = await client.get_me()

    # *  "me" is a user object. You can pretty-print
    # *  any Telegram object with the "stringify" method:
    print(me.stringify())

    # *  When you print something, you see a representation of it.
    # *  You can access all attributes of Telegram objects with
    # *  the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # *  You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)

    # *  * You can send messages to yourself...
    # ! can't see them in my chat
    # await client.send_message('me', 'Hello, myself!')

    # *  ...to some chat ID
    # ! to v2bot - automatically marked as read
    await client.send_message(5081499662, f'v2bot test message ({time.time()})...')
    # *  ...to your contacts
    # ! can's send to my own number
    # await client.send_message('+12675510003', 'Hello, friend!')
    # *  # *  ...or even to any username
    # await client.send_message('Peebsy', 'Testing Telethon!')

    # *  You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'Peebsy',
    #     'TEST MESSAGE: IGNORE  :/ This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )

    # *  Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # *  You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # *  * Or send files, songs, documents, albums...
    # ! saves to 'saved messages' in telegram
    # await client.send_file('me', '/home/jw/store/books/tholonia/Images/CRYSTAL.png')

    # *  You can print the message history of any chat:
    async for message in client.iter_messages('me'):
        print(message.id, message.text)

        # *  You can download media from messages, too!
        # *  The method will return the path where the file was saved.
        if message.photo:
            path = await message.download_media()
            print('File saved to', path)  # *  printed after download is done

with client:
    client.loop.run_until_complete(main())
