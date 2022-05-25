#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import math
import heroku3 # pylint: disable=import-error
import requests
import asyncio
import time
import shutil
import psutil # pylint: disable=import-error


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from bot import LOGGER, Config
from bot.helpers.utils import humanbytes


logger = LOGGER(__name__)


@Client.on_message(filters.command(["start"]) & filters.user(Config.AUTH_USERS), -1)
async def start (_, update: Message):
    
    await update.reply_text(
        f"Hello {update.from_user.mention}\n\n"
        "I am a renamer bot with permanent thumbnail support.\n\n"
        "Use /settings to change the bot settings.\n\n"
        "For more details check Help",
        True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Help', 'help')]])
    )


@Client.on_message(filters.command(["help"]) & filters.user(Config.AUTH_USERS), -1)
async def help (_, update: Message):
    
    await update.reply_text(
        "<b><u>You need Help ??</u></b> 😅\n\n"
        "✵ First go to the /settings and change the bot behavior as your choice.\n\n"
        "✵ Send me the custom thumbnail to save it permanently. (𝚘𝚙𝚝𝚒𝚘𝚗𝚊𝚕)\n\n"
        "✵ Now send me the file or video which you want to rename.\n\n"
        "✵ After that bot will ask you for the New Name then send the New file name with or without Extention.\n\n"
        "✵ Then be relaxed your file will be uploaded soon..\n\n\n"
        "⚠️ <b>Note:</b> If you want to change bot caption use command /setcaption\n\n",
        True,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('❌ Close', 'close')]])
    )



@Client.on_message(filters.private & filters.command(["status"]) & filters.user(Config.AUTH_USERS), -1)
async def stats(bot, update):

    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(
        time.time() - Config.BOT_START_TIME))
    total, used, free = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    # disk_usage = psutil.disk_usage('/').percent
    # id = update.from_user.id
    # dcid = update.from_user.dc_id
    # username = update.from_user.username
    # name = str(update.from_user.first_name\
    #         + (update.from_user.last_name or ""))
    if Config.HEROKU_API_KEY and Config.HEROKU_APP_NAME:
        server = heroku3.from_key(Config.HEROKU_API_KEY)
        user_agent = (
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/80.0.3987.149 Mobile Safari/537.36'
        )
        accountid = server.account().id
        headers = {
            'User-Agent': user_agent,
            'Authorization': f'Bearer {Config.HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
        }
        path = "/accounts/" + accountid + "/actions/get-quota"
        request = requests.get("https://api.heroku.com" + path, headers=headers)
        if request.status_code == 200:
            result = request.json()
            total_quota = result['account_quota']
            quota_used = result['quota_used']
            quota_left = total_quota - quota_used
            total1 = math.floor(total_quota/3600)
            used1 = math.floor(quota_used/3600)
            hours = math.floor(quota_left/3600)
            minutes = math.floor(quota_left/60 % 60)
            days = math.floor(hours/24)
            usedperc = math.floor(quota_used / total_quota * 100)
            leftperc = math.floor(quota_left / total_quota * 100)

    # f"<code>Total Disk Space: {total}</code>\n" \
    # # f"<code>Used Space: {used} ({disk_usage}%)</code>\n" \
    # # f"<code>Free Space: {free}</code>\n" \
    ms_g = (
        f"<b><u>Bot Status</b></u>\n" 
        f"<code>Uptime: {currentTime}</code>\n"
        f"<code>CPU Usage: {cpu_usage}%</code>\n"
        f"<code>RAM Usage: {ram_usage}%</code>\n\n"
    )

    if Config.HEROKU_API_KEY and Config.HEROKU_APP_NAME:
        ms_g += (
            f"<b><u>Heroku Status</b></u>\n\n" 
            f"<code>Total Dyno Hours: {total1} hrs</code>\n" 
            f"<code>Used This Month: {used1} hrs ({usedperc}%)</code>\n" 
            f"<code>Remaining This Month: {hours} hrs ({leftperc}%)</code>\n" 
            f"<code>Approximate Working Days: {days} days</code>\n"
        )

    msg = await bot.send_message(
        chat_id=update.chat.id,
        text="__Processing...__",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    await msg.edit_text(
        text=ms_g,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.private & filters.command(["restart"]) & filters.user(Config.AUTH_USERS), -1)
async def restart(bot, update):

    if Config.HEROKU_API_KEY and Config.HEROKU_APP_NAME:

        b = await bot.send_message(
            chat_id=update.chat.id,
            text="__Restarting.....__",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await asyncio.sleep(3)
        await b.delete()
        heroku_conn = heroku3.from_key(Config.HEROKU_API_KEY)
        app = heroku_conn.apps()[Config.HEROKU_APP_NAME]
        app.restart()


@Client.on_message(filters.command(['logs']) & filters.user(Config.AUTH_USERS), -1)
async def send_logs(_, m):
    await m.reply_document(
        "logs.txt",
        caption='Logs'
    )
    
