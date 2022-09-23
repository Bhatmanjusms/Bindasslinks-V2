from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from config import BANNER_IMAGE, IS_MDISK, USERNAME, base_sites


BATCH_MESSAGE = BATCH = """
This command is used to short or convert links from first to last posts

Make the bot as an admin in your channel

Command usage: `/batch [channel id or username]`

Ex: `/batch -100xxx`
"""

START_MESSAGE = '''🄷🄴🄻🄻🄾, {}
**I'm bindaaslinks.com  Official Bot I Can Convert  Bulk Links To Yours Short Links From Direct Your Bindaaslinks.com Account With Just a Simple Clicks😍\n\n** 
**How To Use 🤔\n ✅1. Got To [https://bit.ly/3cbbgs0](https://bindaaslinks.com/ref/bhatmanjusms) & Complete Your Registration.\n ✅2.Get Your API https://bindaaslinks.com/member/tools/api Copy Your API \n ✅3. Add your api using command /api \n Example : `/Api 0beb1135aac920c1e89856847ef4e8e03e8547a9` \n\n**
** For More Help Press /Help**

**ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛʜᴏᴅ sᴇʟᴇᴄᴛᴇᴅ: {}**
**made with: {}**
'''
START_MESSAGE =  os.environ.get('START_MESSAGE', START_MESSAGE)

HELP_MESSAGE = '''**
Hey! My name is {firstname}. I am a Link Convertor and Shortener Bot, here to make your Work Easy and Help you to Earn more

👇 USEFULL COMMANDS 👇

〽️ Hit 👉 /start To Know More About How To Link bindaaslinks.com Account To This Bot.

🤘 Hit 👉 /features To Know More Features Of This Bot.

💁‍♀️ Hit 👉 /help To Get Help.

🔗 Hit 👉 /Api To Link Your Bindaaslinks Account 

Ⓜ️ Hit 👉 /mdisk_api Link Your Mdisk Account To Converter Others Mdisk Links To Your Mdisklink + Bindaaslinks

🅱 Hit 👉 /bitly_api Link Your Bitly account To Converter Links To Bitly 

⬇️ Hit 👉 /footer To Get Help About Adding your Custom Footer In Your Post

⬆️ Hit 👉 /header To Get Help About Adding Your Custom Header In Your Post

🖼️ Hit 👉 /banner_image To Add Banner In Photo

🔁 Hit 👉 /username To Change Others Username To Your Username

⚙ Hit 👉 /settings To Set settings As per your wish

IF You need More HeLp Then Contact @BindaasLinksIndia ♥️**'''
HELP_MESSAGE =  os.environ.get('HELP_MESSAGE', HELP_MESSAGE)

ABOUT_TEXT = """**
👉Know More:

➲🤖 ʙᴏᴛ ɴᴀᴍᴇ  :  {} 

➲✅ sɪᴛᴇ ɴᴀᴍᴇ : BINDAASLINKS.COM

➲📢 ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ : [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://telegram.me/bindaaslinks)

➲🤑 ᴄᴜʀʀᴇɴᴛ ᴄᴘᴍ : [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://bindaaslinks.com/payout-rates)

➲☎️ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ : [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/BindaasLinksIndia)

➲👨‍💻 ʙᴏᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ : [ᴄʟɪᴄᴋ ʜᴇʀᴇ](http://t.me/CR_0O0)

sᴏ ɴᴏᴡ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ʟɪɴᴋs, ɪ ᴡɪʟʟ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴀɴᴅ ɢɪᴠᴇ ɪᴛ ᴛᴏ ʏᴏᴜ 😊    
**"""
ABOUT_TEXT =  os.environ.get('ABOUT_MESSAGE', ABOUT_TEXT)

is_mdisk = "\n> `mdisk` - Save all the links of the post to your Mdisk account.\n"

METHOD_MESSAGE = """
Current Method: {method}
    
Methods Available:

> `Mdiak+shortner` - Change all the links of the post to your MDisk account first and then short to {shortener} link.

> `shortener` - Short all the links of the post to link directly.
%s
To change method, choose it from the following options:
""" % is_mdisk if IS_MDISK else ''
METHOD_MESSAGE =  os.environ.get('METHOD_MESSAGE', METHOD_MESSAGE)

CUSTOM_ALIAS_MESSAGE = """For custom alias, `[link] | [custom_alias]`, Send in this format

This feature works only in private mode only

Ex: https://t.me/example | Example"""


ADMINS_MESSAGE = """
List of Admins who has access to this Bot

{admin_list}
"""


CHANNELS_LIST_MESSAGE = """
List of channels that have access to this Bot:

{channels}"""


HELP_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Methods', callback_data='method_command'), InlineKeyboardButton('Batch', callback_data='cbatch_command')], [InlineKeyboardButton('Custom Alias', callback_data='alias_conf'), InlineKeyboardButton('Admins', callback_data='admins_list')], [InlineKeyboardButton('Channels', callback_data='channels_list'), InlineKeyboardButton('Home', callback_data='start_command')]])



ABOUT_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Home', callback_data='start_command'), InlineKeyboardButton('Help', callback_data='help_command')], [InlineKeyboardButton('Close', callback_data='delete')]])


START_MESSAGE_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Help', callback_data='help_command'), InlineKeyboardButton('About', callback_data='about_command')], [InlineKeyboardButton('Method', callback_data='method_command'), InlineKeyboardButton('Join Channel♥️', url=f'https://telegram.me/{USERNAME}')], [InlineKeyboardButton('Close', callback_data='delete')]])




