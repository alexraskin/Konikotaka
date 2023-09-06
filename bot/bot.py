import os
import random
import logging
import datetime
import time

from aiohttp import ClientSession, ClientTimeout
from discord import Intents, Game
import discord
from discord.utils import utcnow
from discord.ext import tasks
from discord.ext.commands import Bot, DefaultHelpCommand
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class WiseOldManBot(Bot):
    bot_app_info: discord.AppInfo

    def __init__(self, *args, **options) -> None:
        super().__init__(*args, **options)
        self.session = None
        self.engine = create_engine(os.getenv("MYSQL_URL"))
        self.db_session = None
        self.start_time = time.time()

    async def start(self, *args, **kwargs) -> None:
        self.session = ClientSession(timeout=ClientTimeout(total=30))
        self.DB_Session = sessionmaker(bind=self.engine)
        self.db_session = self.DB_Session()
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = utcnow()

        log.info(f"Ready: {self.user} ID: {self.user.id}")

    async def setup_hook(self) -> None:
        startup_extensions = []
        for file in os.listdir(os.path.join(os.path.dirname(__file__), "cogs/")):
            filename, ext = os.path.splitext(file)
            if ".py" in ext:
                startup_extensions.append(f"cogs.{filename}")

        for extension in reversed(startup_extensions):
            try:
                log.info(f"Loading: {extension}")
                await self.load_extension(f"{extension}")
            except Exception as error:
                exc = f"{type(error).__name__}: {error}"
                log.error(f"Failed to load extension {extension}\n{exc}")

    def get_bot_latency(self) -> float:
        return round(self.latency * 1000)

    def get_uptime(self) -> str:
        """Returns the uptime of the bot."""
        return str(
            datetime.timedelta(seconds=int(round(time.time() - self.start_time)))
        )


help_command = DefaultHelpCommand(
    no_category="Commands",
)

client = WiseOldManBot(
    command_prefix="?",
    intents=Intents.all(),
    max_messages=10000,
    help_command=help_command,
    description="Hello, I am WiseOldManBot!",
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
)


@tasks.loop(minutes=1)
async def change_activity():
    activities = [
        "with Cosmo",
        ".cosmo",
        "RuneLite",
        ".help",
        "Fishing in Lumbridge",
        "Grand Exchange",
        "SMITE",
        "Overwatch 2",
        ".cats",
        "with Bartholomeow",
        "With Snad's Mom",
        "Annoying Seaira",
        "/newpet",
    ]
    await client.change_presence(
        activity=Game(
            name=random.choice(list(activities)),
            emoji="<:cosmo:1146224388220391434>",
        )
    )


@client.event
async def on_ready():
    log.info(f"{client.user.name} has connected to Discord!")
    change_activity.start()


client.run(token=discord_token, reconnect=True, log_handler=None)
log.info(f"{client.user.name} has disconnected from Discord!")
