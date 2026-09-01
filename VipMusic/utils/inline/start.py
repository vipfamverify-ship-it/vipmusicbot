from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
import config
from VipMusic import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="✨ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY
            )
        ],
        [
            InlineKeyboardButton(
                text="🛡️ ᴏᴡɴᴇʀ",
                user_id=config.OWNER_ID,
                style=ButtonStyle.SUCCESS
            ),
            InlineKeyboardButton(
                text="🆘 sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_GROUP,
                style=ButtonStyle.PRIMARY
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 ᴜᴘᴅᴀᴛᴇs",
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                text="💳 ᴘᴀʏᴍᴇɴᴛ ɢᴀᴛᴇᴡᴀʏ",
                url="https://darkpay.co",
                style=ButtonStyle.DANGER
            )
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY
            )
        ],
        [
            InlineKeyboardButton(
                text="📚 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs",
                callback_data="settings_back_helper",
                style=ButtonStyle.SUCCESS
            )
        ],
        [
            InlineKeyboardButton(
                text="👑 ᴏᴡɴᴇʀ",
                user_id=config.OWNER_ID,
                style=ButtonStyle.SUCCESS
            ),
            InlineKeyboardButton(
                text="🆘 sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_GROUP,
                style=ButtonStyle.PRIMARY
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 ᴜᴘᴅᴀᴛᴇs",
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                text="💳 ᴘᴀʏᴍᴇɴᴛ ɢᴀᴛᴇᴡᴀʏ",
                url="https://darkpay.co",
                style=ButtonStyle.DANGER
            )
        ]
    ]
    return InlineKeyboardMarkup(buttons)