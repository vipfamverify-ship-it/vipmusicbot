import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import FloodWait
import random
import re

from VipMusic import app

SPAM_CHATS = []

# Random emojis with EMOJI IDs for tagging
EMOJI = [
    "<emoji id=5427277540316177618>🎉</emoji>",
    "<emoji id=6161292171371614915>✨</emoji>",
    "<emoji id=6160949166693423526>⭐</emoji>",
    "<emoji id=6161146215497995845>🌟</emoji>",
    "<emoji id=6161019007156623342>✨</emoji>",
    "<emoji id=6160940168736937091>💎</emoji>",
    "<emoji id=5368475679937534380>👑</emoji>",
    "<emoji id=5413582255408815156>🎉</emoji>",
    "<emoji id=6050916670120138116>🎊</emoji>",
    "<emoji id=6050699997609989854>🥳</emoji>",
    "<emoji id=6325685291621287657>🔥</emoji>",
    "<emoji id=6328049610988193312>🚀</emoji>",
    "<emoji id=6120436698695338614>💯</emoji>",
    "<emoji id=6129705667616841573>⚡</emoji>",
    "<emoji id=6129572317472233948>🔰</emoji>",
    "<emoji id=6129731974291527294>💕</emoji>",
    "<emoji id=6129776848109836451>🔵</emoji>",
    "<emoji id=6129631914438434952>🟢</emoji>",
    "<emoji id=6129579597441801084>💘</emoji>",
    "<emoji id=6129758830722030858>❤️</emoji>",
    "<emoji id=6129911435205024348>😀</emoji>",
    "<emoji id=5352849115740904895>🦋</emoji>",
    "<emoji id=5353066170503142084>💞</emoji>",
    "<emoji id=4958617898751886363>💥</emoji>",
]

def clean_text(text):
    """Escape markdown special characters"""
    if not text:
        return ""
    return re.sub(r'([_*()~`>#+-=|{}.!])', r'\\1', text)

async def is_admin(chat_id, user_id):
    """Check if user is admin in the chat"""
    try:
        admin_ids = [
            admin.user.id
            async for admin in app.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ]
        return user_id in admin_ids
    except:
        return False

