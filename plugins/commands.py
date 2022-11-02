
import contextlib
import datetime
import logging

from config import Config
from database import db
from database.users import (get_user, is_user_exist, total_users_count,
                            update_user_info)
from helpers import temp
from pyrogram import Client, filters
from pyrogram.types import Message
from translation import *
from utils import (direct_gen_handler, droplink_bypass_handler, extract_link, file_store_handler, get_me_button, get_response, get_size,
                   getHerokuDetails, is_enabled)


logging.getLogger().setLevel(logging.INFO)

avl_web1 = "".join(f"- {i}\n" for i in Config.base_sites)

@Client.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c:Client, m:Message):
    try:
        is_user = await is_user_exist(m.from_user.id)
        if not is_user and Config.LOG_CHANNEL: await c.send_message(Config.LOG_CHANNEL, f"#NewUser\n\nUser ID: `{m.from_user.id}`\nName: {m.from_user.mention}", )
        try:
            new_user = await get_user(m.from_user.id)
        except Exception:
            logging.error("Error creating new user: {0}".format(m.from_user.mention), exc_info=True)
            new_user = await get_user(m.from_user.id)

        if len(m.command) >= 2:
            try:
                _, user_api, site = m.command[1].strip().split('_')
                site = site.replace("dot", ".")
                if site in Config.base_sites:
                    await update_user_info(m.from_user.id, {"shortener_api": user_api})
                    site_index = Config.base_sites.index(site) + 1
                    await update_user_info(m.from_user.id, {f"shortener_api_{site_index}": user_api})
                    await m.reply_text(f"You have successfully connected your {site} API\n\nYour Api: {user_api}\n\n")
                else:
                    await m.reply_text("This website is not available")
            except Exception as e:
                logging.error("Error add user api: {0}".format(m.from_user.mention), exc_info=True)
                await m.reply_text("Something went wrong. Please try again later.")
            return

        t = Config.START_MESSAGE.format(m.from_user.mention, new_user["method"], new_user["base_site"])

        reply_markup = START_MESSAGE_KEYBOARD if Config.KEYBOARD_BUTTON else START_MESSAGE_REPLY_MARKUP
        if Config.WELCOME_IMAGE:
            return await m.reply_photo(photo=Config.WELCOME_IMAGE, caption=t, reply_markup=reply_markup)
        await m.reply_text(t, reply_markup=reply_markup, disable_web_page_preview=True)
    except Exception as e:
        logging.error(e)

@Client.on_message((filters.command('help')| filters.regex("Help")) & filters.private )
async def help_command(c, m: Message):
    s = Config.HELP_MESSAGE.format(
                firstname=temp.FIRST_NAME,
                username=temp.BOT_USERNAME,
                repo=Config.SOURCE_CODE,
                owner="@ask_admin001" )

    if Config.WELCOME_IMAGE:
        return await m.reply_photo(photo=Config.WELCOME_IMAGE, caption=s, reply_markup=HELP_REPLY_MARKUP)
    await m.reply_text(s, reply_markup=HELP_REPLY_MARKUP, disable_web_page_preview=True)

@Client.on_message(filters.command('about') | filters.regex("About"))
async def about_command(c, m: Message):
    reply_markup = None if m.from_user.id not in Config.ADMINS else ABOUT_REPLY_MARKUP
    bot = await c.get_me()
    if Config.WELCOME_IMAGE:
        return await m.reply_photo(photo=Config.WELCOME_IMAGE, caption=Config.ABOUT_TEXT.format(bot.mention(style='md')), reply_markup=reply_markup, disable_web_page_preview=True)
    await m.reply_text(Config.ABOUT_TEXT.format(bot.mention(style='md')),reply_markup=reply_markup , disable_web_page_preview=True)

