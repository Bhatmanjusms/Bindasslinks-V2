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


class Config(object):
    # Mandatory variables for the bot to start
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DROPLINK_API = os.environ.get("DROPLINK_API")
    MDISK_API = os.environ.get("MDISK_API")
    ADMINS = []
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "MdiskConvertor")
    DATABASE_URL = os.environ.get("DATABASE_URL", None)
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

    #  Optionnal variables
    BROADCAST_AS_COPY = False
    IS_PRIVATE = False
    INCLUDE_DOMAIN = []
    EXCLUDE_DOMAIN = []
    CHANNELS = True
    CHANNEL_ID = []
    FORWARD_MESSAGE = False
    SOURCE_CODE = "https://github.com/kevinnadar22/URL-Shortener-V2"
    USERNAME = None
    HASHTAG = None
    HEADER_TEXT = ''
    FOOTER_TEXT = ''
    BANNER_IMAGE = ''
    WELCOME_IMAGE = ''
    LINK_BYPASS = False

    #  Heroku Config
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
    HEROKU = bool(HEROKU_API_KEY and HEROKU_APP_NAME and "DYNOS" in os.environ)

    #  Replit Config
    REPLIT_USERNAME = os.environ.get("REPLIT_USERNAME", None)
    REPLIT_APP_NAME = os.environ.get("REPLIT_APP_NAME", None)
    REPLIT = f"https://{REPLIT_APP_NAME.lower()}.{REPLIT_USERNAME}.repl.co" if REPLIT_APP_NAME and REPLIT_USERNAME else False
    PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "300"))

    VERIFIED_TIME = 1
    LOG_CHANNEL = 0
    UPDATE_CHANNEL = False
    KEYBOARD_BUTTON = True

    IS_MDISK = True
    IS_DEFAULT_BASE_SITE = True
    FILE_STORE_DB = 0
    FILE_STORE_BOT_USERNAME = None
    FILE_STORE = bool(FILE_STORE_DB and FILE_STORE_BOT_USERNAME)

    DIRECT_GEN_DB = 0
    DIRECT_GEN_BOT_USERNAME = None
    DIRECT_GEN_URL = None
    DIRECT_GEN = bool(FILE_STORE_DB and FILE_STORE_BOT_USERNAME and DIRECT_GEN_URL)

    IS_BINDASSLINKS = True
    IS_DROPLINK = True
    IS_TNLINKS= True
    IS_INDIANSHORTENER = True
    IS_EASYSKY = True
    IS_LINKSHORTIFY = True
    IS_EARNL_SITE = True
    IS_EARNL_XYZ = True
    IS_URLEARN_XYZ = True

    stream_msg_text ="""
<u>**Successfully Generated Your Link !**</u>\n
<b>📂 File Name :</b> {}\n
<b>📦 File Size :</b> {}\n"""

    BASE_SITE = os.environ.get('BASE_SITE', None)
    BASE_SITE_2 = os.environ.get('BASE_SITE_2', None)
    BASE_SITE_3 = os.environ.get('BASE_SITE_3', None)

    base_sites = [i for i in [BASE_SITE, BASE_SITE_2, BASE_SITE_3] if i != None]

