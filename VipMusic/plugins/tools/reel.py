import aiohttp
import asyncio
import os
import re
import time
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ButtonStyle
from pyrogram.errors import FloodWait
from VipMusic import app

IG_API_URL = "http://13.60.50.211:5000/download"

def extract_instagram_url(text):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/reel\/([a-zA-Z0-9_\-]+)(?:\/)?(?:\?[^\s]+)?',
        r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/p\/([a-zA-Z0-9_\-]+)(?:\/)?(?:\?[^\s]+)?',
        r'(?:https?:\/\/)?(?:www\.)?instagr\.am\/reel\/([a-zA-Z0-9_\-]+)(?:\/)?(?:\?[^\s]+)?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url
    return None

async def download_reel(video_url, file_path, mystic, file_type="mp4"):
    """Download reel from API with progress and flood wait handling"""
    try:
        start_time = time.time()
        last_update_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            params = {"url": video_url}
            
            async with session.get(IG_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status != 200:
                    return False
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 256):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                # Update every 2 seconds only (flood wait fix)
                                current_time = time.time()
                                if current_time - last_update_time >= 2:
                                    percentage = int((downloaded / total_size) * 100)
                                    
                                    # Progress bar
                                    bar_length = 12
                                    filled = int(bar_length * downloaded // total_size)
                                    bar = '█' * filled + '░' * (bar_length - filled)
                                    
                                    elapsed = time.time() - start_time
                                    speed = downloaded / elapsed if elapsed > 0 else 0
                                    eta = int((total_size - downloaded) / speed) if speed > 0 else 0
                                    
                                    downloaded_mb = downloaded / (1024 * 1024)
                                    total_mb = total_size / (1024 * 1024)
                                    speed_mb = speed / (1024 * 1024)
                                    
                                    progress_text = f"**⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ...**\n\n"
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

async def safe_edit(message, text, reply_markup=None):
    """Safe edit with flood wait handling"""
    try:
        if reply_markup:
            await message.edit_text(text, reply_markup=reply_markup)
        else:
            await message.edit_text(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        if reply_markup:
            await message.edit_text(text, reply_markup=reply_markup)
        else:
            await message.edit_text(text)
    except Exception as e:
        print(f"Edit error: {e}")

@app.on_message(filters.command(["reel", "ig", "instagram"]))
async def reel_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "**🎬 ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ**\n\n"
            "**ᴜꜱᴀɢᴇ :** `/reel [ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ʟɪɴᴋ]`\n\n"
            "**ᴇxᴀᴍᴘʟᴇ :**\n"
            "`/reel https://www.instagram.com/reel/DY6fZXfhof3/`"
        )
        return
    
    query = message.text.split(None, 1)[1]
    
    # Extract Instagram URL
    reel_url = extract_instagram_url(query)
    
    if not reel_url:
        await message.reply_text(
            "**❌ ɪɴᴠᴀʟɪᴅ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ʟɪɴᴋ !**\n\n"
            "**ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ.**"
        )
        return
    
    mystic = await message.reply_text(
        "**🎬 ᴘʀᴏᴄᴇꜱꜱɪɴɢ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ...**\n\n"
        f"**🔗 ʟɪɴᴋ :** `{reel_url[:50]}...`"
    )
    
    # Create output directory
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename
    reel_id = reel_url.split("/")[-1].split("?")[0]
    output_file = os.path.join(output_dir, f"ig_{reel_id}.mp4")
    
    # Download reel
    success = await download_reel(reel_url, output_file, mystic, "mp4")
    
    if not success:
        await safe_edit(mystic, 
            "**❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ !**\n\n"
            "**ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄʜᴇᴄᴋ ᴛʜᴇ ʟɪɴᴋ.**"
        )
        return
    
    await safe_edit(mystic, "**📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ...**")
    
    try:
        # Prepare caption
        caption = f"""**🎬 ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !** ✅

**🔗 ꜱᴏᴜʀᴄᴇ :** [ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ]({reel_url})
**📹 ꜰᴏʀᴍᴀᴛ :** ᴍᴘ4

**⚡ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʙʏ :** {message.from_user.mention}

**🎵 ᴇɴᴊᴏʏ ʏᴏᴜʀ ʀᴇᴇʟ !**"""

        await message.reply_video(
            video=output_file,
            caption=caption,
            supports_streaming=True
        )
        
        await mystic.delete()
        
        # Clean up file
        try:
            os.remove(output_file)
        except:
            pass
            
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await safe_edit(mystic, f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ :** ғʟᴏᴏᴅ ᴡᴀɪᴛ {e.value}s")
    except Exception as e:
        await safe_edit(mystic, f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ :** `{str(e)[:100]}`")
        try:
            os.remove(output_file)
        except:
            pass

# Private message handler
@app.on_message(filters.command(["reel", "ig", "instagram"]) & filters.private)
async def reel_command_pm(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "**🎬 ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ**\n\n"
            "**ᴜꜱᴀɢᴇ :** `/reel [ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ʟɪɴᴋ]`\n\n"
            "**ᴇxᴀᴍᴘʟᴇ :**\n"
            "`/reel https://www.instagram.com/reel/DY6fZXfhof3/`"
        )
        return
    
    query = message.text.split(None, 1)[1]
    
    reel_url = extract_instagram_url(query)
    
    if not reel_url:
        await message.reply_text(
            "**❌ ɪɴᴠᴀʟɪᴅ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ʟɪɴᴋ !**\n\n"
            "**ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ.**"
        )
        return
    
    mystic = await message.reply_text(
        "**🎬 ᴘʀᴏᴄᴇꜱꜱɪɴɢ ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ...**\n\n"
        f"**🔗 ʟɪɴᴋ :** `{reel_url[:50]}...`"
    )
    
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    
    reel_id = reel_url.split("/")[-1].split("?")[0]
    output_file = os.path.join(output_dir, f"ig_{reel_id}.mp4")
    
    success = await download_reel(reel_url, output_file, mystic, "mp4")
    
    if not success:
        await safe_edit(mystic,
            "**❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ !**\n\n"
            "**ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄʜᴇᴄᴋ ᴛʜᴇ ʟɪɴᴋ.**"
        )
        return
    
    await safe_edit(mystic, "**📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ...**")
    
    try:
        caption = f"""**🎬 ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !** ✅

**🔗 ꜱᴏᴜʀᴄᴇ :** [ɪɴꜱᴛᴀɢʀᴀᴍ ʀᴇᴇʟ]({reel_url})
**📹 ꜰᴏʀᴍᴀᴛ :** ᴍᴘ4

**⚡ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʙʏ :** {message.from_user.mention}

**🎵 ᴇɴᴊᴏʏ ʏᴏᴜʀ ʀᴇᴇʟ !**"""

        await message.reply_video(
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
        await safe_edit(mystic, f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ :** ғʟᴏᴏᴅ ᴡᴀɪᴛ {e.value}s")
    except Exception as e:
        await safe_edit(mystic, f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ :** `{str(e)[:100]}`")
        try:
            os.remove(output_file)
        except:
            pass