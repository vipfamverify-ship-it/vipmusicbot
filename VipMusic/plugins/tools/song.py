import aiohttp
import asyncio
import os
import time
import re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ButtonStyle
from pyrogram.errors import FloodWait
from VipMusic import app

# TERA WORKING API
API_URL = "https://api.shrutibots.site/download"
API_KEY = "ShrutiBotss6vlVFlaYRwRVh9jucn1"

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:music\.youtube\.com\/watch\?v=)([\w-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if re.match(r'^[\w-]+$', url):
        return url
    return None

async def download_file(video_id, file_path, mystic, file_type):
    try:
        start_time = time.time()
        
        params = {
            "url": video_id,
            "type": file_type,
            "api_key": API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status != 200:
                    return False
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                last_update_time = time.time()
                
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 512):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                # Update every 2 seconds only (flood wait fix)
                                current_time = time.time()
                                if current_time - last_update_time >= 2:
                                    percentage = int((downloaded / total_size) * 100)
                                    
                                    bar_length = 15
                                    filled = int(bar_length * downloaded // total_size)
                                    bar = '●' * filled + '○' * (bar_length - filled)
                                    
                                    elapsed = time.time() - start_time
                                    speed = downloaded / elapsed if elapsed > 0 else 0
                                    eta = int((total_size - downloaded) / speed) if speed > 0 else 0
                                    
                                    downloaded_mb = downloaded / (1024 * 1024)
                                    total_mb = total_size / (1024 * 1024)
                                    speed_mb = speed / (1024 * 1024)
                                    
                                    progress_text = f"**⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {file_type.upper()}...**\n\n"
                                    progress_text += f"`{bar}` **{percentage}%**\n\n"
                                    progress_text += f"**📦 {downloaded_mb:.1f}ᴍʙ / {total_mb:.1f}ᴍʙ**\n"
                                    progress_text += f"**⚡ {speed_mb:.1f}ᴍʙ/s**\n"
                                    progress_text += f"**⏱️ {eta}s**"
                                    
                                    try:
                                        await mystic.edit_text(progress_text)
                                    except FloodWait as e:
                                        await asyncio.sleep(e.value)
                                    except:
                                        pass
                                    
                                    last_update_time = current_time
                                
                                await asyncio.sleep(0.1)
                
                return True
                
    except Exception as e:
        print(f"Download error: {e}")
        return False


@app.on_message(filters.command(["song", "s"]))
async def song_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "**🎵 sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ**\n\n"
            "**ᴜsᴀɢᴇ :** `/song [ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ ᴏʀ sᴏɴɢ ɴᴀᴍᴇ]`\n\n"
            "**ᴇxᴀᴍᴘʟᴇ :**\n"
            "`/song https://youtu.be/ZvXN0TcZLfQ`"
        )
        return
    
    query = message.text.split(None, 1)[1]
    
    video_id = extract_video_id(query)
    
    if not video_id:
        await message.reply_text("**❌ ɪɴᴠᴀʟɪᴅ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ !**")
        return
    
    mystic = await message.reply_text("**🔍 ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ...**")
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴀᴜᴅɪᴏ (ᴍᴘ3)", callback_data=f"dl_audio_{video_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🎬 ᴠɪᴅᴇᴏ (ᴍᴘ4)", callback_data=f"dl_video_{video_id}", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data=f"close", style=ButtonStyle.DANGER),
        ]
    ])
    
    await mystic.edit_text(
        f"**🎵 sᴇʟᴇᴄᴛ ᴅᴏᴡɴʟᴏᴀᴅ ғᴏʀᴍᴀᴛ :**\n\n"
        f"**🔗 ᴠɪᴅᴇᴏ ɪᴅ :** `{video_id}`",
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex(r"dl_(audio|video)_(.*)"))
async def download_callback(client, callback_query: CallbackQuery):
    file_type = callback_query.data.split("_")[1]
    video_id = callback_query.data.split("_")[2]
    
    await callback_query.answer(f"⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {file_type.upper()}...")
    
    mystic = await callback_query.message.edit_text(
        f"**📥 sᴛᴀʀᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...**\n\n"
        f"**🎵 ғᴏʀᴍᴀᴛ :** {file_type.upper()}\n"
        f"**🔗 ɪᴅ :** `{video_id}`"
    )
    
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{video_id}.{file_type}")
    
    success = await download_file(video_id, output_file, mystic, file_type)
    
    if not success:
        await mystic.edit_text(
            "**❌ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ !**\n\n"
            "**ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.**"
        )
        return
    
    await mystic.edit_text("**📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ...**")
    
    try:
        caption = f"""**✅ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ !**

**📹 ғᴏʀᴍᴀᴛ :** {file_type.upper()}
**🎵 ᴠɪᴅᴇᴏ ɪᴅ :** `{video_id}`

**⚡ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʙʏ :** {callback_query.from_user.mention}"""
        
        if file_type == "audio":
            await callback_query.message.reply_audio(
                audio=output_file,
                caption=caption
            )
        else:
            await callback_query.message.reply_video(
                video=output_file,
                caption=caption,
                supports_streaming=True
            )
        
        await mystic.delete()
        
        try:
            os.remove(output_file)
        except:
            pass
            
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await mystic.edit_text(f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ :** ғʟᴏᴏᴅ ᴡᴀɪᴛ {e.value}s")
    except Exception as e:
        await mystic.edit_text(f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ :** `{str(e)[:100]}`")
        try:
            os.remove(output_file)
        except:
            pass


@app.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except:
        pass