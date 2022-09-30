
import datetime
import logging

from config import (ADMINS, BASE_SITE, HEROKU, HEROKU_API_KEY, HEROKU_APP_NAME,
                    INCLUDE_DOMAIN, IS_DEFAULT_BASE_SITE, IS_PRIVATE,
                    LOG_CHANNEL, SOURCE_CODE, WELCOME_IMAGE, base_sites)
from database import db
from database.users import (get_user, is_user_exist, total_users_count,
                            update_user_info)
from helpers import temp
from pyrogram import Client, filters
from pyrogram.types import Message
from translation import *
from utils import (broadcast_admins, extract_link, get_me_button, get_size,
                   getHerokuDetails)


logger = logging.getLogger(__name__)


avl_web1 = "".join(f"- {i}\n" for i in base_sites)

@Client.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c:Client, m:Message):
    try:
        is_user = await is_user_exist(m.from_user.id)
        if not is_user and LOG_CHANNEL: await c.send_message(LOG_CHANNEL, f"#NewUser\n\nUser ID: `{m.from_user.id}`\nName: {m.from_user.mention}", )
        try:
            new_user = await get_user(m.from_user.id)
        except Exception:
            logging.error("Error creating new user: {0}".format(m.from_user.mention), exc_info=True)
            new_user = await get_user(m.from_user.id)

        if len(m.command) >= 2:
            try:
                _, user_api, site = m.command[1].strip().split('_')
                if site in base_sites:
                    await update_user_info((m.from_user.id, {"shortener_api": user_api}))
                    site_index = base_sites.index(site) + 1
                    await update_user_info((m.from_user.id, {f"shortener_api_{site_index}": user_api}))
                    await m.reply_text(f"You have successfully connected your {site} API\n\nYour Api: {user_api}\n\n")

                else:
                    await m.reply_text("This website is not available")
            except Exception as e:
                logging.error("Error add user api: {0}".format(m.from_user.mention), exc_info=True)
                await m.reply_text("Something went wrong. Please try again later.")
            return

        t = START_MESSAGE.format(m.from_user.mention, new_user["method"], new_user["base_site"])

        if WELCOME_IMAGE:
            return await m.reply_photo(photo=WELCOME_IMAGE, caption=t, reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)
        await m.reply_text(t, reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)
    except Exception as e:
        logging.error(e)

@Client.on_message(filters.command('help') & filters.private)
async def help_command(c, m: Message):
    s = HELP_MESSAGE.format(
                firstname=temp.FIRST_NAME,
                username=temp.BOT_USERNAME,
                repo=SOURCE_CODE,
                owner="@ask_admin001" )

    if WELCOME_IMAGE:
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=s, reply_markup=HELP_REPLY_MARKUP)
    await m.reply_text(s, reply_markup=HELP_REPLY_MARKUP, disable_web_page_preview=True)


@Client.on_message(filters.command('about'))
async def about_command(c, m: Message):
    reply_markup = None if m.from_user.id not in ADMINS else ABOUT_REPLY_MARKUP
    bot = await c.get_me()
    if WELCOME_IMAGE:
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=ABOUT_TEXT.format(bot.mention(style='md')), reply_markup=reply_markup, disable_web_page_preview=True)
    await m.reply_text(ABOUT_TEXT.format(bot.mention(style='md')),reply_markup=reply_markup , disable_web_page_preview=True)

@Client.on_message(filters.command('method') &  filters.private)
async def method_handler(c:Client, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = METHOD_MESSAGE.format(method=user["method"], shortener=user["base_site"],)
        return await m.reply(s, reply_markup=METHOD_REPLY_MARKUP)
    elif len(cmd) == 2:
        method = cmd[1]
        if method not in ["mdisk", "mdlink", "shortener"]:
            return await m.reply(METHOD_MESSAGE.format(method=user["method"]))
        await update_user_info(user_id, {"method": method })
        await m.reply(f"Method updated successfully to {method}")

@Client.on_message(filters.command('restart') & filters.user(ADMINS) & filters.private)
async def restart_handler(c: Client, m:Message):
    RESTARTE_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Sure', callback_data='restart'), InlineKeyboardButton('Disable', callback_data='delete')]])
    await m.reply("Are you sure you want to restart / re-deploy the server?", reply_markup=RESTARTE_MARKUP)


@Client.on_message(filters.command('stats') & filters.user(ADMINS) & filters.private)
async def stats_handler(c: Client, m:Message):
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
    if HEROKU:
        heroku = await getHerokuDetails(HEROKU_API_KEY, HEROKU_APP_NAME)
        msg += f"\n- **Heroku Stats:**\n{heroku}"

    return await txt.edit(msg)


@Client.on_message(filters.command('logs') & filters.user(ADMINS) & filters.private)
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('mdisk_api') & filters.private)
async def mdisk_api_handler(bot, message:Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    cmd = message.command

    if len(cmd) == 1:
        return await message.reply(MDISK_API_MESSAGE.format(user["mdisk_api"]))

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"mdisk_api": api})
        await message.reply(f"Mdisk API updated successfully to {api}")



