from pyrogram import Client, filters
from config import ADMINS, CHANNEL_ID, CHANNELS, FORWARD_MESSAGE
from database.users import get_user
from utils import broadcast_admins, main_convertor_handler, update_stats, user_api_check
from database import db
from helpers import temp

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


# edit forwarded message
@Client.on_message(filters.chat(CHANNEL_ID) & (
        filters.channel | filters.group) & filters.incoming & ~filters.private & filters.forwarded)
async def channel_forward_link_handler(c:Client, message):
    
    user = await get_user(message.from_user.id)
    user_method = user["method"]

    vld = await user_api_check(user)

    if vld is not True and CHANNELS: return await broadcast_admins(c, "To use me in channel...\n\n" + vld )

    if FORWARD_MESSAGE and CHANNELS :
        try:

            await main_convertor_handler(message, user_method)
            await message.delete()
            # Updating DB stats
            await update_stats(message, user_method)

        except Exception as e:
            logger.error(e)