@Client.on_message((filters.command('method') | filters.regex("Method"))&  filters.private)
async def method_handler(c:Client, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []

    if 2 > len(cmd) >= 0:
        s = Config.METHOD_MESSAGE.format(method=user["method"], shortener=user["base_site"],)
        return await m.reply(s, reply_markup=METHOD_REPLY_MARKUP)
    elif len(cmd) == 2:
        method = cmd[1]
        if method not in ["mdisk", "mdlink", "shortener"]:
            return await m.reply(Config.METHOD_MESSAGE.format(method=user["method"]))
        await update_user_info(user_id, {"method": method })
        await m.reply(f"Method updated successfully to {method}")

@Client.on_message(filters.command('restart') & filters.user(Config.ADMINS) & filters.private)
async def restart_handler(c: Client, m:Message):
    RESTARTE_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Sure', callback_data='restart'), InlineKeyboardButton('Disable', callback_data='delete')]])
    await m.reply("Are you sure you want to restart / re-deploy the server?", reply_markup=RESTARTE_MARKUP)

@Client.on_message(filters.command('direct_download_link') & filters.private)
async def direct_link_gen_cmd_handler(c: Client, m:Message):
    try:
        if Config.DIRECT_GEN and (m.video or m.document or m.audio):
            user = await get_user(m.from_user.id)
            await direct_gen_handler(c, m, user, "direct")
    except Exception as e:
        logging.exception(e, exc_info=True)

@Client.on_message(filters.command('stream_link') & filters.private)
async def stream_link_gen_cmd_handler(c: Client, m:Message):
    try:
        if Config.DIRECT_GEN and (m.video or m.document or m.audio):
            user = await get_user(m.from_user.id)
            await direct_gen_handler(c, m, user, "stream")
    except Exception as e:
        logging.exception(e, exc_info=True)

@Client.on_message(filters.command('file_store_link') & filters.private)
async def file_store_cmd_handler(c: Client, m:Message):
    if Config.FILE_STORE and (m.video or m.document or m.audio):
        user = await get_user(m.from_user.id)
        await file_store_handler(m, user)
        return

@Client.on_message(filters.command('bypass') & filters.private)
async def bypass_cmd_handler(c: Client, m:Message):
    if not Config.LINK_BYPASS and m.from_user.id not in Config.ADMINS:
        await m.reply("Link Bypass has been disabled by the admins")
        return

    if not m.reply_to_message:
        return await m.reply("Reply to link you want to bypass")

    ediatble = await m.reply("`Processing...`", disable_web_page_preview=True, quote=True)
    caption = m.reply_to_message.text.html or m.reply_to_message.caption.html
    bypassed_text = await droplink_bypass_handler(caption)
    await ediatble.edit(bypassed_text, disable_web_page_preview=True)

@Client.on_message(filters.command('stats') & filters.private)
async def stats_handler(c: Client, m:Message):
    if m.from_user.id not in Config.ADMINS:
        return
    txt = await m.reply('`Fetching stats...`')
    size = await db.get_db_size()
    free = 536870912 - size
    size = await get_size(size)
    free = await get_size(free)
    link_stats = await db.get_bot_stats()
    runtime = datetime.datetime.now()

    t = runtime - temp.START_TIME
    runtime = str(datetime.timedelta(seconds=t.seconds))
    total_users = await total_users_count()
    
    msg = f"""
**- Total Users:** `{total_users}`
**- Total Posts:** `{link_stats['posts']}`
**- Total Links:** `{link_stats['links']}`
**- Total Mdisk Links:** `{link_stats['mdisk_links']}`
**- Total Shortener Links:** `{link_stats['shortener_links']}`
**- Used Storage:** `{size}`
**- Total Free Storage:** `{free}`

**- Runtime:** `{runtime}`
"""
    if Config.HEROKU:
        heroku = await getHerokuDetails(Config.HEROKU_API_KEY, Config.HEROKU_APP_NAME)
        msg += f"\n- **Heroku Stats:**\n{heroku}"

    return await txt.edit(msg)

@Client.on_message(filters.command('logs') & filters.private)
async def log_file(bot, message):
    """Send log file"""
    if message.from_user.id not in Config.ADMINS:
        return
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message((filters.command('mdisk_api') | filters.regex("Mdisk API")) & filters.private)
async def mdisk_api_handler(bot, message:Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    cmd = message.command or []

    if 2 > len(cmd) >= 0:
        return await message.reply(Config.MDISK_API_MESSAGE.format(user["mdisk_api"]))

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"mdisk_api": api})
        await message.reply(f"Mdisk API updated successfully to {api}")

