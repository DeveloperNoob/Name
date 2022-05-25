#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import os
import datetime
import time

from pyrogram import (
    Client, 
    StopTransmission,
    utils,
    enums
)
from pyrogram.types import (
    Message
)
from pyrogram.raw import *
from pyrogram.types import InputMediaPhoto
from pyrogram.errors import FilePartMissing

from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from bot.database.database import Database as User
from bot.database.thumbs import Database as Thumb
from bot.plugins import LOGGER
from bot.helpers.progress import Progress
from bot.helpers.ffmpeg_utils import *

logger = LOGGER(__name__)
db = User()
db2 = Thumb()


__all__ = [
    'get_thumb', 'send_document', 
    'send_video', 'send_audio',
    'send_scrnshts'
]


async def get_thumb(user_id: int, bot: Client, video: str = None):

    thumb = await db2.get_thumb(int(user_id))

    if thumb != None:
        download_location = "downloads/" + str(user_id) + ".jpg"
        path = await bot.download_media(thumb, file_name=download_location)
    else:
        if video is None:
            path = None
        else:
            duration = 0
            metadata = extractMetadata(createParser(video))
            if metadata.has("duration"):
                duration = metadata.get("duration")
                duration = duration.seconds if isinstance(duration, datetime.timedelta) else int(duration)
            path = await generate_thumbnail_file(video, os.path.split(video)[0])


    height = 0
    if path is not None:
        metadata = extractMetadata(createParser(path))
        if metadata.has("height"):
            height = metadata.get("height")
        Image.open(path).convert("RGB").save(path)
        img = Image.open(path)
        img.resize((90, height))
        img.save(path, "JPEG")

    return path


async def send_document(bot: Client, update: Message, path: str):

    from bot.plugins import DATA
    thumb_path = await get_thumb(update.from_user.id, bot, path)
    start_time = time.time()
    prog = Progress(update.from_user.id, bot, update)

    data = await db.get_configs(update.from_user.id)
    if DATA.get(update.id, False):
        caption = data['caption_data'] if data['need_caption'] else ''
        if len(caption) > 0:
            caption = caption.format(
                filename = DATA[update.id]['filename'],
                duration = DATA[update.id]['duration'],
                filesize = DATA[update.id]['filesize'],
                mimeType = DATA[update.id]['mimetype'],
                caption = DATA[update.id]['caption'],
            )
    else:
        caption = ''
    del data

    await bot.send_document(
        chat_id=update.chat.id,
        document=path,
        thumb=thumb_path,
        caption=caption,
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_to_message_id=update.id,
        progress=prog.progress_for_pyrogram,
        progress_args=(
            "Uploading Started..!",
            start_time
        )
    )


async def send_video(bot: Client, update: Message, path: str, **kargs):

    from bot.plugins import DATA
    thumb = await get_thumb(update.from_user.id, bot, path)  if kargs.get('thumb', 0) == 0 else kargs.get('thumb')

    start_time = time.time()
    prog = Progress(update.from_user.id, bot, update)

    data = await db.get_configs(update.from_user.id)
    if DATA.get(update.id, False):
        caption = data['caption_data'] if data['need_caption'] else ''
        if caption:
            caption = caption.format(
                filename = DATA[update.id]['filename'],
                duration = DATA[update.id]['duration'],
                filesize = DATA[update.id]['filesize'],
                mimeType = DATA[update.id]['mimetype'],
                caption = DATA[update.id]['caption'],
            )
    else:
        caption = ''

    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(path))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")

    thumb = await bot.save_file(thumb)
    file = await bot.save_file(
        path,
        progress=prog.progress_for_pyrogram,
        progress_args=('Uploading Started', start_time)
    )

    media = types.InputMediaUploadedDocument(
        mime_type="video/mp4",
        file=file,
        thumb=thumb,
        attributes=[
            types.DocumentAttributeVideo(
                supports_streaming=True,
                duration=duration,
                w=width,
                h=height
            ),
            types.DocumentAttributeFilename(
                file_name=os.path.basename(path))
        ]
    )

    try:
        while True:
            try:
                r = await bot.send(
                    functions.messages.SendMedia(
                        peer=await bot.resolve_peer(update.chat.id),
                        media=media,
                        reply_to_msg_id=update.id,
                        random_id=bot.rnd_id(),
                        **await utils.parse_text_entities(bot, caption, enums.ParseMode.MARKDOWN, None)
                    )
                )
            except FilePartMissing as e:
                await bot.save_file(path, file_id=file.id, file_part=e.x)
            else:
                for i in r.updates:
                    if isinstance(i, (types.UpdateNewMessage,
                                      types.UpdateNewChannelMessage,
                                      types.UpdateNewScheduledMessage)):
                        return await Message._parse(
                            bot, i.message,
                            {i.id: i for i in r.users},
                            {i.id: i for i in r.chats},
                            is_scheduled=isinstance(
                                i, types.UpdateNewScheduledMessage)
                        )
    except StopTransmission:
        return None


async def send_audio(bot: Client, update: Message, path: str):

    from bot.plugins import DATA

    thumb_path = await get_thumb(update.from_user.id, bot)
    start_time = time.time()
    prog = Progress(update.from_user.id, bot, update)

    data = await db.get_configs(update.from_user.id)
    if DATA.get(update.id, False):
        caption = data['caption_data'] if data['need_caption'] else ''
        if caption:
            caption = caption.format(
                filename = DATA[update.id]['filename'],
                duration = DATA[update.id]['duration'],
                filesize = DATA[update.id]['filesize'],
                mimeType = DATA[update.id]['mimetype'],
                caption = DATA[update.id]['caption'],
            )
    else:
        caption = ''

    duration = 0
    metadata = extractMetadata(createParser(path))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
    del metadata, data

    await bot.send_audio(
        chat_id=update.chat.id,
        audio=path,
        thumb=thumb_path,
        caption=caption,
        parse_mode=enums.ParseMode.MARKDOWN,
        duration=duration,
        file_name=os.path.basename(path),
        reply_to_message_id=update.id,
        progress=prog.progress_for_pyrogram,
        progress_args=(
            "Uploading Started..!",
            start_time
        )
    )


async def send_scrnshts(bot: Client, update: Message, medias: list):

    await update.reply_media_group(
        medias
    )


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "0s")
    return tmp