async def process_members(chat_id, members, text=None, replied=None):
    """Process and tag members in batches of 5"""
    tagged_members = 0
    usernum = 0
    usertxt = ""
    
    for member in members:
        if chat_id not in SPAM_CHATS:
            break
        if member.user.is_deleted or member.user.is_bot:
            continue
            
        tagged_members += 1
        usernum += 1
        
        emoji = random.choice(EMOJI)
        usertxt += f"{emoji} <a href='tg://user?id={member.user.id}'>{member.user.first_name or 'User'}</a> "
        
        if usernum == 5:
            try:
                if replied:
                    await replied.reply_text(
                        usertxt,
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await app.send_message(
                        chat_id,
                        f"{text}\n\n{usertxt}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.HTML
                    )
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
            except FloodWait as e:
                await asyncio.sleep(e.value + 2)
            except Exception:
                continue
    
    if usernum > 0 and chat_id in SPAM_CHATS:
        try:
            if replied:
                await replied.reply_text(
                    usertxt,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML
                )
            else:
                await app.send_message(
                    chat_id,
                    f"{text}\n\n{usertxt}",
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML
                )
        except Exception:
            pass
    
    return tagged_members

@app.on_message(filters.command(["tagall", "all", "mentionall"], prefixes=["/", "@", "!", "#"]))
async def tag_all_users(_, message):
    # Check admin permission
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return await message.reply_text("<emoji id=4956337889593000947>❌</emoji> Only admins can use this command.", parse_mode=ParseMode.HTML)
    
    # Check if already running
    if message.chat.id in SPAM_CHATS:
        return await message.reply_text("<emoji id=6082163188558728946>⚠️</emoji> Tagging is already running! Use <code>/cancel</code> to stop it.", parse_mode=ParseMode.HTML)
    
    # Check if user provided text or replied to a message
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text(
            "<emoji id=4956726373679891220>📝</emoji> <b>Usage:</b>\n"
            "<code>/tagall Hello Everyone</code>\n\n"
            "Or reply to a message with <code>/tagall</code>",
            parse_mode=ParseMode.HTML
        )
    
    # Send initial message
    status_msg = await message.reply_text("<emoji id=4956260073375532310>🔄</emoji> <b>Processing...</b>\n\nFetching members list...", parse_mode=ParseMode.HTML)
    
    try:
        # Get all members
        members = []
        async for m in app.get_chat_members(message.chat.id):
            members.append(m)
        
        total_members = len(members)
        
        if total_members == 0:
            return await status_msg.edit_text("<emoji id=4956337889593000947>❌</emoji> No members found in this chat!", parse_mode=ParseMode.HTML)
        
        await status_msg.edit_text(
            f"<emoji id=4956259055468282692>🔄</emoji> <b>Tagging Started!</b>\n\n"
            f"<emoji id=4956461073550017373>👥</emoji> Total members: <code>{total_members}</code>\n"
            f"<emoji id=4956539525422646612>⏳</emoji> Please wait...",
            parse_mode=ParseMode.HTML
        )
        
        SPAM_CHATS.append(message.chat.id)
        
        # Get text message
        text = None
        if not replied:
            text = clean_text(message.text.split(None, 1)[1])
        
        # Start tagging
        tagged_members = await process_members(message.chat.id, members, text=text, replied=replied)
        
        # Send completion message
        await status_msg.delete()
        await app.send_message(
            message.chat.id,
            f"<emoji id=6240185119961783395>✅</emoji> <b>Tagging Completed!</b>\n\n"
            f"<emoji id=6152289902739329361>👥</emoji> Total members: <code>{total_members}</code>\n"
            f"<emoji id=6235439400143034173>🏷️</emoji> Tagged members: <code>{tagged_members}</code>\n\n"
            f"<emoji id=6161292051112531249>⚡</emoji> <b>Command by:</b> {message.from_user.mention}",
            parse_mode=ParseMode.HTML
        )
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await status_msg.edit_text(f"<emoji id=4956337889593000947>❌</emoji> Rate limited! Please wait <code>{e.value}</code> seconds.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await status_msg.edit_text(f"<emoji id=4956337889593000947>❌</emoji> Error: <code>{str(e)[:100]}</code>", parse_mode=ParseMode.HTML)
    finally:
        try:
            if message.chat.id in SPAM_CHATS:
                SPAM_CHATS.remove(message.chat.id)
        except:
            pass

@app.on_message(filters.command(["admins", "adminmention", "report"], prefixes=["/", "@", "!", "#"]))
async def tag_all_admins(_, message):
    # Check admin permission
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return await message.reply_text("<emoji id=4956337889593000947>❌</emoji> Only admins can use this command.", parse_mode=ParseMode.HTML)
    
    # Check if already running
    if message.chat.id in SPAM_CHATS:
        return await message.reply_text("<emoji id=4956726373679891220>⚠️</emoji> Tagging is already running! Use <code>/cancel</code> to stop it.", parse_mode=ParseMode.HTML)
    
    # Check if user provided text or replied to a message
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text(
            "<emoji id=6235637621473680408>📝</emoji> <b>Usage:</b>\n"
            "<code>/admins Hello Admins</code>\n\n"
            "Or reply to a message with <code>/admins</code>",
            parse_mode=ParseMode.HTML
        )
    
    # Send initial message
    status_msg = await message.reply_text("<emoji id=6242244140168386678>🔄</emoji> <b>Processing...</b>\n\nFetching admins list...", parse_mode=ParseMode.HTML)
    
    try:
        # Get all admins
        members = []
        async for m in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            members.append(m)
        
        total_admins = len(members)
        
        if total_admins == 0:
            return await status_msg.edit_text("<emoji id=4956337889593000947>❌</emoji> No admins found in this chat!", parse_mode=ParseMode.HTML)
        
        await status_msg.edit_text(
            f"<emoji id=4956260073375532310>🔄</emoji> <b>Tagging Admins!</b>\n\n"
            f"<emoji id=4956461073550017373>👥</emoji> Total admins: <code>{total_admins}</code>\n"
            f"<emoji id=4956539525422646612>⏳</emoji> Please wait...",
            parse_mode=ParseMode.HTML
        )
        
        SPAM_CHATS.append(message.chat.id)
        
        # Get text message
        text = None
        if not replied:
            text = clean_text(message.text.split(None, 1)[1])
        
        # Start tagging
        tagged_admins = await process_members(message.chat.id, members, text=text, replied=replied)
        
        # Send completion message
        await status_msg.delete()
        await app.send_message(
            message.chat.id,
            f"<emoji id=6161196191737451564>✅</emoji> <b>Admin Tagging Completed!</b>\n\n"
            f"<emoji id=6143005514885239872>👥</emoji> Total admins: <code>{total_admins}</code>\n"
            f"<emoji id=6235394337346165182>🏷️</emoji> Tagged admins: <code>{tagged_admins}</code>\n\n"
            f"<emoji id=6030821243991626781>⚡</emoji> <b>Command by:</b> {message.from_user.mention}",
            parse_mode=ParseMode.HTML
        )
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await status_msg.edit_text(f"<emoji id=4956337889593000947>❌</emoji> Rate limited! Please wait <code>{e.value}</code> seconds.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await status_msg.edit_text(f"<emoji id=4956337889593000947>❌</emoji> Error: <code>{str(e)[:100]}</code>", parse_mode=ParseMode.HTML)
    finally:
        try:
            if message.chat.id in SPAM_CHATS:
                SPAM_CHATS.remove(message.chat.id)
        except:
            pass

@app.on_message(filters.command(["cancel", "stopmention", "cancelall"], prefixes=["/", "@", "!", "#"]))
async def cancel_tagging(_, message):
    # Check admin permission
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return await message.reply_text("<emoji id=4956337889593000947>❌</emoji> Only admins can use this command.", parse_mode=ParseMode.HTML)
    
    if message.chat.id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(message.chat.id)
            return await message.reply_text("<emoji id=6161196191737451564>✅</emoji> <b>Tagging process stopped successfully!</b>", parse_mode=ParseMode.HTML)
        except:
            return await message.reply_text("<emoji id=4956337889593000947>❌</emoji> Failed to stop tagging process!", parse_mode=ParseMode.HTML)
    else:
        return await message.reply_text("<emoji id=4956337889593000947>❌</emoji> No tagging process is currently running!", parse_mode=ParseMode.HTML)