@Client.on_message((filters.command('api') | filters.regex("API")) & filters.private )
async def api_handler(bot, m:Message):

    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(site, url=f'https://{site}/member/tools/api')
        ]
        for site in Config.base_sites
    ])

    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []

    if 2 > len(cmd) >= 0:
        s = Config.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"],)
        return await m.reply(s, reply_markup=REPLY_MARKUP)

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply(f"{user['base_site']} API updated successfully to {api}")

@Client.on_message((filters.command('bitly_api') | filters.regex(r"Bitly API")) & filters.private )
async def bitly_api_handler(bot, m:Message):
    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Connect', url='https://bindaaslinks.com/member/tools/api'),

        ],])

    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []

    if 2 > len(cmd) >= 0:
        s = Config.BITLY_API_MESSAGE.format(bitly_api=user["bitly_api"])
        return await m.reply(s,reply_markup=REPLY_MARKUP)

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"bitly_api": api})
        await m.reply(f"Bitly API updated successfully to {api}")

@Client.on_message((filters.command('Header') | filters.regex("Header")) & filters.private )
async def header_handler(bot, m:Message):
    cmd = m.command or []

    if 2 > len(cmd) >= 0:
        return await m.reply(Config.HEADER_MESSAGE)
    user_id = m.from_user.id
    if "remove" in cmd:
        await update_user_info(user_id, {"header_text": ""})
        return await m.reply("Header Text Successfully Removed")
    else:
        header_text = m.text.html.replace("/header", "")
        await update_user_info(user_id, {"header_text": header_text})
        await m.reply("Header Text Updated Successfully")

@Client.on_message((filters.command('footer') | filters.regex("Footer")) & filters.private)
async def footer_handler(bot, m:Message):
    user_id = m.from_user.id
    cmd = m.command or []

    if 2 > len(cmd) >= 0:
        return await m.reply(Config.FOOTER_MESSAGE)
    if "remove" in cmd:
        await update_user_info(user_id, {"footer_text": ""})
        return await m.reply("Footer Text Successfully Removed")
    else:
        footer_text = m.text.html.replace("/footer", "")
        await update_user_info(user_id, {"footer_text": footer_text})
        await m.reply("Footer Text Updated Successfully")

@Client.on_message((filters.command('username') | filters.regex("Username")) & filters.private)
async def username_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []
    if 2 > len(cmd) >= 0:
        username = user["username"] or None
        return await m.reply(Config.USERNAME_TEXT.format(username=username))
    elif len(cmd) == 2:
        if "remove" in cmd:
            await update_user_info(user_id, {"username": ""})
            return await m.reply("Username Successfully Removed")
        else:
            username = cmd[1].strip().replace("@", "")
            await update_user_info(user_id, {"username": username})
            await m.reply(f"Username updated successfully to {username}")

@Client.on_message((filters.command('hashtag') | filters.regex("Hashtag")) & filters.private)
async def hashtag_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []
    if 2 > len(cmd) >= 0:
        hashtag = user["hashtag"] or None
        return await m.reply(Config.HASHTAG_TEXT.format(hashtag=hashtag))
    elif len(cmd) == 2:
        if "remove" in cmd:
            await update_user_info(user_id, {"hashtag": ""})
            return await m.reply("Hashtag Successfully Removed")
        else:
            hashtag = cmd[1].strip().replace("#", "")
            await update_user_info(user_id, {"hashtag": hashtag})
            await m.reply(f"Hashtag updated successfully to {hashtag}")

