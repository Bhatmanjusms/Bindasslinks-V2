import asyncio
import base64
import random
import re
import json
import time
import aiohttp
import contextlib
import heroku3
from pyrogram import Client
from database import db
import requests
from pyrogram.raw.types.messages import Messages
from shortzy import Shortzy
from mdisky import Mdisk
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pyrogram.errors import FloodWait
from config import *
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyshorteners
from pyrogram.types import InputMediaPhoto
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
import logging
from urllib.parse import quote_plus
from database.users import update_user_info

from helpers import temp
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def main_convertor_handler(message:Message, type:str, edit_caption:bool=False, user=None):
    username = USERNAME
    header_text = HEADER_TEXT
    footer_text = FOOTER_TEXT
    banner_image = BANNER_IMAGE

    if user:
        header_text = user["header_text"] if user["is_header_text"] else ""
        footer_text = user["footer_text"] if user["is_footer_text"] else ""
        username = user["username"] if user["is_username"] else None
        banner_image = user["banner_image"] if user["is_banner_image"] else None
        pvt_link = user["pvt_link"] if user["is_pvt_link"] else None

    caption = None

    if message.text:
        caption = message.text.html
    elif message.caption:
        caption = message.caption.html
    
    # Checking if the message has any link or not. If it doesn't have any link, it will return.
    if (caption and len(await extract_link(caption)) <=0 and not message.reply_markup) or not caption:
        return

    user_method = type

    # Checking if the user has set his method or not. If not, it will reply with a message.
    if user_method is None:
        return await message.reply(text="Set your /method first")

    # Bypass Links
    caption = await droplink_bypass_handler(caption)

    # A dictionary which contains the methods to be called.
    METHODS = {
        "mdisk": mdisk_api_handler,
        "shortener": replace_link,
        "mdlink": mdisk_droplink_convertor
    }

    # Replacing the username with your username.
    caption = await replace_username(caption, username)

    # Replacing the private links with your links.
    if pvt_link: caption = await replace_username(caption, pvt_link, is_pvt_links=True)

    # Getting the function for the user's method
    method_func = METHODS[user_method] 

    # converting urls
    shortenedText = await method_func(user, caption)

    # converting reply_markup urls
    reply_markup = await reply_markup_handler(message, method_func)

    try:
        shortenedText = await bitly_short_handler(shortenedText, user) if user["is_bitly_link"] and user["bitly_api"] else shortenedText
    except Exception as e:
        logging.error(e)

    # Adding header and footer
    shortenedText = f"{header_text}\n{shortenedText}\n{footer_text}"

    # Used to get the file_id of the media. If the media is a photo and BANNER_IMAGE is set, it will
    # replace the file_id with the BANNER_IMAGE.
    if message.media:
        medias = getattr(message, message.media.value)
        fileid = medias.file_id
        if message.photo and banner_image:
            fileid = banner_image
            if edit_caption:
                fileid = InputMediaPhoto(banner_image, caption=shortenedText)


    if message.text:
        if user_method in {"shortener", "mdlink"} and '|' in caption:
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))\s\|\s([a-zA-Z0-9_]){,30}"
            if custom_alias := re.match(regex, caption):
                custom_alias = custom_alias[0].split('|')
                alias = custom_alias[1].strip()
                url = custom_alias[0].strip()
                shortenedText = await method_func(url, alias)

        if edit_caption:
            return await message.edit(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup)

        return await message.reply(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup, quote=True)

    elif message.media:

        if edit_caption:
            if BANNER_IMAGE and message.photo:
                return await message.edit_media(media=fileid)

            return await message.edit_caption(shortenedText, reply_markup=reply_markup)

        if message.document:
            return await message.reply_document(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True)

        elif message.photo:
            return await message.reply_photo(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True)

        elif message.video:
            return await message.reply_video(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True)
            
# Reply markup 
async def reply_markup_handler(message:Message, method_func):
    if message.reply_markup:
        reply_markup = json.loads(str(message.reply_markup))
        buttsons = []
        for markup in reply_markup["inline_keyboard"]:
            buttons = []
            for j in markup:
                text = j["text"]
                url = j["url"]
                url = await method_func(url)
                button = InlineKeyboardButton(text, url=url)
                buttons.append(button)
            buttsons.append(buttons)
        reply_markup = InlineKeyboardMarkup(buttsons)
        return reply_markup


async def mdisk_api_handler(user, text):
    api_key = user["mdisk_api"] if user else MDISK_API
    mdisk = Mdisk(api_key)
    return await mdisk.convert_from_text(text)

async def replace_link(user, text, x=""):
    api_key = user["shortener_api"]
    base_site = user["base_site"]
    shortzy = Shortzy(api_key, base_site)
    links = await extract_link(text)
    is_pvt_link = bool(user['is_pvt_link'] and user['pvt_link'])
    for link in links:
        if ("t.me" not in link and not is_pvt_link) or ("t.me" in link and not is_pvt_link):
            long_url = link
            logging.info(f"Contverting {long_url}")
            if user["include_domain"]:
                include = user["include_domain"]
                domain = [domain.strip() for domain in include]
                if any(i in link for i in domain):
                    try:
                        short_link = await shortzy.convert(link, x)
                    except Exception:
                        short_link = await tiny_url_main(await shortzy.get_quick_link(link))
                    text = text.replace(long_url, short_link)
            elif user["exclude_domain"]:
                exclude = user["include_domain"]
                domain = [domain.strip() for domain in exclude]
                if all(i not in link for i in domain):
                    try:
                        short_link = await shortzy.convert(link, x)
                    except Exception:
                        short_link = await tiny_url_main(await shortzy.get_quick_link(link))
                    text = text.replace(long_url, short_link)
            else:
                try:
                    short_link = await shortzy.convert(link, x)
                except Exception as e:
                    logging.exception(e)
                    short_link = await tiny_url_main(await shortzy.get_quick_link(link))
                text = text.replace(long_url, short_link)
    return text

####################  Mdisk and Droplink  ####################
async def mdisk_droplink_convertor(user, text, alias=""):
    links = await mdisk_api_handler(user, text)
    links = await replace_link(user, links, x=alias)
    return links

####################  Replace Username  ####################
async def replace_username(text, username, is_pvt_links=False):
    if username:
        if is_pvt_links:
            pvt_links = re.findall('https?://t.me+.*', text)
            for i in pvt_links:
                text = text.replace(i, username)
        else:
            usernames = re.findall("([@#][A-Za-z0-9_]+)", text)
            for i in usernames:
                text = text.replace(i, f"@{username}")
    return text
    

#####################  Extract all urls in a string ####################
async def extract_link(string):
    regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    urls = re.findall(regex, string)
    return ["".join(x) for x in urls]

# Incase droplink server fails, bot will return https://droplink.co/st?api={DROPLINK_API}&url={link} 

# TinyUrl 
async def tiny_url_main(url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)

async def bitly_short(url, api):
    s = pyshorteners.Shortener(api_key=api)
    return s.bitly.short(url)

async def bitly_short_handler(text, user):
    api_key = user["bitly_api"]
    
    links = await extract_link(text)

    for link in links:
        long_url = link
        short_url = await bitly_short(long_url, api_key)
        text = text.replace(long_url, short_url)
    return text


# todo -> bypass long droplink url
async def droplink_bypass_handler(text):
    if LINK_BYPASS:
        links = await extract_link(text)
        for link in links:
            if "bindaaslinks.com" in link and IS_BINDASSLINKS:
                bypassed_link = await bindasslink_bypass(link)
            elif "droplink.co" in link and IS_DROPLINK:
                bypassed_link = await droplink_bypass(link)
            elif "tnlink.in" in link and IS_TNLINKS:
                bypassed_link = await tnlink_bypass(link)
            elif "easysky.in" in link and IS_EASYSKY:
                bypassed_link = await easysky_bypass(link)
            elif "indianshortner" in link and IS_INDIANSHORTENER:
                bypassed_link = await indianshortner_bypass(link)
            elif 'lksfy' in link and IS_LINKSHORTIFY:
                bypassed_link = await linkshortify_bypass(link)
            elif 'earnl.site' in link and IS_EARNL_SITE:
                bypassed_link = await earnl_site_bypass(link)
            elif 'earnl.xyz' in link and IS_EARNL_SITE:
                bypassed_link = await earnl_xyz_bypass(link)
            elif 'vearnl.in' in link and IS_URLEARN_XYZ:
                bypassed_link = await urlearn_xyz_bypass(link)
            with contextlib.suppress(Exception):
                text = text.replace(link, bypassed_link)
    return text


