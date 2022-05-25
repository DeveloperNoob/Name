#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

from typing import Union
from pyromod import listen
from pyrogram import Client, filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.plugins import LOGGER, User

db = User()
logger = LOGGER(__name__)


@Client.on_message(filters.command(["settings"]), -1)
async def _settings(bot, update):
    await display_settings(bot, update)


@Client.on_callback_query(filters.regex(r'^set\+(?:.+)$'), group=1)
async def settings_cb(bot, update: CallbackQuery):

    _, typ = update.data.split("+")
    user_id = update.from_user.id
    alert_text = "Not supported action."

    await update.answer('')

    settings = await db.get_configs(user_id)
    alert_text = "Successfully changed settings..!"
    data = settings.copy()

    if typ == "upm":
        data["as_file"] = not settings["as_file"]

    elif typ == 'nc':
        data['need_caption'] = not settings['need_caption']

    elif typ == 'ru':
        data['need_updates'] = not settings['need_updates']

    elif typ == 'ssht_ct':
        sshct = settings['need_screenshot']
        if sshct < 10:
            sshct += 2
        elif sshct >= 10:
            sshct = 0
        data['need_screenshot'] = sshct

    elif typ == 'sv':
        sample_duration = settings['need_sample']
        if sample_duration < 180:
            sample_duration += 30
        elif sample_duration >= 180:
            sample_duration = 0
        else:   # Just For handling previous db entries during devlopment
            sample_duration = 0
    
        data['need_sample'] = sample_duration

    await db.update_configs(user_id, data)
    await update.answer(alert_text, show_alert=False)
    await display_settings(bot, update, True)


async def display_settings(bot: Client, update: Union[Message, CallbackQuery], is_cb=False):


    user_id = update.from_user.id

    text = "⚙ Change Bot Settings According To Your Needs..."

    settings = await db.get_configs(user_id)

    upMode = settings['as_file']
    upMode = "Upload As Document 📤" if upMode is True else "Upload As Video 📤"

    needCaptions = settings['need_caption']
    needCaptions = 'Captions: ✅ ON' if needCaptions is True else 'Captions: ❌ OFF'


    buttons = [
        [
            InlineKeyboardButton
            (
                upMode, callback_data="set+upm"
            )
        ],
        [
            InlineKeyboardButton
            (
                needCaptions, callback_data="set+nc"
            )
        ],
    ]


    if is_cb:
        try:
            await update.edit_message_reply_markup(InlineKeyboardMarkup(buttons))
        except Exception as e:
            logger.exception(e, exc_info=True)
        return

    await update.reply(
        text,
        True,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

