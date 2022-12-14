from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import Config


Config.BATCH_MESSAGE = BATCH = """
This command is used to short or convert links from first to last posts

Make the bot as an admin in your channel

Command usage: `/batch [channel id or username]`

Ex: `/batch -100xxx`
"""

Config.START_MESSAGE = '''π·π΄π»π»πΎ, {}
**I'm bindaaslinks.com  Official Bot I Can Convert  Bulk Links To Yours Short Links From Direct Your Bindaaslinks.com Account With Just a Simple Clicksπ\n\n** 
**How To Use π€\n β1. Got To [https://bit.ly/3cbbgs0](https://bindaaslinks.com/ref/bhatmanjusms) & Complete Your Registration.\n β2.Get Your API https://bindaaslinks.com/member/tools/api Copy Your API \n β3. Add your api using command /api \n Example : `/Api 0beb1135aac920c1e89856847ef4e8e03e8547a9` \n\n**
** For More Help Press /Help**

**α΄α΄ΚΚα΄Ι΄α΄ α΄α΄α΄Κα΄α΄ sα΄Κα΄α΄α΄α΄α΄: {}**
**made with: {}**
'''


Config.HELP_MESSAGE = '''**
Hey! My name is {firstname}. I am a Link Convertor and Shortener Bot, here to make your Work Easy and Help you to Earn more

π USEFULL COMMANDS π

γ½οΈ Hit π /start To Know More About How To Link bindaaslinks.com Account To This Bot.

π€ Hit π /features To Know More Features Of This Bot.

πββοΈ Hit π /help To Get Help.

π Hit π /Api To Link Your Bindaaslinks Account 

βοΈ Hit π /mdisk_api Link Your Mdisk Account To Converter Others Mdisk Links To Your Mdisklink + Bindaaslinks

π± Hit π /bitly_api Link Your Bitly account To Converter Links To Bitly 

β¬οΈ Hit π /footer To Get Help About Adding your Custom Footer In Your Post

β¬οΈ Hit π /header To Get Help About Adding Your Custom Header In Your Post

πΌοΈ Hit π /banner_image To Add Banner In Photo

π Hit π /username To Change Others Username To Your Username

β Hit π /settings To Set settings As per your wish

IF You need More HeLp Then Contact @BindaasLinksIndia β₯οΈ**'''


Config.ABOUT_TEXT = """**πKnow More: 

β²π€ Κα΄α΄ Ι΄α΄α΄α΄  :  {} 

β²β sΙͺα΄α΄ Ι΄α΄α΄α΄ : Earnl.site

β²π’ α΄??Ιͺα΄Ιͺα΄Κ α΄Κα΄Ι΄Ι΄α΄Κ : [α΄ΚΙͺα΄α΄ Κα΄Κα΄](https://telegram.me/EarnlWeb)

β²π€ α΄α΄ΚΚα΄Ι΄α΄ α΄α΄α΄ : [α΄ΚΙͺα΄α΄ Κα΄Κα΄](https://earnl.site/payout-rates)

β²βοΈ α΄α΄Ι΄α΄α΄α΄α΄ sα΄α΄α΄α΄Κα΄ : [α΄ΚΙͺα΄α΄ Κα΄Κα΄](https://t.me/earnl_admin)

β²π¨βπ» Κα΄α΄ α΄α΄α΄ α΄Κα΄α΄α΄Κ : [α΄ΚΙͺα΄α΄ Κα΄Κα΄](http://t.me/CR_0O0)

sα΄ Ι΄α΄α΄‘ sα΄Ι΄α΄ α΄α΄ α΄Κα΄ ΚΙͺΙ΄α΄s, Ιͺ α΄‘ΙͺΚΚ α΄α΄Ι΄α΄ α΄Κα΄ Ιͺα΄ α΄Ι΄α΄ Ι’Ιͺα΄ α΄ Ιͺα΄ α΄α΄ Κα΄α΄ π  Ιͺ? Κα΄α΄ Ι΄α΄α΄α΄ sα΄α΄α΄ Κα΄α΄ α΄α΄ Κα΄α΄'Κα΄ sΚα΄Κα΄Ι΄α΄Κ α΄Κα΄Ι΄ α΄α΄Ι΄α΄α΄α΄α΄ @CR_0O0
**"""

is_mdisk = "\n> `mdisk` - Save all the links of the post to your Mdisk account.\n"

