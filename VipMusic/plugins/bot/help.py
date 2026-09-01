from typing import Union

from pyrogram import filters, types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, Message

from VipMusic import app
from VipMusic.utils import help_pannel
from VipMusic.utils.database import get_lang
from VipMusic.utils.decorators.language import LanguageStart, languageCB
from VipMusic.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_GROUP
from strings import get_string, helpers


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        try:
            await update.edit_message_text(
                _["help_1"].format(SUPPORT_GROUP),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except:
            await update.message.reply_text(
                _["help_1"].format(SUPPORT_GROUP),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_GROUP),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(
        _["help_2"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    cb = CallbackQuery.data.strip().split(None, 1)[1]
    keyboard = help_back_markup(_)
    
    # Handle all help callbacks
    if cb == "hb16":
        text = helpers.HELP_16
    elif cb == "hb17":
        text = helpers.HELP_17
    elif cb == "hb18":
        text = helpers.HELP_18
    elif cb == "hb19":
        text = helpers.HELP_19
    else:
        text = getattr(helpers, f"HELP_{cb[2:]}")
    
    # ✅ FIX: Try-except for already deleted messages
    try:
        await CallbackQuery.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        await CallbackQuery.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )