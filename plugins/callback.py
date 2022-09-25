import asyncio
import logging
import os
import re
import sys
from datetime import datetime

from config import ADMINS, IS_PRIVATE, LOG_CHANNEL, SOURCE_CODE, VERIFIED_TIME, base_sites
from database import update_user_info
from database.users import get_user, is_user_verified
from helpers import Helpers, temp
from pyrogram import Client, filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup)
from translation import (ABOUT_REPLY_MARKUP, ABOUT_TEXT, ADMINS_MESSAGE,
                         BACK_REPLY_MARKUP, BATCH_MESSAGE,
                         CHANNELS_LIST_MESSAGE, CUSTOM_ALIAS_MESSAGE,
                         HELP_MESSAGE, HELP_REPLY_MARKUP, METHOD_MESSAGE,
                         METHOD_REPLY_MARKUP, START_MESSAGE,
                         START_MESSAGE_REPLY_MARKUP)
from utils import get_me_button

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex(r"^setgs"))
async def user_setting_cb(c:Client,query: CallbackQuery):
    _, setting, toggle, user_id = query.data.split('#')
    print(toggle)
    myvalues = {setting: toggle == "True"}
    await update_user_info(user_id, myvalues)
    user = await get_user(user_id)
    buttons = await get_me_button(user)
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        await query.message.edit_reply_markup(reply_markup)
        setting = (re.sub(r"is|_", " ", setting)).title()
        toggle = "Enabled" if toggle == "True" else "Disabled"
        await query.answer(f"{setting} {toggle} Successfully", show_alert=True)
    except Exception as e:
        logging.error("Errors occurred while updating user information", exc_info=True)


@Client.on_callback_query(filters.regex(r"^give_access"))
async def give_access_handler(c:Client,query: CallbackQuery):
    try:
        if IS_PRIVATE:
            user_id = int(query.data.split("#")[1])
            user = await get_user(user_id)
            if user["has_access"] and is_user_verified(user_id):
                return query.answer("User already have access", show_alert=True)
            update = await update_user_info(user_id, {"has_access": True, "last_verified":datetime.now()})
            txt = await query.edit_message_text("User has been accepted successfully")
            return await c.send_message(user_id, f"You have been authenticated by Admin. Now you can use this bot for {VERIFIED_TIME} days. Hit /help for more information")
        else:
            query.answer("Bot is Public", show_alert=True)
    except Exception as e:
        logging.exception(e, exc_info=True)

@Client.on_callback_query(filters.regex(r"^deny_access"))
async def deny_access_handler(c:Client,query: CallbackQuery):
    if IS_PRIVATE:
        user_id = int(query.data.split("#")[1])
        user = await get_user(user_id)
        await update_user_info(user_id, {"has_access": False})
        await query.edit_message_text("User has been rejected successfully")
        return await c.send_message(user_id, "Your request has been rejected by Admin to use this bot.")
    else:
        query.answer("Bot is Public", show_alert=True)

@Client.on_callback_query(filters.regex(r"^request_access"))
async def request_access_handler(c:Client,query: CallbackQuery):
    try:
        if IS_PRIVATE:
            user_id = int(query.data.split("#")[1])
            user = await get_user(user_id)
            if user["has_access"] and await is_user_verified(user_id=user_id):
                return await query.message.reply("You already have access to this Bot")
            REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Allow', callback_data=f'give_access#{query.from_user.id}'), InlineKeyboardButton('Deny', callback_data=f'deny_access#{query.from_user.id}'),], [InlineKeyboardButton('Close', callback_data='delete')]])

            await c.send_message(LOG_CHANNEL, f"""
#NewRequest

User ID: {user_id}""", reply_markup=REPLY_MARKUP)
            await query.edit_message_text("Request has been sent to Admin. You will be notified when Admin accepts your request")
        else:
            query.answer("Bot is Public", show_alert=True)
    except Exception as e:
        logging.exception(e, exc_info=True)

@Client.on_callback_query()
async def on_callback_query(bot:Client, query:CallbackQuery):
    user_id = query.from_user.id
    h = Helpers()
    user = await get_user(user_id)
    if query.data == 'delete':
        await query.message.delete()

    elif query.data == 'help_command':
        await query.message.edit(HELP_MESSAGE.format(
            firstname=temp.FIRST_NAME,
            username=temp.BOT_USERNAME,
            repo=SOURCE_CODE,
            owner="@ask_admin001" ), reply_markup=HELP_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'about_command':
        bot = await bot.get_me()
        await query.message.edit(ABOUT_TEXT.format(bot.mention(style='md')), reply_markup=ABOUT_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'start_command':
        new_user = await get_user(query.from_user.id)
        tit = START_MESSAGE.format(query.from_user.mention, new_user["method"], new_user["base_site"])
        await query.message.edit(tit, reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data.startswith('change_method'):
        method_name = query.data.split('#')[1]
        user = temp.BOT_USERNAME
        await update_user_info(user_id, {"method": method_name })
        REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='method_command')]])
        await query.message.edit("Method changed successfully to `{method}`".format(method=method_name, username=user), reply_markup=REPLY_MARKUP)

    elif query.data.startswith('change_site'):
        _, site = query.data.split('#')
        if site in base_sites:
            await update_user_info(user_id, {"base_site": site })
            site_index = base_sites.index(site) + 1
            user = await get_user(user_id)
            if user[f'shortener_api_{site_index}']:
                await update_user_info(user_id, {"shortener_api": user[f'shortener_api_{site_index}']})
                return await query.message.edit("Base Site Updated Sucessfully. Start sending posts",)
            REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton(site, url=f'https://{site}/member/tools/api')]])
            await query.message.edit(f"There is no API found for {site}. Send your api from or Click the below button to connect", reply_markup=REPLY_MARKUP)
        else:
            await query.message.edit("This website is not available")

    elif query.data == 'method_command':
        s = METHOD_MESSAGE.format(method=user["method"], shortener=user["base_site"],)
        return await query.message.edit(s, reply_markup=METHOD_REPLY_MARKUP)

    elif query.data == 'cbatch_command':
        if user_id not in ADMINS:
            return await query.message.edit("Works only for admins", reply_markup=BACK_REPLY_MARKUP)

        await query.message.edit(BATCH_MESSAGE, reply_markup=BACK_REPLY_MARKUP)

    elif query.data == 'alias_conf':
        await query.message.edit(CUSTOM_ALIAS_MESSAGE, reply_markup=BACK_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'admins_list':
        if user_id not in ADMINS:
            return await query.message.edit("Works only for admins", reply_markup=BACK_REPLY_MARKUP)

        await query.message.edit(ADMINS_MESSAGE.format(
            admin_list=await h.get_admins
        ), reply_markup=BACK_REPLY_MARKUP)

    elif query.data == 'channels_list':
        if user_id not in ADMINS:
            return await query.message.edit("Works only for admins", reply_markup=BACK_REPLY_MARKUP)

        await query.message.edit(CHANNELS_LIST_MESSAGE.format(
            channels=await h.get_channels
        ), reply_markup=BACK_REPLY_MARKUP)


    elif query.data == 'restart':
        await query.message.edit('**Restarting.....**')
        await asyncio.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)

    await query.answer()
