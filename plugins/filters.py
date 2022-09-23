from config import ADMINS, IS_PRIVATE
from database.users import get_user
from pyrogram.filters import create
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


async def is_private_filter(_, __, m: Message):
    
    user = m.from_user.id
    has_access = (await get_user(user))["has_access"]

    is_private = not bool(IS_PRIVATE)

    REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Request Access', callback_data=f'request_access#{m.from_user.id}'),
        ],

    ])
    if m.from_user.id not in ADMINS and IS_PRIVATE and not has_access :
        await m.reply_text(f"This bot works only for authorized users. Request admin to use this bot" ,reply_markup=REPLY_MARKUP ,disable_web_page_preview=True)
    else:
        return True

    return is_private

is_private = create(is_private_filter)