@Client.on_message((filters.command('channel_link') | filters.regex("Channel Link")) & filters.private)
async def pvt_links_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []
    if 2 > len(cmd) >= 0:
        try:
            pvt_link = user["pvt_link"] or None
        except KeyError:
            pvt_link = None
        return await m.reply(Config.PVT_LINKS_TEXT.format(pvt_link=pvt_link))
    elif len(cmd) == 2:
        if "remove" in cmd:
            await update_user_info(user_id, {"pvt_link": ""})
            return await m.reply("Private Link Successfully Removed")
        else:
            pvt_link = cmd[1].strip()
            await update_user_info(user_id, {"pvt_link": pvt_link})
            await m.reply(f"Private Link updated successfully to {pvt_link}")

@Client.on_message((filters.command('banner_image')|filters.regex("Banner Image")) & filters.private)
async def banner_image_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command or []

    if  2 > len(cmd) >= 0:
        if not m.reply_to_message or not m.reply_to_message.photo:
            return await m.reply_photo(user["banner_image"], caption=Config.BANNER_IMAGE_TEXT) if user["banner_image"] else await m.reply("Current Banner Image URL: None\n" + Config.BANNER_IMAGE_TEXT)
        # Getting the file_id of the photo that was sent to the bot.
        fileid = m.reply_to_message.photo.file_id
        await update_user_info(user_id, {"banner_image": fileid})
        return await m.reply_photo(fileid, caption="Banner Image updated successfully")
    elif len(cmd) == 2:    
        if "remove" in cmd:
            await update_user_info(user_id, {"banner_image": ""})
            return await m.reply("Banner Image Successfully Removed")
        else:
            image_url = cmd[1].strip()
            valid_image_url = await extract_link(image_url)
            if valid_image_url:
                await update_user_info(user_id, {"banner_image": image_url})
                return await m.reply_photo(image_url, caption="Banner Image updated successfully")
            else:
                return await m.reply_text("Image URL is Invalid")

@Client.on_message(filters.command('base_site') & filters.private)
async def base_site_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    site = user['base_site']
    text = f"`/base_site (base_site)`\n\nCurrent base site: {site}\n\nAvailable base sites:\n{avl_web1}"
    return await m.reply(
    text=text,
    disable_web_page_preview=True,
    reply_markup=BASE_SITE_REPLY_MARKUP)

@Client.on_message((filters.command('features')| filters.regex("Features")) & filters.private )
async def features(bot, message: Message):
    await message.reply(Config.FEATURES_MESSAGE.format(message.from_user.first_name))

@Client.on_message((filters.command('site')| filters.regex("Site")) & filters.private )
async def site(bot, message):
    await message.reply(
        f"**Hello, {message.chat.first_name}!**"
      "**\n\n🔹sɪᴛᴇ ɴᴀᴍᴇ : [ʙɪɴᴅᴀᴀs ʟɪɴᴋs](http://bindaaslinks.com) \n\n 📢 ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ : [ᴄʟɪᴄᴋ ʜᴇᴀʀ](http://telegram.me/bindaaslinks) \n\n 💰 ᴘᴜʙʟɪsʜᴇʀ ʀᴀᴛᴇ : [ᴘᴀʏᴏᴜᴛ ʀᴀᴛᴇs](https://bindaaslinks.com/payout-rates) \n\n 🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ : [ᴄʟɪᴄᴋ ʜᴇᴀʀ](https://t.me/BindaasLinksIndia) \n\n 🏦 ᴀʙᴏᴜᴛ.ᴘᴀʏᴍᴇɴᴛs : ᴅᴀʟʏ ᴘᴀʏᴍᴇɴᴛs \n\n ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ 🤗**")

@Client.on_message((filters.command('settings')| filters.regex("Settings")) & filters.private )
async def settings_cmd_handler(bot, m:Message):
    try:
        user_id = m.from_user.id
        user = await get_user(user_id)
        res = Config.USER_ABOUT_MESSAGE.format(base_site=user["base_site"], method=user["method"], shortener_api=user["shortener_api"], mdisk_api=user["mdisk_api"], username=user["username"], header_text=user["header_text"] or None, footer_text=user["footer_text"] or None, banner_image=user["banner_image"], bitly_api=user["bitly_api"],channel_link=user['pvt_link'], hashtag=user['hashtag'])
        buttons = await get_me_button(user)
        reply_markup = InlineKeyboardMarkup(buttons)
        return await m.reply_text(res, reply_markup=reply_markup, disable_web_page_preview=True)
    except Exception as e:
        logging.error(e)