# credits -> https://github.com/TheCaduceus/Link-Bypasser
async def droplink_bypass(url):
    try:
        # client = aiohttp.ClientSession()
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as res:    
                ref = re.findall("action[ ]{0,}=[ ]{0,}['|\"](.*?)['|\"]", await res.text())[0]
                h = {'referer': ref}
                # res = client.get(url, headers=h)
                async with client.get(url, headers=h) as res:
                    bs4 = BeautifulSoup(await res.content.read(), 'html.parser')
                    inputs = bs4.find_all('input')
                    data = { input.get('name'): input.get('value') for input in inputs }
                    h = {
                        'content-type': 'application/x-www-form-urlencoded',
                        'x-requested-with': 'XMLHttpRequest'
                    }
                    p = urlparse(url)
                    final_url = f'{p.scheme}://{p.netloc}/links/go'
                    await asyncio.sleep(3.1)
                    # res = client.post(final_url, data=data, headers=h).json()
                    async with client.post(final_url, data=data, headers=h) as res:
                        res = await res.json()
                        if res['status'] == 'success':
                            return res['url']
                        else:
                            raise Exception("Error while bypassing droplink {0}: {1}".format(url, res['message']))
    except Exception as e:
        raise Exception(e)

async def indianshortner_bypass(url):
    url = url.replace("https://indianshortner.in", "https://indianshortner.com")
    try:
        h = {'referer': 'https://moddingzone.in/'}
        client = requests.Session()
        res = client.get(url, headers=h)
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = {input.get('name'): input.get('value') for input in inputs}
        h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest', 'referer': 'url'}

        final_url = 'https://indianshortner.com/links/go'
        time.sleep(5.1)
        res = client.post(final_url, data=data, headers=h).json()
        return res['url']
    except Exception as e:
        raise Exception(e)

async def linkshortify_bypass(url):
    url = url.replace("https://lksfy.com", "https://linkshortify.site/")
    try:
        client = requests.Session()
        res = client.get(url, headers={"referer": "https://technoflip.in/"})
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = {input.get('name'): input.get('value') for input in inputs}
        h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest'}
        final_url = 'https://linkshortify.site/links/go'
        time.sleep(int(os.environ.get('COUNTER_VALUE', '3')))
        res = client.post(final_url, data=data, headers=h).json()
        return res['url']
    except Exception as e:
        print(e)

async def easysky_bypass(url):
    url = url.replace("https://m.easysky.in", "https://techy.veganab.co")
    try:
        h = {
            'referer':'https://veganab.co/'
        }
        client = requests.Session()
        res = client.get(url, headers=h)
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = { input.get('name'): input.get('value') for input in inputs }


        h = {
            'content-type': 'application/x-www-form-urlencoded',
            'x-requested-with': 'XMLHttpRequest',
        }

        final_url = 'https://techy.veganab.co/links/go'
        time.sleep(5.1)
        res = client.post(final_url, data=data, headers=h,).json()
        return res['url']

    except Exception as e:
        raise Exception("Error while bypassing droplink {0}: {1}".format(url, e))


async def bindasslink_bypass(url):
    url = url.replace("https://bindaaslinks.com", "https://www.techishant.in/blog/")

    try:
        h = {'referer': 'https://www.techishant.in'}
        client = requests.Session()
        res = client.get(url, headers=h)
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = {input.get('name'): input.get('value') for input in inputs}
        h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest', 'referer': url}
        final_url = 'https://www.techishant.in/blog/links/go'
        time.sleep(5.1)
        res = client.post(final_url, data=data, headers=h).json()
        print(res)
        return res['url']
    except Exception as e:
        raise Exception("Error while bypassing droplink {0}: {1}".format(url, e)) from e