@Client.on_message(filters.command('api') & filters.private )
async def api_handler(bot, m:Message):

    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(site, url=f'https://{site}/member/tools/api')
        ]
        for site in base_sites
    ])

    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"],)
        return await m.reply(s, reply_markup=REPLY_MARKUP)

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply(f"{user['base_site']} API updated successfully to {api}")

@Client.on_message(filters.command('bitly_api') & filters.private )
async def bitly_api_handler(bot, m:Message):
    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Connect', url='https://bindaaslinks.com/member/tools/api'),

        ],])

    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = BITLY_API_MESSAGE.format(bitly_api=user["bitly_api"])
        return await m.reply(s,reply_markup=REPLY_MARKUP)

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"bitly_api": api})
        await m.reply(f"Bitly API updated successfully to {api}")

@Client.on_message(filters.command('header') & filters.private )
async def header_handler(bot, m:Message):
    cmd = m.command

    if len(m.command) == 1:
        return await m.reply(HEADER_MESSAGE)
    user_id = m.from_user.id
    if "remove" in cmd:
        await update_user_info(user_id, {"header_text": ""})
        return await m.reply("Header Text Successfully Removed")
    else:
        header_text = m.text.html.replace("/header", "")
        await update_user_info(user_id, {"header_text": header_text})
        await m.reply("Header Text Updated Successfully")

@Client.on_message(filters.command('footer') & filters.private)
async def footer_handler(bot, m:Message):
    user_id = m.from_user.id
    cmd = m.command

    if len(m.command) == 1:
        return await m.reply(FOOTER_MESSAGE)
    if "remove" in cmd:
        await update_user_info(user_id, {"footer_text": ""})
        return await m.reply("Footer Text Successfully Removed")
    else:
        footer_text = m.text.html.replace("/footer", "")
        await update_user_info(user_id, {"footer_text": footer_text})
        await m.reply("Footer Text Updated Successfully")

@Client.on_message(filters.command('username') & filters.private)
async def username_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    if len(cmd) == 1:
        username = user["username"] or None
        return await m.reply(USERNAME_TEXT.format(username=username))
    elif len(cmd) == 2:
        if "remove" in cmd:
            await update_user_info(user_id, {"username": ""})
            return await m.reply("Username Successfully Removed")
        else:
            username = cmd[1].strip().replace("@", "")
            await update_user_info(user_id, {"username": username})
            await m.reply(f"Username updated successfully to {username}")

@Client.on_message(filters.command('channel_link') & filters.private)
async def pvt_links_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    if len(cmd) == 1:
        try:
            pvt_link = user["pvt_link"] or None
        except KeyError:
            pvt_link = None
        return await m.reply(PVT_LINKS_TEXT.format(pvt_link=pvt_link))
    elif len(cmd) == 2:
        if "remove" in cmd:
            await update_user_info(user_id, {"pvt_link": ""})
            return await m.reply("Private Link Successfully Removed")
        else:
            pvt_link = cmd[1].strip()
            await update_user_info(user_id, {"pvt_link": pvt_link})
            await m.reply(f"Private Link updated successfully to {pvt_link}")

@Client.on_message(filters.command('banner_image') & filters.private)
async def banner_image_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        if not m.reply_to_message or not m.reply_to_message.photo:
            return await m.reply_photo(user["banner_image"], caption=BANNER_IMAGE) if user["banner_image"] else await m.reply("Current Banner Image URL: None\n" + BANNER_IMAGE)

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

