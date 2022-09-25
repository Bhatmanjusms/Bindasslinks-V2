from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import BASE_SITE, DATABASE_URL, DATABASE_NAME, VERIFIED_TIME

client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
col = db["users"]
misc = db["misc"]

async def get_user(user_id):

    user_id = int(user_id)

    user = await col.find_one({"user_id": user_id})

    if not user:
        res = {
            "user_id": user_id,
            "method":"shortener",
            "shortener_api_1":None,
            "shortener_api_2":None,
            "shortener_api_3":None,
            "shortener_api": None,
            "mdisk_api": None,
            "header_text": "",
            "footer_text": "",
            "username": None,
            "base_site": BASE_SITE,
            "banner_image": None,
            "bitly_api":None,
            "pvt_link": None,
            "is_pvt_link": True,
            "is_bitly_link": False,
            "is_banner_image": True,
            "is_username": True,
            "is_header_text": True,
            "is_footer_text": True,
            "include_domain": [],
            "exclude_domain": [],
            "has_access": False,
            "last_verified": datetime(2020, 5, 17),
        }

        await col.insert_one(res)
        user = await col.find_one({"user_id": user_id})
    return user

async def update_user_info(user_id, value:dict):
    user_id = int(user_id)
    myquery = {"user_id": user_id}
    newvalues = { "$set": value }
    await col.update_one(myquery, newvalues)

async def total_users_count():
    count = await col.count_documents({})
    return count

async def get_all_users():
    return col.find({})

async def delete_user(user_id):
    await col.delete_one({'user_id': int(user_id)})


async def update_verify_user(user_id, value:dict):
    user_id = int(user_id)
    await get_user(user_id)
    myquery = {"user_id": user_id}
    newvalues = { "$set": value }
    await misc.update_one(myquery, newvalues)

async def is_user_verified(user_id):
    user = await get_user(user_id)
    try:
        pastDate = user["last_verified"]
    except Exception:
        user = await get_user(user_id)
        pastDate = user["last_verified"]
    return (datetime.now() - pastDate).days <= VERIFIED_TIME

async def total_users_count():
    return await col.count_documents({})

async def is_user_exist(id):
    user = await col.find_one({'user_id':int(id)})
    return bool(user)