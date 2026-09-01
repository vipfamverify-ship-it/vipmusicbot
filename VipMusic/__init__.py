import asyncio

# ✅ Fix for uvloop / event loop issue on Heroku (Python 3.10+)
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Optional but recommended if you still use uvloop
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass


# --- Original bot imports ---
from VipMusic.core.bot import Venom
from VipMusic.core.dir import dirr
from VipMusic.core.git import git
from VipMusic.core.userbot import Userbot
from VipMusic.misc import dbb, heroku

from .logging import LOGGER


# --- Initialization calls ---
dirr()
git()
dbb()
heroku()


# --- Create bot & userbot instances ---
app = Venom()
userbot = Userbot()


# --- Platform imports ---
from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
