from config import Config
from pyrogram import Client, filters
from database.users import get_user
from utils import broadcast_admins, main_convertor_handler, update_stats, user_api_check
from database import db
from helpers import temp
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
from config import Config
from database.users import get_user, is_user_verified, update_user_info
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from utils import (extract_link, main_convertor_handler, update_stats,
                   user_api_check)

# Channel
@Client.on_message(filters.private & filters.incoming)
async def private_link_handler(c:Client, message:Message):
    user = await get_user(message.from_user.id)

    try:
        user['is_pvt_link']
    except KeyError:
        await update_user_info(message.from_user.id, {"pvt_link":None, "is_pvt_link":False})

    try:
        if message.text:
            has_link = len(await extract_link(message.text))
            if message.text.startswith('/'):return
            elif len(message.text.strip()) == 20 and has_link <=0 and not message.reply_markup:
                api = message.text
                await update_user_info(message.from_user.id, {"mdisk_api": api})
                return await message.reply(f"Mdisk API updated successfully to {api}")

            elif len(message.text.strip()) == 40 and has_link <=0 and not message.reply_markup:
                api = message.text
                await update_user_info(message.from_user.id, {"shortener_api": api})
                site_index = Config.base_sites.index(user['base_site']) + 1
                await update_user_info(message.from_user.id, {f'shortener_api_{site_index}': api})
                return await message.reply(f"Shortener API updated successfully to {api}")

        # User Verification
        has_access = (await get_user(message.from_user.id))["has_access"]

        REPLY_MARKUP = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Request Access', callback_data=f'request_access#{message.from_user.id}'),
            ],

        ])
        if message.from_user.id not in Config.ADMINS and Config.IS_PRIVATE and not has_access:
            return await message.reply_text("This bot works only for authorized users. Request admin to use this bot", reply_markup=REPLY_MARKUP, disable_web_page_preview=True)


        is_verified = await is_user_verified(message.from_user.id)

        if not is_verified and has_access:
            REPLY_MARKUP = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Request Access', callback_data=f'request_access#{message.from_user.id}'),
            ],

        ])
            return message.reply_text(f"Your Verification time has expired. Request admin to use this bot" ,reply_markup=REPLY_MARKUP ,disable_web_page_preview=True)

        user_method = user["method"]

        vld = await user_api_check(user)

        if vld is not True: return await message.reply_text(vld)

        try:
            txt = await message.reply('`🔗 Cooking Your Links So Please Wait . . . `', quote=True)
            await main_convertor_handler(message, user_method, user=user)

            if message.caption:
                await update_stats(message, user_method)

        except Exception as e:
            await message.reply(f"Error while trying to convert links {e}:", quote=True)
            logger.exception(e, exc_info=True)
        finally:
            await txt.delete()

    except Exception as e:
        logger.exception(e, exc_info=True)

@Client.on_message(~filters.forwarded & filters.chat(Config.CHANNEL_ID) & (filters.channel | filters.group) & filters.incoming & ~filters.private & ~filters.forwarded)
async def channel_link_handler(c:Client, message):
    
    user = await get_user(message.from_user.id)
    user_method = user["method"]

    vld = await user_api_check(user)

    if vld is not True and Config.CHANNELS: return await broadcast_admins(c, "To use me in channel...\n\n" + vld )

    if Config.CHANNELS:
        try:
            await main_convertor_handler(message, user_method, True)
            # Updating DB stats
            await update_stats(message, user_method)

        except Exception as e:
            logger.error(e)