if IS_MDISK:
    method_btn = [[InlineKeyboardButton('Mdisk+shortner', callback_data='change_method#mdlink'), InlineKeyboardButton('Shortener', callback_data='change_method#shortener'), InlineKeyboardButton('Mdisk', callback_data='change_method#mdisk')], [InlineKeyboardButton('Back', callback_data='help_command'), InlineKeyboardButton('Close', callback_data='delete')]]



else:
    method_btn = [[InlineKeyboardButton('Mdisk+Shortner', callback_data='change_method#mdlink'), InlineKeyboardButton('Shortener', callback_data='change_method#shortener')], [InlineKeyboardButton('Back', callback_data='help_command'), InlineKeyboardButton('Close', callback_data='delete')]]




METHOD_REPLY_MARKUP = InlineKeyboardMarkup(method_btn)

BACK_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='help_command')]])


BASE_SITE_REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(site, callback_data=f'change_site#{site}')
    ]
    for site in base_sites
])


USER_ABOUT_MESSAGE = """**
- sʜᴏʀᴛᴇɴᴇʀ ᴡᴇʙsɪᴛᴇ: {base_site}

- ᴍᴇᴛʜᴏᴅ: {method}

- {base_site} ᴀᴘɪ: {shortener_api}

- ᴍᴅɪsᴋ ᴀᴘɪ: {mdisk_api}

- ʙɪᴛʟʏ ᴀᴘɪ: {bitly_api}

- ᴜsᴇʀɴᴀᴍᴇ: @{username}

- ʜᴇᴀᴅᴇʀ ᴛᴇxᴛ: 
{header_text}

- ғᴏᴏᴛᴇʀ ᴛᴇxᴛ: 
{footer_text}

- ʙᴀɴɴᴇʀ ɪᴍᴀɢᴇ: {banner_image}
**"""
USER_ABOUT_MESSAGE =  os.environ.get('USER_ABOUT_MESSAGE', USER_ABOUT_MESSAGE)


MDISK_API_MESSAGE = """**To add or update your Mdisk API, \n`/mdisk_api mdisk_api`
            
Ex: `/mdisk_api 6LZq851sXoPHugiKQq`
            
Others Mdisk Links will be automatically changed to the API of this Mdisk account

Current Mdisk API: `{}`**"""
MDISK_API_MESSAGE =  os.environ.get('MDISK_API_MESSAGE', MDISK_API_MESSAGE)

SHORTENER_API_MESSAGE = """**To add or update your Shortner Website API, 
`/shortener_api [api]`
            
Ex: `/api 6LZq851sXofffPHugiKQq`

Current Website: {base_site}

Current Shortener API: `{shortener_api}`**"""
SHORTENER_API_MESSAGE =  os.environ.get('SHORTENER_API_MESSAGE', SHORTENER_API_MESSAGE)

HEADER_MESSAGE = """**Reply to the Header Text You Want

This Text will be added to the top of every message caption or text

Example :- `/Header Join @filmyfunda_movies` 

To Remove Header Text: `/header remove`**"""
HEADER_MESSAGE =  os.environ.get('HEADER_MESSAGE', HEADER_MESSAGE)

FOOTER_MESSAGE = """**Reply to the Footer Text You Want

This Text will be added to the bottom of every message caption or text


Example :- `/Footer Join @filmyfunda_movies` 

To Remove Footer Text: `/footer remove`**"""
FOOTER_MESSAGE =  os.environ.get('FOOTER_MESSAGE', FOOTER_MESSAGE)

USERNAME_TEXT = """"**Current Username: {username}

Usage: `/username your_username`

This username will be automatically replaced with other usernames in the post


Example :- `/username @CR_0O0` 

To remove this username, `/username remove`**"""
USERNAME_TEXT =  os.environ.get('USERNAME_MESSAGE', USERNAME_TEXT)

BANNER_IMAGE = """**Current Banner Image URL: {banner_image}

Usage: `firat send your image after reply that image with /banner_image command`

This image will be automatically replaced with other images in the post

To remove custom image, `/banner_image remove`

Eg: `/banner_image https://www.nicepng.com/png/detail/436-4369539_movie-logo-film.png`**"""
BANNER_IMAGE = os.environ.get('BANNER_IMAGE_MESSAGE', BANNER_IMAGE)

INCLUDE_DOMAIN_TEXT = """**
Use this option if you want to short only links from the following domains list.

Current Include Domain:
{}

Usage: /include_domain domain_name
Ex: /include_domain t.me

To remove a domain, `/include_domain remove domain_name
Ex: /include_domain remove t.me

To remove all domains, `/include_domain remove_all
Ex: /include_domain remove_all
**"""
INCLUDE_DOMAIN_TEXT = os.environ.get('INCLUDE_DOMAIN_MESSAGE', INCLUDE_DOMAIN_TEXT)

EXCLUDE_DOMAIN_TEXT = """**
Use this option if you wish to short every link on your channel but exclude only the links from the following domains list

Current Exclude Domains:
{}

Usage: /exclude_domain domain_name
Ex: /exclude_domain t.me

To remove a domain, `/exclude_domain remove domain_name
Ex: /exclude_domain remove t.me

To remove all domains, `/exclude_domain remove_all
Ex: /exclude_domain remove_all
**"""
INCLUDE_DOMAIN_TEXT = os.environ.get('EXCLUDE_DOMAIN_MESSAGE', EXCLUDE_DOMAIN_TEXT)

BITLY_API_MESSAGE = """**To add or update your Bitly API , 
`/bitly_api [api]`
            
Ex: `/bitly_api 6LZq851sXofffPHugiKQq`

Current API: `{bitly_api}`**"""
BITLY_API_MESSAGE = os.environ.get('BITLY_API_MESSAGE', BITLY_API_MESSAGE)