@Client.on_callback_query(filters.command("ban") & filters.private)
async def deny_access_cmd_handler(c:Client,query: Message):
    if query.from_user.id not in Config.ADMINS:
        return
    if Config.IS_PRIVATE and len(query.command) ==2:
        user_id = int(query.command[1])
        await update_user_info(user_id, {"has_access": False})
        await query.reply_text("User has been banned")
        return await c.send_message(user_id, "You have been banned from using this bot")
    else:
        await query.reply_text("Bot is Public")

@Client.on_message((filters.command('account')| filters.regex("Account")) & filters.private)
async def account_cmd_handler(_, message: Message):
    user = await get_user(message.from_user.id)

    if not user["shortener_api"]:
        return await message.reply("Set your /api first")

    url = f"https://{user['base_site']}/stats?api={user['shortener_api']}"
    res = await get_response(url)
    ref_link = f"https://{user['base_site']}/ref/{res['username']}"
    share_url = f"https://telegram.me/share/url?url={ref_link}"
    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Share", url=share_url)
        ]
    ])
    await message.reply(Config.ACCOUNT_CMD_TEXT.format(
        username=res['username'],
        email=res['email'],
        withdrawal_method=res['full_info']['withdrawal_method'],
        withdrawal_account=res['full_info']['withdrawal_account'],
        referral_link=ref_link,
        ),reply_markup=REPLY_MARKUP, disable_web_page_preview=True)

@Client.on_message((filters.command('balance')| filters.regex("Balance")) & filters.private)
async def balance_cmd_handler(_, message: Message):
    user = await get_user(message.from_user.id)

    if not user["shortener_api"]:
        return await message.reply("Set your /api first")

    url = f"https://{user['base_site']}/stats?api={user['shortener_api']}"
    res = await get_response(url)

    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Withdraw", url=f"https://{user['base_site']}/member/withdraws")
        ]
    ])

    await message.reply(Config.BALANCE_CMD_TEXT.format(
        username=res['username'],
        available_balance=res['stats']['available_balance'],
        referral_earnings=res['stats']['referral_earnings'],
        publisher_earnings=res['full_info']['publisher_earnings'],
        ), reply_markup=REPLY_MARKUP, disable_web_page_preview=True)

@Client.on_message(filters.command('addadmin') & filters.private & filters.incoming)
async def addadmin_handler(bot, m: Message):
    try:
        if m.from_user.id != Config.OWNER_ID:
            return await m.reply("Owner command")

        config = await db.get_bot_vars()

        admin_list = config["admins"]
        tdl = ""
        if admin_list:
            for i in admin_list:
                tdl += f"- `{i}`\n"
        else:
            tdl = "None\n"
        if len(m.command) == 1:
            return await m.reply(Config.ADD_ADMIN_TEXT.format(tdl))

        cmd = m.command
        cmd.remove('addadmin')
        if "remove_all" in cmd:
            admin_list_new = []
        elif "remove" in cmd:
            cmd.remove('remove')
            admin_list_cmd = [int(x) for x in "".join(cmd).strip().split(",")] 

            for i in list(admin_list_cmd):
                with contextlib.suppress(Exception):
                    admin_list.remove(i)
            admin_list_new = list(set(list(admin_list)))
        else:
            admin_list_cmd = [int(x) for x in "".join(cmd).strip().split(",")] 
            admin_list_new = list(set(admin_list_cmd + list(admin_list)))

        await db.update_bot_vars({"admins": admin_list_new})
        Config.ADMINS = admin_list_new
        return await m.reply("Updated admin list successfully")
    except Exception as e:
            logging.error(e)
            return await m.reply("Some error updating admin list")


@Client.on_message(filters.command('broadcast_as_copy') & filters.private)
async def broadcast_as_copy_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"broadcast_as_copy": value})
        Config.BROADCAST_AS_COPY = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Broadcast as Copy - {Config.BROADCAST_AS_COPY}\nEx: /broadcast_as_copy True")
    
    
