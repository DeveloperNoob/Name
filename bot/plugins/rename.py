#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import asyncio
import datetime
import os
import time
import mimetypes

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ForceReply

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from bot.config import Config

from bot.plugins import LOGGER, DATA
from bot.helpers.utils import *
from bot.helpers.progress import *
from bot.helpers.ffmpeg_utils import *
from bot.database.database import Database


logger = LOGGER(__name__)
db = Database()

def get_media(m):
    typs = ("audio", "video", "document")
    for typ in typs:
        res = getattr(m, typ, None)
        if res:
            return res, typ
    else:
        return '', None


@Client.on_message((filters.document | filters.video | filters.audio) & filters.private, 1)
async def recive_file(b: Client, m: Message):
    
    media_atrb, typ = get_media(m)
    q = await m.reply(
        f"<i><b>📑 File Name:</b>< <code>{media_atrb.file_name}</code>\n\n"
        f"<b>🗂 Type:</b> <code>{typ}</code>\n\n"
        "<b>Changing Your Thumbnail and Caption..!</b></i>",
        True,
        enums.ParseMode.HTML
    )
    a = asyncio.create_task(change_thum_and_caption(b, m))
    a.add_done_callback(q.delete)
    # await q.delete()


async def change_thum_and_caption(bot: Client, update: Message):

    # Retriving Media msg using get_messages() which is replied by the ForceReply mesg
    media_message = update
    media_atrb, typ = get_media(media_message)

    filesize = humanbytes(media_atrb.file_size)
    file_name = media_atrb.file_name
    del media_atrb


    msg = await update.reply('Processing....⏳', True)
    msg.from_user = update.from_user

    prgs = Progress(update.from_user.id, bot, msg)
    path = await media_message.download(
        file_name=f"{update.from_user.id}/{int(update.date.timestamp())}/",
        progress=prgs.progress_for_pyrogram,
        progress_args=(
            "Downloading Your File....!",
            time.time()
        )
    )

    if path is None:
        return

    duration = 0
    metadata = extractMetadata(createParser(path))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
    del metadata

    DATA[msg.id] = {}
    DATA[msg.id]['duration'] = TimeFormatter(duration)
    DATA[msg.id]['filename'] = file_name
    DATA[msg.id]['filesize'] = filesize
    DATA[msg.id]['caption' ] = media_message.caption
    DATA[msg.id]['mimetype'] = mimetypes.guess_type(path)[0]


    try:
        await msg.edit('<i>Changing Thumbnail and Caption...⏳</i>', enums.ParseMode.HTML)
    except:
        pass

    if typ == 'audio':
        await send_audio(bot, msg, path)
    else:
        data = await db.get_configs(update.from_user.id)
        if data['as_file']:
            await send_document(bot, msg, path)
        else:
            await send_video(bot, msg, path)
        del DATA[msg.id]

    await msg.delete(True)

            
