import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from VipMusic import LOGGER, app, userbot
from VipMusic.core.call import Venom
from VipMusic.misc import sudo
from VipMusic.plugins import ALL_MODULES
from VipMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("VipMusic.plugins" + all_module)
    LOGGER("VipMusic.plugins").info("Successfully Imported Modules...")
    await userbot.start()
    await Venom.start()
    try:
        await Venom.stream_call("https://files.catbox.moe/74dq91.jpg")
    except NoActiveGroupCall:
        LOGGER("VipMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Venom.decorators()
    LOGGER("VipMusic").info(
        "Vip Music Started Successfully.\n\nDon't forget to visit @VIP_X_OFFICIAL"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("VipMusic").info("Stopping Vip Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
