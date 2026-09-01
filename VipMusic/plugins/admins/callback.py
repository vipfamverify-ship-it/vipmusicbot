import asyncio
import math
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle

from VipMusic import YouTube, app
from VipMusic.core.call import Venom
from VipMusic.misc import SUDOERS, db
from VipMusic.utils.database import (
    get_active_chats,
    get_lang,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from VipMusic.utils.decorators.language import languageCB
from VipMusic.utils.formatters import seconds_to_min, time_to_seconds
from VipMusic.utils.stream.autoclear import auto_clean
from VipMusic.utils.thumbnails import gen_thumb
from config import (
    BANNED_USERS,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    adminlist,
)
from strings import get_string
import config

# ============ STREAM MARKUP WITH PROGRESS BAR ============
def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    if duration_sec == 0:
        percentage = 0
    else:
        percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "◉—————————"
    elif 10 < umm < 20:
        bar = "—◉————————"
    elif 20 <= umm < 30:
        bar = "——◉———————"
    elif 30 <= umm < 40:
        bar = "———◉——————"
    elif 40 <= umm < 50:
        bar = "————◉—————"
    elif 50 <= umm < 60:
        bar = "—————◉————"
    elif 60 <= umm < 70:
        bar = "——————◉———"
    elif 70 <= umm < 80:
        bar = "———————◉——"
    elif 80 <= umm < 95:
        bar = "————————◉—"
    else:
        bar = "—————————◉"
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 ᴜᴘᴅᴀᴛᴇs",
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                text="🆘 sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_GROUP,
                style=ButtonStyle.SUCCESS
            ),
        ],
        [InlineKeyboardButton(text="CLOSE", callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons

def close_markup(_):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text="CLOSE", callback_data="close", style=ButtonStyle.DANGER)]])


# ============ CALLBACK HANDLERS ============
@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def admin_callback(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
    chat_id = int(chat)
    
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    
    mention = CallbackQuery.from_user.mention
    
    # Check admin rights
    is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
    if not is_non_admin:
        if CallbackQuery.from_user.id not in SUDOERS:
            admins = adminlist.get(CallbackQuery.message.chat.id)
            if not admins or CallbackQuery.from_user.id not in admins:
                return await CallbackQuery.answer(_["admin_14"], show_alert=True)
    
    if command == "Pause":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_1"], show_alert=True)
        await music_off(chat_id)
        await Venom.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_2"].format(mention), reply_markup=close_markup(_))
        
    elif command == "Resume":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_3"], show_alert=True)
        await music_on(chat_id)
        await Venom.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_4"].format(mention), reply_markup=close_markup(_))
        
    elif command == "Stop" or command == "End":
        await Venom.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(_["admin_5"].format(mention), reply_markup=close_markup(_))
        await CallbackQuery.message.delete()
        
    elif command == "Skip" or command == "Replay":
        check = db.get(chat_id)
        if not check:
            return await CallbackQuery.answer(_["queue_2"], show_alert=True)
        
        if command == "Skip":
            try:
                popped = check.pop(0)
                if popped:
                    await auto_clean(popped)
            except:
                pass
        
        if not check:
            await Venom.stop_stream(chat_id)
            return
        
        queued = check[0]
        title = queued["title"].title()
        user = queued["by"]
        duration = queued["dur"]
        videoid = queued["vidid"]
        
        db[chat_id][0]["played"] = 0
        
        button = stream_markup_timer(_, chat_id, "00:00", duration)
        
        caption = _["stream_1"].format(
            f"https://t.me/{app.username}?start=info_{videoid}" if videoid not in ["telegram", "soundcloud"] else config.SUPPORT_GROUP,
            title[:23], duration, user
        )
        
        run = await CallbackQuery.message.reply_photo(
            photo=config.STREAM_IMG_URL,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        await CallbackQuery.message.delete()
        
    await CallbackQuery.answer()


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    await CallbackQuery.message.delete()


@app.on_callback_query(filters.regex("GetTimer") & ~BANNED_USERS)
async def timer_callback(_, CallbackQuery):
    await CallbackQuery.answer()


# ============ PROGRESS BAR TIMER ============
async def markup_timer():
    while True:
        await asyncio.sleep(4)
        try:
            active_chats = await get_active_chats()
            for chat_id in active_chats:
                try:
                    if not await is_music_playing(chat_id):
                        continue
                    playing = db.get(chat_id)
                    if not playing:
                        continue
                    if playing[0]["seconds"] == 0:
                        continue
                    
                    mystic = playing[0].get("mystic")
                    if not mystic:
                        continue
                    
                    try:
                        language = await get_lang(chat_id)
                        _ = get_string(language)
                    except:
                        _ = get_string("en")
                    
                    played = seconds_to_min(playing[0]["played"])
                    dur = playing[0]["dur"]
                    
                    buttons = stream_markup_timer(_, chat_id, played, dur)
                    await mystic.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
                except Exception as e:
                    continue
        except Exception as e:
            continue


# Start the timer
asyncio.create_task(markup_timer())
