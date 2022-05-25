#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

from pyrogram import Client, __version__, enums
from pyromod import listen
from . import LOGGER, Config


class Bot(Client):

    def __init__(self):
        super().__init__(
            "bot",
            api_hash=Config.API_HASH,
            api_id=Config.APP_ID,
            plugins={
                "root": "bot/plugins"
            },
            workers=400,
            bot_token=Config.BOT_TOKEN
        )
        self.LOGGER = LOGGER


    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.set_parse_mode(enums.ParseMode.HTML)
        self.LOGGER(__name__).info(
            f"@{usr_bot_me.username}  started! "
        )

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped. Bye.")

