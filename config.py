import os
from dotenv import load_dotenv

load_dotenv()

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Mandatory variables for the bot to start
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DROPLINK_API = os.environ.get("DROPLINK_API")
MDISK_API = os.environ.get("MDISK_API")
ADMINS = [int(i.strip()) for i in os.environ.get("ADMINS").split(",")] if os.environ.get("ADMINS") else []
DATABASE_NAME = os.environ.get("DATABASE_NAME", "MdiskConvertor")
DATABASE_URL = os.environ.get("DATABASE_URL", None)
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

#  Optionnal variables
BROADCAST_AS_COPY = is_enabled((os.environ.get('BROADCAST_AS_COPY', "False")), False)
IS_PRIVATE = is_enabled(os.environ.get("IS_PRIVATE", "False"), "False")
INCLUDE_DOMAIN = [i.strip() for i in os.environ.get("INCLUDE_DOMAIN").split(",")] if os.environ.get("INCLUDE_DOMAIN") else []
EXCLUDE_DOMAIN = [i.strip() for i in os.environ.get("EXCLUDE_DOMAIN").split(",")] if os.environ.get("EXCLUDE_DOMAIN") else []
CHANNELS = is_enabled((os.environ.get('CHANNELS', "True")), True)
CHANNEL_ID = [int(i.strip()) for i in os.environ.get("CHANNEL_ID").split(" ")] if os.environ.get("CHANNEL_ID") else []
FORWARD_MESSAGE = is_enabled((os.environ.get('FORWARD_MESSAGE', "False")), False)
SOURCE_CODE = os.environ.get("SOURCE_CODE", "https://github.com/kevinnadar22/URL-Shortener-V2")
USERNAME = os.environ.get("USERNAME", None)
HEADER_TEXT = os.environ.get("HEADER_TEXT", '')
FOOTER_TEXT = os.environ.get("FOOTER_TEXT", '')
BANNER_IMAGE = os.environ.get("BANNER_IMAGE", '')
WELCOME_IMAGE = os.environ.get("WELCOME_IMAGE", '')
LINK_BYPASS = is_enabled((os.environ.get('LINK_BYPASS', "False")), False)
BASE_SITE = os.environ.get("BASE_SITE", "droplink.co")

#  Heroku Config
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
HEROKU = bool(HEROKU_API_KEY and HEROKU_APP_NAME and "DYNOS" in os.environ)

#  Replit Config
REPLIT_USERNAME = os.environ.get("REPLIT_USERNAME", None)
REPLIT_APP_NAME = os.environ.get("REPLIT_APP_NAME", None)
REPLIT = f"https://{REPLIT_APP_NAME.lower()}.{REPLIT_USERNAME}.repl.co" if REPLIT_APP_NAME and REPLIT_USERNAME else False
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "300"))

VERIFIED_TIME = int(os.environ.get("VERIFIED_TIME", "1"))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", False)


IS_MDISK = is_enabled(os.environ.get("IS_MDISK", "True"), "True")
IS_DEFAULT_BASE_SITE = is_enabled(os.environ.get("IS_DEFAULT_BASE_SITE", "True"), "True")
FILE_STORE_DB = int(os.environ.get("FILE_STORE_DB", "0"))
FILE_STORE_BOT_USERNAME = os.environ.get("FILE_STORE_BOT_USERNAME", None)
FILE_STORE = bool(FILE_STORE_DB and FILE_STORE_BOT_USERNAME)

DIRECT_GEN_DB = int(os.environ.get("DIRECT_GEN_DB", "0"))
DIRECT_GEN_BOT_USERNAME = os.environ.get("DIRECT_GEN_BOT_USERNAME", None)
DIRECT_GEN_URL = os.environ.get("DIRECT_GEN_URL", None)
DIRECT_GEN = bool(FILE_STORE_DB and FILE_STORE_BOT_USERNAME and DIRECT_GEN_URL)


IS_BINDASSLINKS = is_enabled(os.environ.get("IS_BINDASSLINKS", "True"), "True")
IS_DROPLINK = is_enabled(os.environ.get("IS_DROPLINK", "True"), "True")
IS_TNLINKS= is_enabled(os.environ.get("IS_TNLINKS", "True"), "True")
IS_INDIANSHORTENER = is_enabled(os.environ.get("IS_INDIANSHORTENER", "True"), "True")
IS_EASYSKY = is_enabled(os.environ.get("IS_EASYSKY", "True"), "True")
IS_LINKSHORTIFY = is_enabled(os.environ.get("IS_LINKSHORTIFY", "True"), "True")
IS_EARNL_SITE = is_enabled(os.environ.get("IS_EARNL_SITE", "True"), "True")
IS_EARNL_XYZ = is_enabled(os.environ.get("IS_EARNL_XYZ", "True"), "True")
IS_URLEARN_XYZ = is_enabled(os.environ.get("IS_URLEARN_XYZ", "True"), "True")

stream_msg_text ="""
<u>**Successfully Generated Your Link !**</u>\n
<b>📂 File Name :</b> {}\n
<b>📦 File Size :</b> {}\n
<b>📥 Download :</b> {}\n
<b>🖥 Watch :<//b> {}"""


BASE_SITE_2 = os.environ.get('BASE_SITE_2', None)
BASE_SITE_3 = os.environ.get('BASE_SITE_3', None)

base_sites = [i for i in [BASE_SITE, BASE_SITE_2, BASE_SITE_3] if i != None]

