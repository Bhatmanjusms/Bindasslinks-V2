from pyrogram import Client, filters
from selenium import webdriver
from selenium import *
import os
import asyncio
from selenium.common.exceptions import NoSuchElementException
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.users import get_user, update_user_info
from config import base_sites


# EMAIL
@Client.on_message(filters.command('email') & filters.private)
async def email(bot, message: Message):
    if len(message.command) > 1:
        userid = message.from_user.id
        email_id = message.command[1]
        user = await get_user(userid)
        site_index = base_sites.index(user['base_site']) + 1
        await update_user_info(userid, {f'base_site_{site_index}': {'email': email_id}})
        await message.reply_text(f'Email Added Successfully for {user["base_site"]} ✅')
    else:
        await message.reply(f"Please Provide {user['base_site']} Email Along With Command")

# password
@Client.on_message(filters.command('password') & filters.private)
async def password(bot, message: Message):
    if len(message.command) > 1:
        userid = message.from_user.id
        password = message.command[1]
        user = await get_user(userid)
        site_index = base_sites.index(user['base_site']) + 1
        await update_user_info(userid, {f'base_site_{site_index}': {'password': password}})
        await message.reply_text(f'Password Added Successfully for {user["base_site"]} ✅')
    else:
        await message.reply(f"Please Provide {user['base_site']} password Along With Command")

@Client.on_message(filters.command('stats') & filters.private)
async def balance(bot, message: Message):
  try:
    userid = message.from_user.id
    user = await get_user(userid)

    site_index = base_sites.index(user['base_site']) + 1
    mail = user[f'base_site_{site_index}']['email']

    if not mail:
        await message.reply_text("**Please Add Email First**", quote=True)
#     mail = db3.get(str(message.from_user.id))
    username = driver.find_element("xpath",'//*[@id="username"]').send_keys(mail)
    asyncio.sleep(3)
    passwd = user[f'base_site_{site_index}']['password']
    if not passwd:
        await message.reply_text("**Please Add Password First**", quote=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "/app/.apt/usr/bin/google-chrome")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH", "/app/.chromedriver/bin/chromedriver"), chrome_options=chrome_options)
    fetch = await message.reply_text("**🔍 Fetching Details....**\n**🚫 Don't Spam**", quote=True)
    login2 = f"https://{user['base_site']}/auth/signin"
    # driver = webdriver.Chrome()
    driver.get(login2)

#     passwd = db4.get(str(message.from_user.id))
    password = driver.find_element("xpath",'//*[@id="password"]').send_keys(passwd)
    asyncio.sleep(3)
    sign = driver.find_element("xpath",'//*[@id="invisibleCaptchaSignin"]').click()
    asyncio.sleep(5)
    # balance = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section/div[3]/div[2]/div/div/div/div[1]/span').text()
    view = driver.find_element('xpath',"/html/body/div[1]/div[1]/section/div[3]/div[1]/div/div/div/div[1]/span").text
    view2 = view.replace(" ","")
    balance = driver.find_element("xpath",'/html/body/div[1]/div[1]/section/div[3]/div[2]/div/div/div/div[1]/span').text
    name = driver.find_element('xpath',"/html/body/div[1]/aside/section/li/a/div[2]/p").text 
    date = driver.find_element('xpath',"/html/body/div[1]/div[1]/section/div[3]/div[1]/div/div/p/span[2]").text
    avg_cpm = driver.find_element('xpath',"/html/body/div[1]/div[1]/section/div[3]/div[4]/div/div/div/div[1]/span").text
    ref_earn = driver.find_element('xpath',"/html/body/div[1]/div[1]/section/div[3]/div[3]/div/div/div/div[1]/span").text
    tbalance = driver.find_element('xpath',"/html/body/div[1]/aside/section/ul/li[3]/a/span").click()
    asyncio.sleep(3)
    total_balance = driver.find_element('xpath',"/html/body/div[1]/div[1]/section/div[2]/div[1]/div/div/div/div/h6").text
    msg = f"**😎Username:** {name}\n**🗓Date:** {date}\n\n**📊Your Today's Statistic\n\n**👀 Views:** {view2}\n**💰Earnings:** {balance}\n**👬REF Earn:** {ref_earn}\n**💲Avg CPM:** {avg_cpm}\n\n**🤑 Total Available Balance :** {total_balance}"
    driver.close()
    await fetch.delete()
    await message.reply_text(msg, quote=True)
    driver.quit()
  except NoSuchElementException as e:
    print(e)
    await fetch.delete()
#     message.reply_text(f"**Please Add Mail & Password Before Using This Command!!**\n\n**(or)**\n\n**Invalid Email or Password**", quote=True)
    await message.reply(f"**Please Add Mail & Password Before Using This Command!!**\n\n**(or)**\n\n**Invalid Email or Password**\n\n Click On **Help** Button To Know", bot,
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Help', callback_data="help"),InlineKeyboardButton('About Bot', callback_data="about")]]))