@Client.on_message(filters.command('is_private') & filters.private)
async def is_private_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_private": value})
        Config.IS_PRIVATE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Is Private - {Config.IS_PRIVATE}\nEx: /is_private True")
    
@Client.on_message(filters.command('link_bypass') & filters.private)
async def link_bypass_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"link_bypass": value})
        Config.LINK_BYPASS = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Link Bypass - {Config.LINK_BYPASS}\nEx: /link_bypass True")
    
@Client.on_message(filters.command('base_site') & filters.private)
async def base_site_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"base_site": value})
        Config.BASE_SITE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Base Site - {Config.BASE_SITE}\nEx: /base_site droplink.co")
    
@Client.on_message(filters.command('verified_time') & filters.private)
async def verified_time_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"verified_time": int(value)})
        Config.VERIFIED_TIME = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Verified Time - {Config.VERIFIED_TIME}\nEx: /verified_time 1")
    
@Client.on_message(filters.command('log_channel') & filters.private)
async def log_channel_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"log_channel": int(value)})
        Config.LOG_CHANNEL = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Log Channel - {Config.LOG_CHANNEL}\nEx: /log_channel -100xxx")
    
    
@Client.on_message(filters.command('update_channel') & filters.private)
async def update_channel_cmd_handler(bot, message):

    if message.from_user.id not in Config.ADMINS:
        return

    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"update_channel": int(value)})
        Config.UPDATE_CHANNEL = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Update Channel - {Config.UPDATE_CHANNEL}\nEx: /update_channel -100xxx")
    
    
@Client.on_message(filters.command('keyboard_button') & filters.private)
async def keyboard_button_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"keyboard_button": value})
        Config.KEYBOARD_BUTTON = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Keyboard Button - {Config.KEYBOARD_BUTTON}\nEx: /keyboard_button True")

    
@Client.on_message(filters.command('is_mdisk') & filters.private)
async def is_mdisk_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_mdisk": value})
        Config.IS_MDISK = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Is Mdisk? - {Config.IS_MDISK}\nEx: /is_mdisk True")
    
@Client.on_message(filters.command('is_default_base_site') & filters.private)
async def is_default_base_site_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_default_base_site": value})
        Config.IS_DEFAULT_BASE_SITE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Is Default base site? - {Config.IS_DEFAULT_BASE_SITE}\nEx: /is_default_base_site True")
    
    
@Client.on_message(filters.command('is_bindasslinks') & filters.private)
async def is_bindasslinks_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_bindasslinks": value})
        Config.IS_BINDASSLINKS = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS BINDASSLINKS? - {Config.IS_BINDASSLINKS}\nEx: /is_bindasslinks True")
    
@Client.on_message(filters.command('is_droplink') & filters.private)
async def is_droplink_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_droplink": value})
        Config.IS_DROPLINK = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS DROPLINK? - {Config.IS_DROPLINK}\nEx: /is_droplink True")
      
@Client.on_message(filters.command('is_tnlinks') & filters.private)
async def is_tnlinks_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_tnlinks": value})
        Config.IS_TNLINKS = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS TNLINKS? - {Config.IS_TNLINKS}\nEx: /is_tnlinks True")
    
@Client.on_message(filters.command('is_indianshortener') & filters.private)
async def is_indianshortener_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_indianshortener": value})
        Config.IS_INDIANSHORTENER = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS INDIANSHORTENER? - {Config.IS_INDIANSHORTENER}\nEx: /is_indianshortener True")
    
@Client.on_message(filters.command('is_easysky') & filters.private)
async def is_easysky_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_easysky": value})
        Config.IS_EASYSKY = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS EASYSKY? - {Config.IS_EASYSKY}\nEx: /is_easysky True")
    

@Client.on_message(filters.command('is_earnl_site') & filters.private)
async def is_earnl_site_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_earnl_site": value})
        Config.IS_EARNL_SITE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS EARNL SITE? - {Config.IS_EARNL_SITE}\nEx: /is_earnl_site True")

