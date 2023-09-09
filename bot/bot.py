import datetime
import logging
import os
import random
import time

import discord
from aiohttp import ClientSession, ClientTimeout
from discord.ext import tasks
from discord.ext.commands import Bot, DefaultHelpCommand
from discord.utils import utcnow
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Discord")


class WiseOldManBot(Bot):
    bot_app_info: discord.AppInfo

    def __init__(self, *args, **options) -> None:
        super().__init__(*args, **options)
        self.session = None
        self.engine = create_async_engine(os.getenv("MYSQL_URL"), echo=True, future=True)
        self.start_time = time.time()
        self.log = log
        self.cosmo_guild = 1020830000104099860

    async def start(self, *args, **kwargs) -> None:
        self.session = ClientSession(timeout=ClientTimeout(total=30))
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.session.close()
        await self.engine.dispose()
        await super().close()

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = utcnow()

        self.log.info(f"Ready: {self.user} ID: {self.user.id}")

    async def setup_hook(self) -> None:
        startup_extensions = []
        for file in os.listdir(os.path.join(os.path.dirname(__file__), "cogs/")):
            filename, ext = os.path.splitext(file)
            if ".py" in ext:
                startup_extensions.append(f"cogs.{filename}")

        for extension in reversed(startup_extensions):
            try:
                self.log.info(f"Loading: {extension}")
                await self.load_extension(f"{extension}")
            except Exception as error:
                exc = f"{type(error).__name__}: {error}"
                self.log.error(f"Failed to load extension {extension}\n{exc}")

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
    intents=discord.Intents.all(),
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
        activity=discord.Game(name=random.choice(list(activities)))
    )


@client.event
async def on_ready():
    client.log.info(f"{client.user.name} has connected to Discord!")
    change_activity.start()


client.run(token=os.getenv("DISCORD_TOKEN"), reconnect=True, log_handler=None)
client.log.info(f"{client.user.name} has disconnected from Discord!")