async def earnl_site_bypass(url):
    url = url.replace("Go", "get")
    try:
        client = requests.Session()
        res = client.get(url, headers={"referer": "https://s.apkdone.live/"})
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = {input.get('name'): input.get('value') for input in inputs}
        h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest'}
        final_url = 'https://get.earnl.site/links/go'
        time.sleep(int(os.environ.get('COUNTER_VALUE', '5')))
        res = client.post(final_url, data=data, headers=h).json()
        return res['url']
    except Exception as e:
        print(e)

async def earnl_xyz_bypass(url):
    url = url.replace("go", "v")
    try:
        client = requests.Session()
        res = client.get(url, headers={"referer": "https://short.modmakers.xyz/"})
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = {input.get('name'): input.get('value') for input in inputs}
        h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest'}
        final_url = 'https://v.earnl.xyz/links/go'
        time.sleep(int(os.environ.get('COUNTER_VALUE', '5')))
        res = client.post(final_url, data=data, headers=h).json()
        return res['url']
    except Exception as e:
        print(e)

async def urlearn_xyz_bypass(url):
    url = url.replace("http://vearnl.in/", "https://go.urlearn.xyz/")
    try:
        client = requests.Session()
        res = client.get(url, headers={"referer": "https://download.modmakers.xyz/"})
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = {input.get('name'): input.get('value') for input in inputs}
        h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest'}
        final_url = 'https://go.urlearn.xyz/links/go'
        time.sleep(int(os.environ.get('COUNTER_VALUE', '5')))
        res = client.post(final_url, data=data, headers=h).json()
        print(res)
        return res['url']
    except Exception as e:
        print(e)

async def tnlink_bypass(url):
    url = url.replace("https://tnlink.in", "https://gadgets.usanewstoday.club")
    try:
        h = {
            'referer':'https://usanewstoday.club/'
        }
        client = requests.Session()
        res = client.get(url, headers=h)
        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all('input')
        data = { input.get('name'): input.get('value') for input in inputs }

        h = {
            'content-type': 'application/x-www-form-urlencoded',
            'x-requested-with': 'XMLHttpRequest',
            'referer':'url'
        }
        p = urlparse(url)
        final_url = 'https://gadgets.usanewstoday.club/links/go'
        time.sleep(8.1)
        res = client.post(final_url, data=data, headers=h,).json()
        return res['url']

    except Exception as e:
        raise Exception("Error while bypassing droplink {0}: {1}".format(url, e)) from e

async def is_droplink_url(url):
    domain = urlparse(url).netloc
    domain = url if "droplink.co" in domain else False
    return domain


async def broadcast_admins(c: Client, Message, sender=False):

    admins = ADMINS[:]
    
    if sender:
        admins.remove(sender)

    for i in admins:
        try:
            await c.send_message(i, Message)
        except PeerIdInvalid:
            logging.info(f"{i} have not yet started the bot")
    return

async def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

async def update_stats(m:Message, method):
    reply_markup = json.loads(str(m.reply_markup)) if m.reply_markup else ''
    message = m.caption.html if m.caption else m.text.html

    mdisk_links = re.findall(r'https?://mdisk.me[^\s`!()\[\]{};:".,<>?«»“”‘’]+', message + reply_markup)
    droplink_links = await extract_link(message + reply_markup)
    total_links = len(droplink_links)

    await db.update_posts(1)

    if method == 'mdisk': droplink_links = []
    if method == 'shortener': mdisk_links = []

    await db.update_links(total_links, len(droplink_links), len(mdisk_links))


