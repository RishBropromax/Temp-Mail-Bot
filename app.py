import os
import asyncio
import requests
import random
import bs4

from pykeyboard import InlineKeyboard
from pyrogram.errors import UserNotParticipant
from pyrogram import filters, Client
from RandomWordGenerator import RandomWord
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, bad_request_400


from database import (
    get_served_users,
    add_served_user,
    remove_served_user,
    get_served_chats,
    add_served_chat,
    remove_served_chat
)

app = Client(
    "Fake_mail_bot",
    api_hash= os.environ["API_HASH"],
    api_id=os.environ["API_ID"],
    bot_token=os.environ["BOT_TOKEN"]
)

#********************************************************************************
start_text = """
Hello! {}, 
Welcome Temp Mail Bot

For Temp Mail Users

π₯ Powered By ImRishmika API
βοΈ Simple & Friendly BOT
π― Group Supported
β‘οΈ Fast Response 
β 24 Hour Active 

Send /help

β₯οΈ I can create **temp emails** for you. 
β₯οΈ Send /tempmail to **create new mail**
 
π€ Don't Forget to Share Your Friends β

βββββββββββββββββ

βοΈ Dα΄α΄ α΄Κα΄α΄α΄Κ : @ImRishmika
π₯ </> ΡΠΌΟ Π²ΟΡ βΡΞ½ΟβΟΟΡΚΡ Corporation Β©οΈ

βββββββββββββββββ
"""


start_button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("β¨α΄α΄α΄ κ±α΄α΄©α΄©α΄Κα΄ ", url="https://t.me/EmoBotSupport"),
                    InlineKeyboardButton("πͺΡΠΌΟ Π²ΟΡ βΡΞ½ΟβΟΟΡΚΡ", url="https://t.me/EmoBotDevolopers")
                ],
		[
                    InlineKeyboardButton("</> ΚΞΉΡΠ½ΠΌΞΉΠΊΞ± ΡΞ±nα΄Ξ±nΟ", url=f"http://t.me/ImRishmika"),
                ], 
                [
                    InlineKeyboardButton("βAdd to Group β", url=f"http://t.me/?startgroup=new"),
                ]  
            ]
)

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    try:
       await message._client.get_chat_member(-1001719968457, message.from_user.id)
    except UserNotParticipant:
       await app.send_message(
			chat_id=message.from_user.id,
			text=f"""
π§ **Access Denied** {message.from_user.mention}
You must,
πΉ[join Our Telegram Channel](https://t.me/EmoBotDevolopers).

""")
       return
    name = message.from_user.id
    if message.chat.type != "private":
       await app.send_message(
        name,
        text = start_text.format(message.from_user.mention),
        reply_markup = start_button)
       return await add_served_chat(message.chat.id) 
    else:
        await app.send_message(
    name,
    text = start_text.format(message.from_user.mention),
    reply_markup = start_button)
    return await add_served_user(message.from_user.id) 
    
#********************************************************************************
API1='https://www.1secmail.com/api/v1/?action=getDomainList'
API2='https://www.1secmail.com/api/v1/?action=getMessages&login='
API3='https://www.1secmail.com/api/v1/?action=readMessage&login='
#********************************************************************************

create = InlineKeyboardMarkup(
            [[InlineKeyboardButton("</> ΡΠΌΟ Π²ΟΡ βΡΞ½ΟβΟΟΡΚΡ π±π°", url="https://t.me/EmoBotDevolopers")]])

#********************************************************************************
@app.on_message(filters.command("tempmail"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    m =  await app.send_message(name,text=f"βοΈCreating Your Temp Mail...",reply_markup = create)
    rp = RandomWord(max_word_size=8, include_digits=True)
    email = rp.generate()
    xx = requests.get(API1).json()
    domain = random.choice(xx)
    #print(email)
    mes = await app.send_message(
    name, 
    text = f"""
**π¬Done,Your Email Address Created!**
**Email** : `{email}@{domain}`
**Mail BOX** : `empty`
**Powered by** : @EmoBotDevolopers""",
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("π« Update Mail BOX π«", callback_data = f"mailbox |{email}|{domain}")]]))
    pi = await mes.pin(disable_notification=True, both_sides=True)
    await m.delete()
    await pi.delete()