@Client.on_message(filters.command('is_earnl_xyz') & filters.private)
async def is_earnl_xyz_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_earnl_xyz": value})
        Config.IS_EARNL_XYZ = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS EARNL XYZ? - {Config.IS_EARNL_XYZ}\nEx: /is_earnl_xyz True")


@Client.on_message(filters.command('is_urlearn_xyz') & filters.private)
async def is_urlearn_xyz_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_urlearn_xyz": value})
        Config.IS_URLEARN_XYZ = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS URLEARN XYZ? - {Config.IS_URLEARN_XYZ}\nEx: /is_urlearn_xyz True")

@Client.on_message(filters.command('is_linkshortify') & filters.private)
async def is_linkshortify_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = is_enabled(message.command[1])
        await db.update_bot_vars({"is_linkshortify": value})
        Config.IS_LINKSHORTIFY = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"IS LINKSHORTIFY? - {Config.IS_LINKSHORTIFY}\nEx: /is_linkshortify True")
    

@Client.on_message(filters.command('file_store_db') & filters.private)
async def file_store_db_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"file_store_db": int(value)})
        Config.FILE_STORE_DB = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"file store db - {Config.FILE_STORE_DB}\nEx: /file_store_db -100xx")


@Client.on_message(filters.command('direct_gen_db') & filters.private)
async def direct_gen_db_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"direct_gen_db": int(value)})
        Config.DIRECT_GEN_DB = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"direct gen db - {Config.DIRECT_GEN_DB}\nEx: /direct_gen_db -100xx")

@Client.on_message(filters.command('file_store_bot_username') & filters.private)
async def file_store_bot_username_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"file_store_bot_username": value})
        Config.FILE_STORE_BOT_USERNAME = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"file store bot username - {Config.FILE_STORE_BOT_USERNAME}\nEx: /file_store_bot_username -100xx")

@Client.on_message(filters.command('direct_gen_bot_username') & filters.private)
async def direct_gen_bot_username_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"direct_gen_bot_username": value})
        Config.DIRECT_GEN_BOT_USERNAME = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"direct gen bot username - {Config.DIRECT_GEN_BOT_USERNAME}\nEx: /direct_gen_bot_username -100xx")

@Client.on_message(filters.command('direct_gen_url') & filters.private)
async def direct_gen_url_cmd_handler(bot, message):
    if message.from_user.id not in Config.ADMINS:
        return
    if len(message.command) == 2:
        value = message.command[1]
        await db.update_bot_vars({"direct_gen_url": value})
        Config.DIRECT_GEN_URL = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"direct gen url - {Config.DIRECT_GEN_URL}\nEx: /direct_gen_url -100xx")


@Client.on_message(filters.command('start_message') & filters.private)
async def start_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"start_message": value})
        Config.START_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Start message\n\n`{Config.START_MESSAGE}`\n\nEx: Reply /start_message to the start message")

@Client.on_message(filters.command('help_message') & filters.private)
async def help_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"help_message": value})
        Config.HELP_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Help message\n\n`{Config.HELP_MESSAGE}`\n\nEx: Reply /help_message to the help message")


@Client.on_message(filters.command('about_text') & filters.private)
async def about_text_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"about_message": value})
        Config.ABOUT_TEXT = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"About message\n\n`{Config.ABOUT_TEXT}`\n\nEx: Reply /about_text to the about message")


@Client.on_message(filters.command('method_message') & filters.private)
async def method_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"method_message": value})
        Config.METHOD_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"METHOD message\n\n`{Config.METHOD_MESSAGE}`\n\nEx: Reply /method_message to the method message")


@Client.on_message(filters.command('user_about_message') & filters.private)
async def user_about_message_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"user_about_message": value})
        Config.USER_ABOUT_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"User message\n\n`{Config.USER_ABOUT_MESSAGE}`\n\nEx: Reply /user_about_message to the user_about message")


@Client.on_message(filters.command('mdisk_api_message') & filters.private)
async def mdisk_api_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"mdisk_api_message": value})
        Config.MDISK_API_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"MDISK_API_MESSAGE\n\n`{Config.MDISK_API_MESSAGE}`\n\nEx: Reply /mdisk_api_message to the mdisk_api_message")