Config.METHOD_MESSAGE = """
Current Method: {method}
                
Methods Available:

> `Mdiak+shortner` - Change all the links of the post to your MDisk account first and then short to {shortener} link.

> `shortener` - Short all the links of the post to link directly.
%s
To change method, choose it from the following options:
            """ % is_mdisk if Config.IS_MDISK else ''


Config.CUSTOM_ALIAS_MESSAGE = """For custom alias, `[link] | [custom_alias]`, Send in this format

This feature works only in private mode only

Ex: https://t.me/example | Example"""


Config.ADMINS_MESSAGE = """
List of Admins who has access to this Bot

{admin_list}
"""


Config.CHANNELS_LIST_MESSAGE = """
List of channels that have access to this Bot:

{channels}"""


HELP_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Methods', callback_data='method_command'), InlineKeyboardButton('Batch', callback_data='cbatch_command')], [InlineKeyboardButton('Custom Alias', callback_data='alias_conf'), InlineKeyboardButton('Admins', callback_data='admins_list')], [InlineKeyboardButton('Channels', callback_data='channels_list'), InlineKeyboardButton('Home', callback_data='start_command')]])



ABOUT_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Home', callback_data='start_command'), InlineKeyboardButton('Help', callback_data='help_command')], [InlineKeyboardButton('Close', callback_data='delete')]])

START_MESSAGE_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Help', callback_data='help_command'), InlineKeyboardButton('About', callback_data='about_command')], [InlineKeyboardButton('Method', callback_data='method_command'), InlineKeyboardButton('Join Channelβ₯οΈ', url=f'https://telegram.me/{Config.USERNAME}')], [InlineKeyboardButton('Close', callback_data='delete')]])

START_MESSAGE_KEYBOARD = ReplyKeyboardMarkup([ 
    [KeyboardButton(text="βΆοΈ Start")], 
    [KeyboardButton(text="π Help"), KeyboardButton(text="π About"), KeyboardButton(text="π‘ Features")],
    [KeyboardButton(text="βοΈ Mdisk API"), KeyboardButton(text="π API"), KeyboardButton(text="π± Bitly API")],
    [KeyboardButton(text="π Method"), KeyboardButton(text="βοΈ Settings"), KeyboardButton(text="πͺͺ Account")],
    [KeyboardButton(text="π° Balance")],
    [KeyboardButton(text="β¬οΈ Header"), KeyboardButton(text="β¬οΈ Footer")],
    [KeyboardButton(text="π· Username"), KeyboardButton(text="π Hashtag")],
    [KeyboardButton(text="β Channel Link"), KeyboardButton(text="π Banner Image")],
    [KeyboardButton(text="π File Store Link"), KeyboardButton(text="π‘ Stream Link")],
    [KeyboardButton(text="π₯ Direct Download Link"), KeyboardButton(text="π Bypass")],
    ])


BACK_REPLY_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='help_command')]])


BASE_SITE_REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(site, callback_data=f'change_site#{site}')
    ]
    for site in Config.base_sites
])


Config.USER_ABOUT_MESSAGE = """**
- sΚα΄Κα΄α΄Ι΄α΄Κ α΄‘α΄ΚsΙͺα΄α΄: {base_site}

- α΄α΄α΄Κα΄α΄: {method}

- {base_site} α΄α΄Ιͺ: {shortener_api}

- α΄α΄Ιͺsα΄ α΄α΄Ιͺ: {mdisk_api}

- ΚΙͺα΄ΚΚ α΄α΄Ιͺ: {bitly_api}

- α΄sα΄ΚΙ΄α΄α΄α΄: @{username}

- Channel link: {channel_link}

- Κα΄α΄α΄α΄Κ α΄α΄xα΄: 
{header_text}

- ?α΄α΄α΄α΄Κ α΄α΄xα΄: 
{footer_text}

- Κα΄Ι΄Ι΄α΄Κ Ιͺα΄α΄Ι’α΄: {banner_image}

- Hashtag: {hashtag}
**"""


Config.MDISK_API_MESSAGE = """**To add or update your Mdisk API, \n`/mdisk_api mdisk_api`
            
Ex: `/mdisk_api 6LZq851sXoPHugiKQq`
            
Others Mdisk Links will be automatically changed to the API of this Mdisk account

Current Mdisk API: `{}`**"""


Config.SHORTENER_API_MESSAGE = """**To add or update your Shortner Website API, 
`/shortener_api [api]`
            
Ex: `/api 6LZq851sXofffPHugiKQq`

Current Website: {base_site}

Current Shortener API: `{shortener_api}`**"""


