import datetime
import asyncio
import sys
from pyrogram import Client
from config import *
from database import db
from helpers import temp, ping_server
from utils import broadcast_admins

import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)


if REPLIT:
    from flask import Flask, jsonify
    from threading import Thread
    
    app = Flask('')
    
    @app.route('/')
    def main():
        
        runtime = datetime.datetime.now()
        t = runtime - temp.START_TIME
        runtime = str(datetime.timedelta(seconds=t.seconds))
        
        res = {
            "status":"running",
            "hosted":"replit.com",
            "repl":REPLIT,
            "bot":temp.BOT_USERNAME,
            "runtime":runtime
        }
        
        return jsonify(res)

    def run():
      app.run(host="0.0.0.0", port=8000)
    
    async def keep_alive():
      server = Thread(target=run)
      server.start()


class Bot(Client):

    def __init__(self):
        super().__init__(
        "shortener",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
        )

    async def start(self):  

        if REPLIT:
            await keep_alive()

            asyncio.create_task(ping_server())

        temp.START_TIME = datetime.datetime.now()
        await super().start()
        me = await self.get_me()
        self.username = f'@{me.username}'
        temp.BOT_USERNAME = me.username
        temp.FIRST_NAME = me.first_name

        if not await db.get_bot_stats():
            await db.create_stats()

        if FILE_STORE:
            try:
                
                db_channel = await self.get_chat(FILE_STORE_DB)
                temp.DB_CHANNEL = db_channel
                test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
                await test.delete()
            except Exception as e:
                logging.error(e)
                sys.exit()

            await broadcast_admins(self, '** Bot started successfully **')
            logging.info('Bot started')

    async def stop(self, *args):
        await broadcast_admins(self, '** Bot Stopped Bye **')
        await super().stop()
        logging.info('Bot Stopped Bye')