async def gen_keyboard(mails, email, domain):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    for mail in mails:
        id = mail['id']
        data.append(
            InlineKeyboardButton(f"{mail['subject']}", f"mail |{email}|{domain}|{id}")
        )
        num += 1
    data.append(
        InlineKeyboardButton(f"β»οΈ Update Mail BOX β»οΈ", f"mailbox |{email}|{domain}")
    )
    i_kbd.add(*data)
    return i_kbd
 
#********************************************************************************

@app.on_callback_query(filters.regex("mailbox"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain = callback_request.split("|")
    mails = requests.get(f'{API2}{email}&domain={domain}').json()
    if mails == []:
            await query.answer("π€·ββοΈ No Mails found! π€·ββοΈ")
    else:
        try:
            smail = f"{email}@{domain}"
            mbutton = await gen_keyboard(mails,email, domain)
            await query.message.edit(f""" 
**π¬Done,Your Email Address Created!**
π§ **Email** : `{smail}`
π¨ **Mail BOX** : β
**Powered by** : @EmoBotDevolopers""",
reply_markup = mbutton
)   
        except bad_request_400.MessageNotModified as e:
            await query.answer("π€·ββοΈ No New Mails found! π€·ββοΈ")

#********************************************************************************

@app.on_callback_query(filters.regex("mail"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain, id = callback_request.split("|")
    mail = requests.get(f'{API3}{email}&domain={domain}&id={id}').json()
    froms = mail['from']
    subject = mail['subject']
    date = mail['date']
    if mail['textBody'] == "":
        kk = mail['htmlBody']
        body = bs4.BeautifulSoup(kk, 'lxml')
        txt = body.get_text()
        text = " ".join(txt.split())
        url_part = body.find('a')
        link = url_part['href']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("π Open Link", url=link)
                ],
                [
                    InlineKeyboardButton("βοΈ Back", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{text}
""",
reply_markup = mbutton
)
    else:
        body = mail['textBody']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("βοΈ Back", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{body}
""",
reply_markup = mbutton
)
#********************************************************************************

@app.on_message(filters.command("domains"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    x = requests.get(f'https://www.1secmail.com/api/v1/?action=getDomainList').json()
    xx = str(",".join(x))
    email = xx.replace(",", "\n")
    await app.send_message(
    name, 
    text = f"""
**{email}**
""",
    reply_markup = create)



#============================================================================================
#Owner commands pannel here
#user_count, broadcast_tool

@app.on_message(filters.command("stats") & filters.user(5171347305))
async def stats(_, message: Message):
    name = message.from_user.id
    served_chats = len(await get_served_chats())
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    served_users = len(await get_served_users())
    served_users = []
    users = await get_served_users()
    for user in users:
        served_users.append(int(user["bot_users"]))

    await app.send_message(
        name,
        text=f"""
π Chats Stats π
πββοΈ Users : `{len(served_users)}`
π₯ Groups : `{len(served_chats)}`
π§ Total users & groups : {int((len(served_chats) + len(served_users)))} """)

async def broadcast_messages(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await remove_served_user(user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await remove_served_user(user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await remove_served_user(user_id)
        return False, "Error"
    except Exception as e:
        return False, "Error"

@app.on_message(filters.private & filters.command("bcast") & filters.user([5171347305]) & filters.reply)
async def broadcast_message(_, message):
    b_msg = message.reply_to_message
    chats = await get_served_users() 
    m = await message.reply_text("Broadcast in progress..")
    for chat in chats:
        try:
            await broadcast_messages(int(chat['bot_users']), b_msg)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass  
    await m.edit(f"""
Broadcast Completed:.""")    

@app.on_message(filters.command("ads"))
async def ads_message(_, message):
	await app.forward_messages(
		chat_id = message.chat.id, 
		from_chat_id = int(-1001468061399), 
		message_ids = 2255,
	)

print("I'm Alive Now Baby !")
app.run()