Config.HEADER_MESSAGE = """**Reply to the Header Text You Want

This Text will be added to the top of every message caption or text

Example :- `/Header Join @filmyfunda_movies` 

To Remove Header Text: `/header remove`**"""


Config.FOOTER_MESSAGE = """**Reply to the Footer Text You Want

This Text will be added to the bottom of every message caption or text


Example :- `/Footer Join @filmyfunda_movies` 

To Remove Footer Text: `/footer remove`**"""


Config.USERNAME_TEXT = """"**Current Username: {username}

Usage: `/username your_username`

This username will be automatically replaced with other usernames in the post


Example :- `/username @CR_0O0` 

To remove this username, `/username remove`**"""


Config.HASHTAG_TEXT = """**Current Hashtag: {hashtag}

Usage: `/hashtag your_hashtag`

This hashtag will be automatically replaced with other hashtags in the post

Example :- `/hashtag instagramdown` 

To remove this hashtag, `/hashtag remove`**"""



Config.PVT_LINKS_TEXT = """**Current Channel Links: {pvt_link}

Usage: `/channel_link https://t.me/+riua0Y3YXHo4NjY1`

This Channel Link will be automatically replaced with other private links in the post

Example :- `/channel_link https://t.me/+riua0Y3YXHo4NjY1` 

To remove this Channel Link, `/channel_link remove`**"""


Config.BANNER_IMAGE_TEXT = """**Current Banner Image URL: {banner_image}

Usage: `firat send your image after reply that image with /banner_image command`

This image will be automatically replaced with other images in the post

To remove custom image, `/banner_image remove`

Eg: `/banner_image https://www.nicepng.com/png/detail/436-4369539_movie-logo-film.png`**"""


Config.INCLUDE_DOMAIN_TEXT = """**
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


Config.EXCLUDE_DOMAIN_TEXT = """**
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


Config.BITLY_API_MESSAGE = """**To add or update your Bitly API , 
`/bitly_api [api]`
            
Ex: `/bitly_api 6LZq851sXofffPHugiKQq`

Current API: `{bitly_api}`**"""

Config.FEATURES_MESSAGE = "**Hello, {first_name}!**\n\n**π  Features Of Link Shortner Bot π \n\nβ€οΈ It's A User Friendly Bot β€οΈ\n\nβ‘οΈ Use Can Short Bulk Links Into Your Shortner Account With This Bot\n\nβ‘οΈ You Can Also Short Links With Custom Alias\n\nβ‘οΈ You Can Also Use Mdisk Links To Short It Into Your Mdisk Account And Then Shortner Account\n\nβ‘οΈ You Can Set Custom Header\n\nβ‘οΈ You Can Set Custom Footer\n\nβ‘οΈ You Can Set Custom Banner Image\n\nβ‘οΈ You Can Chage Telegram Username\n\nβ‘οΈ You Can replace others channel links to your channel link\n\nβ‘οΈ You Can Use Bitly To Short shortner Link\n\nβ‘οΈ You Can Chose Different Link Short Methods\n\nβ‘οΈ You Can Use Settings Section To Manage All Things At One Place\n\nβ‘οΈ You Can Send File To Bot And Bot Will Give You Different shortner Links & It Will Be Usable To Download File Directly, Streaming It Online & Download File From File To Link Bot\n\nβ‘οΈ You Can Change Other Shortner Links To Your Shortner Account Links\n\nβ‘οΈ Bot can also short hidden links and hyperlinks\n\nβ‘οΈ Bot can short button links also\n\nβ οΈ if you need same bot to your shortner site then contact me @CR_0O0 β‘οΈ**"  


Config.BALANCE_CMD_TEXT = """
π° Account Username : {username} 

β‘οΈ Publisher Earnings : {publisher_earnings}
β‘οΈ Referral Earning : {referral_earnings}

β Available Balance : {available_balance}

ππ»Click Hear To Withdraw Your Earnings ππ»"""


Config.ACCOUNT_CMD_TEXT = """
π° Username : {username} 
π§ Email Address : {email} 

π  Withdrawal Method : {withdrawal_method} 
β‘οΈ Withdrawal Account : {withdrawal_account}

π Referral Link : {referral_link}

π Click Here To Share Your Referral Link π"""

Config.ADD_ADMIN_TEXT = """Current Admins:
{}
Usage: /addadmin id
Ex: `/addadmin 14035272, 14035272`
To remove a admin,
Ex: `/addadmin remove 14035272`
To remove all admins,
Ex: `/addadmin remove_all`
"""
