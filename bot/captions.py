#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG


from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot.plugins import LOGGER
from bot.database.database import Database


logger = LOGGER(__name__)
db = Database()


@Client.on_message(filters.private & filters.command(['caption']), -1)
async def _caption(_: Client, update: Message):
    
    data = await db.get_configs(update.from_user.id)
    caption = data['caption_data']

    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton('Setup Caption', 'setupCaption')],
        [InlineKeyboardButton('❌ Close', 'close')]
    ])

    if caption:
        await update.reply(
            '<b><i>Your Saved Caption:</i></b>\n\n<code>' + caption + '</code>',
            True,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=btns
        )
    else:
        await update.reply(
            'You dont have any saved captions...!\nUse /setcaption to set your caption...!',
            True,
            reply_markup=btns
        )


@Client.on_message(filters.command(["setcaption"]) & filters.private, -1)
async def set_captions(_: Client, update: Message):
    
    user_id = update.from_user.id

    if len(update.command) > 1:
        caption = update.text.split(" ", 1)[1]

    elif update.reply_to_message and hasattr(update.reply_to_message, 'text'):
        caption = update.reply_to_message.text

    else:
        await update.reply(
            '<b><i>Wrong Format... Correct Format: <code>/setcaption text</code></i></b>',
            True,
            parse_mode=enums.ParseMode.HTML
        )
        return


    configs = await db.get_configs(user_id)
    configs["caption_data"] = caption
    await db.update_configs(user_id, configs)
    
    await update.reply(
        text="<b><i>Sucessfully Updated Your Captions ✅</i></b>",
        quote=True,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔰Show Caption🔰', 'showCaption')]])
    )
    del caption, configs



@Client.on_message(filters.command(["delcaption"]) & filters.private, -1)
async def del_captions(_: Client, update: Message):

    user_id = update.from_user.id
    caption = ""
    
    configs = await db.get_configs(user_id)
    configs["caption_data"] = caption
    await db.update_configs(user_id, configs)
    
    await update.reply(
        text="<b><i>Sucessfully Deleted Your Captions ✅</i></b>",
        quote=True,
        parse_mode=enums.ParseMode.HTML
    )
    del caption, configs


@Client.on_callback_query(filters.regex('setupCaption'))
async def showCaptionHelp (_: Client, update: CallbackQuery):
    
    text = (
        "Use <code>/setcaption < your_caption ></code> to set the custom caption for your files.\n\n"
        "<u><b>Examples:</u></b>\n\n"
        "<b>Simple caption:</b> <code>/setcaption My caption</code>\n\n"
        "<b>Dynamic capiton:</b>\n\n"
        "<code>/setcaption 📕 File Name: {filename}\n\n"
        "💾 Size: {filesize}\n\n"
        "⏰ Duration: {duration}</code>\n\n"
        "<b><u>Available Variables:</b></u>\n\n"
        "    • <code>{filename}</code> - replaced by the filename\n"
        "    • <code>{duration}</code> - replaced by the duration of videos\n"
        "    • <code>{filesize}</code> - replaced by filesize\n"
        "    • <code>{mimeType}</code> - replaced by the media mimeType\n"
        "    • <code>{caption}</code> - replaced with the previous file caption\n\n"
    )
    
    await update.edit_message_text(
        text, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('❌ Close', 'close')]])
    )



@Client.on_callback_query(filters.regex('^close$'))
async def close(_: Client, update: CallbackQuery):

    await update.message.delete(True)


@Client.on_callback_query(filters.regex('showCaption'))
async def showCaption(_: Client, update: CallbackQuery):
    

    data = await db.get_configs(update.from_user.id)
    caption = data['caption_data']

    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton('Setup Caption', 'setupCaption')],
        [InlineKeyboardButton('❌ Close', 'close')]
    ])

    if caption:
        await update.edit_message_text(
            '<b><i>Your Saved Caption:</i></b>\n\n<code>' + caption + '</code>',
            parse_mode=enums.ParseMode.HTML,
            reply_markup=btns
        )
    else:
        await update.edit_message_text(
            'You dont have any saved captions...!\nUse /setcaption to set your caption...!',
            reply_markup=btns
        )