@Client.on_message(filters.command('features') & filters.private )
async def features(bot, message):
    await message.reply(
        f"**Hello, {message.chat.first_name}!**\n\n"
      "**💠 Features Of LinkShortify Robot 💠\n\n❤️ It's A User Friendly Bot ❤️\n\n➡️ Use Can Short Bulk Links Into Your LinkShortify Account With This Bot\n\n➡️ You Can Also Short Links With Custom Alias\n\n➡️ You Can Also Use Mdisk Links To Short It Into Your Mdisk Account And Then LinkShortify Account\n\n➡️ You Can Set Custom Header\n\n➡️ You Can Set Custom Footer\n\n➡️ You Can Set Custom Banner Image\n\n➡️ You Can Chage Telegram Username & Channel Link To Yours\n\n➡️ You Can Use Bitly To Short LinkShortify Link\n\n➡️ You Can Chose Different Link Short Methods\n\n➡️ You Can Use Settings Section To Manage All Things At One Place\n\n➡️ You Can Send File To Bot And Bot Will Give You Different LinkShortify Links & It Will Be Usable To Download File Directly, Streaming It Online & Download File From File To Link Bot\n\n➡️ You Can Change Other LinkShortify Links To Your LinkShortify Account Links\n\n⚠️ If You Need More Help Then Message Us At @BrixFlySupport**")     

@Client.on_message(filters.command('site') & filters.private )
async def site(bot, message):
    await message.reply(
        f"**Hello, {message.chat.first_name}!**"
      "**\n\n🔹sɪᴛᴇ ɴᴀᴍᴇ : [ʙɪɴᴅᴀᴀs ʟɪɴᴋs](http://bindaaslinks.com) \n\n 📢 ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ : [ᴄʟɪᴄᴋ ʜᴇᴀʀ](http://telegram.me/bindaaslinks) \n\n 💰 ᴘᴜʙʟɪsʜᴇʀ ʀᴀᴛᴇ : [ᴘᴀʏᴏᴜᴛ ʀᴀᴛᴇs](https://bindaaslinks.com/payout-rates) \n\n 🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ : [ᴄʟɪᴄᴋ ʜᴇᴀʀ](https://t.me/BindaasLinksIndia) \n\n 🏦 ᴀʙᴏᴜᴛ.ᴘᴀʏᴍᴇɴᴛs : ᴅᴀʟʏ ᴘᴀʏᴍᴇɴᴛs \n\n ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ 🤗**")

@Client.on_message(filters.command('settings') & filters.private )
async def settings_cmd_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)

    user_id = m.from_user.id
    user = await get_user(user_id)
    res = USER_ABOUT_MESSAGE.format(base_site=user["base_site"], method=user["method"], shortener_api=user["shortener_api"], mdisk_api=user["mdisk_api"], username=user["username"], header_text=user["header_text"] or None, footer_text=user["footer_text"] or None, banner_image=user["banner_image"], bitly_api=user["bitly_api"],channel_link=user['pvt_link'])

    buttons = await get_me_button(user)
    reply_markup = InlineKeyboardMarkup(buttons)
    return await m.reply_text(res, reply_markup=reply_markup, disable_web_page_preview=True)


#  Todo
@Client.on_message(filters.command('include_domain') & filters.private )
async def include_domain_handler(bot, m:Message):
    user = get_user(m.from_user.id)
    inc_domain = user["include_domain"]

    tdl = "".join(f"- {i}\n" for i in inc_domain)

    if len(m.command) <= 1:
        return m.reply(INCLUDE_DOMAIN_TEXT.format(tdl))

@Client.on_message(filters.command('exclude_domain') & filters.private)
async def exclude_domain_handler(bot, m:Message):
    user = get_user(m.from_user.id)
    ex_domain = user["exclude_domain"]
    tdl = "".join(f"- {i}\n" for i in ex_domain)
    if len(m.command) <= 1:
        return m.reply(EXCLUDE_DOMAIN_TEXT.format(tdl))

@Client.on_callback_query(filters.command("ban") & filters.private & filters.user(ADMINS))
async def deny_access_cmd_handler(c:Client,query: Message):
    if IS_PRIVATE and len(query.command) ==2:
        user_id = int(query.command[1])
        user = await get_user(user_id)
        await update_user_info(user_id, {"has_access": False})
        await query.reply_text("User has been banned")
        return await c.send_message(user_id, "You have been banned from using this bot")
    else:
        await query.reply_text("Bot is Public")