#  Heroku Stats
async def getRandomUserAgent():
    agents = [
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.699.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.220 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (X11; CrOS i686 0.13.507) AppleWebKit/534.35 (KHTML, like Gecko) Chrome/13.0.763.0 Safari/534.35",
    "Mozilla/5.0 (X11; CrOS i686 0.13.587) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.14 Safari/535.1",
    "Mozilla/5.0 (X11; CrOS i686 1193.158.0) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7",
    "Mozilla/5.0 (X11; CrOS i686 12.0.742.91) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.93 Safari/534.30",
    "Mozilla/5.0 (X11; CrOS i686 12.433.109) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.93 Safari/534.30",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.34 Safari/534.24",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.04 Chromium/11.0.696.0 Chrome/11.0.696.0 Safari/534.24",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.703.0 Chrome/12.0.703.0 Safari/534.24",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21",
    "Opera/9.80 (Windows NT 5.1; U; sk) Presto/2.5.22 Version/10.50",
    "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00",
    "Opera/9.80 (Windows NT 5.1; U; zh-tw) Presto/2.8.131 Version/11.10",
    "Opera/9.80 (Windows NT 5.1; U;) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (Windows NT 5.2; U; en) Presto/2.6.30 Version/10.63",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.6.30 Version/10.61",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (X11; Linux x86_64; U; pl) Presto/2.7.62 Version/11.00",
    "Opera/9.80 (X11; Linux x86_64; U; Ubuntu/10.10 (maverick); pl) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.117 Mobile Safari/537.36"
    ]
    return agents[random.randint(0, len(agents)-1)]


async def TimeFormatter(milliseconds) -> str:
    milliseconds = int(milliseconds) * 1000
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (f"{str(days)}d, " if days else "") + (f"{str(hours)}h, " if hours else "") + (f"{str(minutes)}m, " if minutes else "") + (f"{str(seconds)}s, " if seconds else "") + (f"{str(milliseconds)}ms, " if milliseconds else "")

    return tmp[:-2]


async def getHerokuDetails(h_api_key, h_app_name):
    if (not h_api_key) or (not h_app_name):
        logger.info("if you want heroku dyno stats, read readme.")
        return None
    try:
        heroku_api = "https://api.heroku.com"
        Heroku = heroku3.from_key(h_api_key)
        app = Heroku.app(h_app_name)
        useragent = await getRandomUserAgent()
        user_id = Heroku.account().id
        headers = {
            "User-Agent": useragent,
            "Authorization": f"Bearer {h_api_key}",
            "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }
        path = f"/accounts/{user_id}/actions/get-quota"

        async with aiohttp.ClientSession() as session:
            result = (await session.get(heroku_api + path, headers=headers))

        result=await result.json()

        abc = ""
        account_quota = result["account_quota"]
        quota_used = result["quota_used"]
        quota_remain = account_quota - quota_used

        abc += f"<b>- Dyno Used:</b> `{await TimeFormatter(quota_used)}`\n"
        abc += f"<b>- Free:</b> `{await TimeFormatter(quota_remain)}`\n"
        # App Quota
        AppQuotaUsed = 0
        OtherAppsUsage = 0
        for apps in result["apps"]:
            if str(apps.get("app_uuid")) == str(app.id):
                try:
                    AppQuotaUsed = apps.get("quota_used")
                except Exception as t:
                    logger.error("error when adding main dyno")
                    logger.error(t)
            else:
                try:
                    OtherAppsUsage += int(apps.get("quota_used"))
                except Exception as t:
                    logger.error("error when adding other dyno")
                    logger.error(t)
        logger.info(f"This App: {str(app.name)}")
        abc += f"<b>- This App:</b> `{await TimeFormatter(AppQuotaUsed)}`\n"
        abc += f"<b>- Other:</b> `{await TimeFormatter(OtherAppsUsage)}`"
        return abc
    except Exception as g:
        logger.error(g)
        return None


async def get_me_button(user):
    user_id = user["user_id"]

    try:
        user['is_pvt_link']
    except KeyError:
        await update_user_info(user_id, {"pvt_link":None, "is_pvt_link":False})

    buttons = []
    try:
        buttons = [[InlineKeyboardButton('Header Text', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_header_text"] else '✅ Enable', callback_data=f'setgs#is_header_text#{not user["is_header_text"]}#{str(user_id)}')], [InlineKeyboardButton('Footer Text', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_footer_text"] else '✅ Enable', callback_data=f'setgs#is_footer_text#{not user["is_footer_text"]}#{str(user_id)}')], [InlineKeyboardButton('Username', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_username"] else '✅ Enable', callback_data=f'setgs#is_username#{not user["is_username"]}#{str(user_id)}')], [InlineKeyboardButton('Banner Image', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_banner_image"] else '✅ Enable', callback_data=f'setgs#is_banner_image#{not user["is_banner_image"]}#{str(user_id)}')], [InlineKeyboardButton('Bitly Link', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_bitly_link"] else '✅ Enable', callback_data=f'setgs#is_bitly_link#{not user["is_bitly_link"]}#{str(user_id)}')], [InlineKeyboardButton('Channel Link', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_pvt_link"] else '✅ Enable', callback_data=f'setgs#is_pvt_link#{not user["is_pvt_link"]}#{str(user_id)}')]]
    except Exception as e:
        print(e)
    return buttons