@Client.on_message(filters.command('shortener_api_message') & filters.private)
async def shortener_api_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"shortener_api_message": value})
        Config.SHORTENER_API_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"SHORTENER_API_MESSAGE\n\n`{Config.SHORTENER_API_MESSAGE}`\n\nEx: Reply /shortener_api_message to the shortener_api_message")


@Client.on_message(filters.command('username_message') & filters.private)
async def username_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"username_message": value})
        Config.USERNAME_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"Username message\n\n`{Config.USERNAME_MESSAGE}`\n\nEx: Reply /username_message to the username_message")


@Client.on_message(filters.command('hashtag_message') & filters.private)
async def hashtag_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"hashtag_message": value})
        Config.HASHTAG_TEXT = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"HASHTAG TEXT\n\n`{Config.HASHTAG_TEXT}`\n\nEx: Reply /hashtag_message to the HASHTAG TEXT")


@Client.on_message(filters.command('pvt_links_message') & filters.private)
async def pvt_links_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"pvt_links_message": value})
        Config.PVT_LINKS_TEXT = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"pvt links message\n\n`{Config.PVT_LINKS_TEXT}`\n\nEx: Reply /pvt_links_message to the pvt_links_message")


@Client.on_message(filters.command('banner_image_message') & filters.private)
async def banner_image_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"banner_image_message": value})
        Config.BANNER_IMAGE_TEXT = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"banner_image_message\n\n`{Config.BANNER_IMAGE_TEXT}`\n\nEx: Reply /banner_image_message to the message")


@Client.on_message(filters.command('bitly_api_message') & filters.private)
async def bitly_api_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"bitly_api_message": value})
        Config.BITLY_API_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"BITLY_API_MESSAGE\n\n`{Config.BITLY_API_MESSAGE}`\n\nEx: Reply /bitly_api_message to the bitly_api_message")


@Client.on_message(filters.command('features_message') & filters.private)
async def features_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"features_message": value})
        Config.FEATURES_MESSAGE = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"FEATURES_MESSAGE\n\n`{Config.FEATURES_MESSAGE}`\n\nEx: Reply /features_message to the features_message")


@Client.on_message(filters.command('balance_message') & filters.private)
async def balance_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"balance_message": value})
        Config.BALANCE_CMD_TEXT = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"BALANCE_CMD_TEXT\n\n`{Config.BALANCE_CMD_TEXT}`\n\nEx: Reply /balance_message to the balance_message")

@Client.on_message(filters.command('account_message') & filters.private)
async def account_message_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    if message.reply_to_message:
        value = message.reply_to_message.text.html
        await db.update_bot_vars({"account_message": value})
        Config.ACCOUNT_CMD_TEXT = value
        await message.reply("Updated successfully")
    else:
        await message.reply(f"ACCOUNT_CMD_TEXT\n\n`{Config.ACCOUNT_CMD_TEXT}`\n\nEx: Reply /account_message to the account_message")



@Client.on_message(filters.command('admin_cmd') & filters.private)
async def admin_cmd_cmd_handler(bot, message: Message):
    if message.from_user.id not in Config.ADMINS:
        return
    txt = """/addadmin
/log
/stats
/ban
/restart
/is_private
/link_bypass
/base_site
/verified_time
/log_channel
/update_channel
/keyboard_button
/is_mdisk
/is_default_base_site
/is_bindasslinks
/is_droplink
/is_tnlinks
/is_indianshortener
/is_easysky
/is_earnl_site
/is_earnl_xyz
/is_urlearn_xyz
/is_linkshortify
/file_store_db
/direct_gen_db
/file_store_bot_username
/direct_gen_bot_username
/direct_gen_url
/start_message
/help_message
/about_text
/method_message
/user_about_message
/mdisk_api_message
/shortener_api_message
/username_message
/hashtag_message
/pvt_links_message
/banner_image_message
/bitly_api_message
/features_message
/balance_message
/account_message"""

    await message.reply(txt)



