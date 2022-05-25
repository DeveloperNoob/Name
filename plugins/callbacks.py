from bot.config import Config
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters, enums



@Client.on_callback_query(filters.regex(r"^help$"))
async def help_button(bot: Client, update: CallbackQuery):
    
    msg = ("<b><u>You need Help ??</u></b> 😅\n\n"
        "✵ First go to the /settings and change the bot behavior as your choice.\n\n"
        "✵ Send me the custom thumbnail to save it permanently. (𝚘𝚙𝚝𝚒𝚘𝚗𝚊𝚕)\n\n"
        "✵ Now send me the file or video which you want to rename.\n\n"
        "✵ After that bot will ask you for the New Name then send the New file name with or without Extention.\n\n"
        "✵ Then be relaxed your file will be uploaded soon..\n\n\n"
        "⚠️ <b>Note:</b> If you want to change bot caption use command /setcaptions\n\n")

    await bot.edit_message_text(
        text=msg,
        chat_id=update.from_user.id,
        message_id=update.message.id,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('❌ Close', 'close')]])
    )



@Client.on_callback_query(filters.regex(r"^cancel\/\d+\/\d+\/\d+"), 2)
async def cancel_media_transfer(bot: Client, update: CallbackQuery):

    from bot.helpers.progress import cDict
  
    _, chat_id, msg_id, from_user = update.data.split("/")
    chat_id, msg_id, from_user = int(chat_id), int(msg_id), int(from_user)

    if (update.from_user.id == from_user) or (update.from_user.id in Config.AUTH_USERS):
        await update.answer("Cancelling...")
        cDict[chat_id] = []
        cDict[chat_id].append(msg_id)
    else:
        await update.answer("Feck U", True)
        