async def user_api_check(user):
    user_method = user["method"]
    text = ""
    if user_method in ["mdisk", "mdlink"] and not user["mdisk_api"]:
        text += "\n\nSend your Mdisk API to continue..."
    if user_method in ["shortener", "mdlink"] and not user["shortener_api"]:
        text += f"\n\nSend your Shortener API to continue...\nCurrent Website {user['base_site']}"

    return text or True

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")


async def file_store_handler(message, user):
    # FIle store Bot 
    try:
        post_message: Message = await message.copy(chat_id = temp.DB_CHANNEL.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(chat_id = temp.DB_CHANNEL.id, disable_notification=True)
    except Exception as e:
        logging.error(e)
        await message.reply_text("Something went Wrong while storing file")
        return
    try:
        converted_id = post_message.id * abs(temp.DB_CHANNEL.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://telegram.me/{FILE_STORE_BOT_USERNAME}?start={base64_string}"
        link = await replace_link(user, link)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
        await message.reply_text(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)
    except Exception as e:
        logging.error(e, exc_info=True)


#  Tg DIRECT Link Generator
async def direct_gen_handler(c: Client, m: Message, user):
    # FIle store Bot 
    try:
        log_msg = await m.forward(chat_id=DIRECT_GEN_DB)
        reply_markup, Stream_Text, stream_link = await gen_link(m=m, log_msg=log_msg, user=user)
        await log_msg.reply_text(text=f"**Requested By :** [{m.chat.first_name}](tg://user?id={m.chat.id})\n**Group ID :** `{m.from_user.id}`\n**Download Link :** {stream_link}", disable_web_page_preview=True, quote=True)
        
        await m.reply_text(
            text=Stream_Text,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=DIRECT_GEN_DB, text=f"Got Floodwait Of {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**User ID :** `{str(m.from_user.id)}`", disable_web_page_preview=True, )


def get_media_from_message(message: "Message"):
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        if media := getattr(message, attr, None):
            return media

def get_hash(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, "file_unique_id", "")[:6]

def get_media_file_size(m):
    media = get_media_from_message(m)
    return getattr(media, "file_size", "None")

def get_name(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, "file_name", "None")

def get_media_mime_type(m):
    media = get_media_from_message(m)
    return getattr(media, "mime_type", "None/unknown")

def get_media_file_unique_id(m):
    media = get_media_from_message(m)
    return getattr(media, "file_unique_id", "")

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{str(round(size, 2))} {Dic_powerN[n]}B"


# Generate Text, Stream Link, reply_markup
async def gen_link(m: Message,log_msg: Messages, user):
    """Generate Text for Stream Link, Reply Text and reply_markup"""
    # lang = getattr(Language, message.from_user.language_code)

    file_name = get_name(log_msg)
    file_size = humanbytes(get_media_file_size(log_msg))

    page_link = f"{DIRECT_GEN_URL}watch/{get_hash(log_msg)}{log_msg.id}"
    stream_link = f"{DIRECT_GEN_URL}{log_msg.id}/{quote_plus(get_name(m))}?hash={get_hash(log_msg)}"
    
    # short
    page_link = await replace_link(user, page_link)
    stream_link = await replace_link(user, stream_link)

    Stream_Text=stream_msg_text.format(file_name, file_size, stream_link, page_link)

    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🖥STREAM", url=page_link), InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ 📥", url=stream_link)],])

    return reply_markup, Stream_Text, stream_link

