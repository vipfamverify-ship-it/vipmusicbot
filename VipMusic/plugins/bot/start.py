import time
import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from VipMusic import app
from VipMusic.misc import _boot_
from VipMusic.plugins.sudo.sudoers import sudoers_list
from VipMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VipMusic.utils import bot_sys_stats
from VipMusic.utils.decorators.language import LanguageStart
from VipMusic.utils.formatters import get_readable_time
from VipMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# ========== NEW ADDITIONS ==========
# Random stickers (Replace with your own sticker IDs)
RAM_STKR = [
    "CAACAgUAAxkBAAIBO2i1Spi48ZdWCNehv-GklSI9aRYWAAJ9GAACXB-pVds_sm8brMEqHgQ",
    "CAACAgUAAxkBAAIBOmi1Sogwaoh01l5-e-lJkK1VNY6MAAIlGAACKI6wVVNEvN-6z3Z7HgQ",
    "CAACAgUAAxkBAAIBPGi1Spv1tlx90xM1Q7TRNyL0fhcJAAKDGgACZSupVbmJpWW9LmXJHgQ",
    "CAACAgUAAxkBAAIBPWi1SpxJZKxuWYsZ_G06j_G_9QGkAAIsHwACdd6xVd2HOWQPA_qtHgQ",
    "CAACAgUAAxkBAAIBPmi1Sp4QFoLkZ0oN3d01kZQOHQRwAAI4FwACDDexVVp91U_1BZKFHgQ",
    "CAACAgUAAxkBAAIBP2i1SqFoa4yqgl1QSISZrQ4VuYWgAAIpFQACvTqpVWqbFSKOnWYxHgQ",
    "CAACAgUAAxkBAAIBQGi1Sqk3OGQ2jRW2rN6ZVZ7vWY2ZAAJZHQACCa-pVfefqZZtTHEdHgQ",
]

# Valid reaction emojis
emojis = ["🥰", "🔥", "💖", "😁", "😎", "🌚", "🎉", "🙈"]
# ===================================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # ====== STEP 1: REACTION ======
    try:
        await message.react(random.choice(emojis))
    except Exception:
        pass

    # ====== STEP 2: STICKER ======
    try:
        sticker = await message.reply_sticker(random.choice(RAM_STKR))
        await asyncio.sleep(1)
        await sticker.delete()
    except Exception:
        pass

    # ====== STEP 3: ANIMATION (8 messages) ======
    ram = await message.reply_text("<emoji id=4958719848390591540>🦋</emoji>")
    await asyncio.sleep(1)
    await ram.edit_text(f"<emoji id=5987715818337603766>✨</emoji> ʜᴇʟʟᴏ ᴅᴇᴀʀ {message.from_user.mention}")
    await asyncio.sleep(0.4)
    await ram.edit_text("<emoji id=4958719848390591540>🦋</emoji> ɪ ᴀᴍ ʏᴏᴜʀ ᴍᴜsɪᴄ ʙᴏᴛ..<emoji id=4958719848390591540>🦋</emoji>")
    await asyncio.sleep(0.4)
    await ram.edit_text("<emoji id=4956706659780003072>❓</emoji> ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ᴛᴏᴅᴀʏ.....??")
    await asyncio.sleep(0.4)
    await ram.edit_text("<emoji id=4956222745814762495>❤️‍🔥</emoji> ᴅɪηɢ ᴅᴏηɢ.<emoji id=4956222745814762495>❤️‍🔥</emoji>")
    await asyncio.sleep(0.4)
    await ram.edit_text("<emoji id=4956222745814762495>❤️‍🔥</emoji> ᴅɪηɢ ᴅᴏηɢ..<emoji id=4956222745814762495>❤️‍🔥</emoji>")
    await asyncio.sleep(0.4)
    await ram.edit_text("<emoji id=4956222745814762495>❤️‍🔥</emoji> ᴅɪηɢ ᴅᴏηɢ...<emoji id=4956222745814762495>❤️‍🔥</emoji>")
    await asyncio.sleep(0.4)
    await ram.edit_text("<emoji id=5352657886617018049>🥀</emoji> sᴛᴀʀᴛᴇᴅ!<emoji id=5352657886617018049>🥀</emoji>")
    await asyncio.sleep(0.5)
    await ram.delete()

    # ====== REST OF YOUR ORIGINAL CODE ======
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_GROUP),
                reply_markup=keyboard,
                has_spoiler=True,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("<emoji id=5472214816766577537>🔎</emoji>")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            from py_yt import VideosSearch
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🎬 Watch on YouTube", url=link),
                        InlineKeyboardButton(text="🆘 Support", url=config.SUPPORT_GROUP),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
                has_spoiler=True,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        UP, CPU, RAM, DISK = await bot_sys_stats()
        
        welcome_text = f"""<blockquote expandable>
<emoji id=4956539525422646612>❤️</emoji><emoji id=4958719848390591540>🦋</emoji> ʜᴇʟʟᴏ {message.from_user.mention} ! <emoji id=4958719848390591540>🦋</emoji><emoji id=4956539525422646612>❤️</emoji>

<emoji id=5470135030393090150>🎵</emoji> {app.mention}
ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ
ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ

<emoji id=6237585097084638739>📌</emoji> ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ
ᴛᴏ ᴋɴᴏᴡ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs

<emoji id=6129479035077531636>✨</emoji> ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ
ᴀɴᴅ ᴇɴᴊᴏʏ ᴍᴜsɪᴄ ɪɴ ᴠᴄ

<emoji id=6030821243991626781>⚡</emoji> ᴜᴘᴛɪᴍᴇ : `{UP}`

<emoji id=4956739572114392015>💎</emoji> ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ : <a href='tg://user?id={config.OWNER_ID}'>VIP_X_OFFICIAL</a>
</blockquote>"""
        
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=welcome_text,
            reply_markup=out,
            parse_mode=ParseMode.HTML,
            has_spoiler=True,
        )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=out,
        has_spoiler=True,
    )
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_GROUP,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                welcome_group_text = f"""<blockquote expandable>
<emoji id=4956539525422646612>❤️</emoji><emoji id=4958719848390591540>🦋</emoji> ɢʀᴇᴇᴛɪɴɢs, {message.chat.title} ! <emoji id=4958719848390591540>🦋</emoji><emoji id=4956539525422646612>❤️</emoji>

<emoji id=6328074912640534314>🎉</emoji> ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ {app.mention}
ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ !

<emoji id=5470135030393090150>🎵</emoji> ɴᴏᴡ ᴇɴᴊᴏʏ ᴛʜᴇ ʙᴇsᴛ
ᴍᴜsɪᴄ ᴇxᴘᴇʀɪᴇɴᴄᴇ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ

<emoji id=6237585097084638739>📌</emoji> ᴜsᴇ /help ᴄᴏᴍᴍᴀɴᴅ
ᴛᴏ ᴠɪᴇᴡ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs

<emoji id=4956739572114392015>💎</emoji> ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ : <a href='tg://user?id={config.OWNER_ID}'>VIP_X_OFFICIAL</a>
</blockquote>"""

                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=welcome_group_text,
                    reply_markup=out,
                    parse_mode=ParseMode.HTML,
                    has_spoiler=True,
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)