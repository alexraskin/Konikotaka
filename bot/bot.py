import datetime
import logging
import os
import random
import time

import discord
import wavelink
from aiohttp import ClientSession, ClientTimeout
from cogs import EXTENSIONS
from cogs.utils.lists import activities, games, songs
from discord.ext import tasks
from discord.ext.commands import (Bot, DefaultHelpCommand, NoEntryPointError,
                                  when_mentioned_or)
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
        self.engine: create_async_engine = create_async_engine(
            os.getenv("MYSQL_URL"), echo=True, future=True
        )
        self.start_time = time.time()
        self.log = log
        self.cosmo_guild: int = 1020830000104099860
        self.lavalink_uri = os.getenv("LAVALINK_URI")
        self.lavalink_password = os.getenv("LAVALINK_PASSWORD")
        self.logo_url = "https://i.gyazo.com/b44411736275628586cc8b3ff4239789.jpg"

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

    async def on_ready(self) -> None:
        if not hasattr(self, "uptime"):
            self.uptime = time.time()

        self.log.info(f"Ready: {self.user} ID: {self.user.id}")

    async def setup_hook(self) -> None:
        node: wavelink.Node = wavelink.Node(
            uri=self.lavalink_uri, password=self.lavalink_password
        )
        node1: wavelink.Node = wavelink.Node(
            uri="lava2.horizxon.studio:80", password="horizxon.studio"
        )
        await wavelink.NodePool.connect(client=self, nodes=[node, node1])
        for cog in EXTENSIONS:
            try:
                await self.load_extension(cog)
                self.log.info(f"Loaded extension: {cog}")
            except NoEntryPointError:
                self.log.error(
                    f"Could not load extension: {cog} due to NoEntryPointError"
                )
            except Exception as exc:
                self.log.error(
                    f"Could not load extension: {cog} due to {exc.__class__.__name__}: {exc}"
                )

    @property
    def get_bot_latency(self) -> float:
        """
        Returns the websocket latency in seconds.
        """
        return round(self.latency * 1000)

    @property
    def get_uptime(self) -> str:
        """Returns the uptime of the bot."""
        return str(
            datetime.timedelta(seconds=int(round(time.time() - self.start_time)))
        )


client = WiseOldManBot(
    command_prefix=when_mentioned_or(os.getenv("PREFIX", "?")),
    intents=discord.Intents.all(),
    max_messages=10000,
    description="Hello, I am WiseOldManBot!",
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
)


@tasks.loop(minutes=1)
async def change_activity() -> None:
    await client.change_presence(activity=discord.Game(name=random.choice(activities)))


@client.event
async def on_ready() -> None:
    client.log.info(f"{client.user.name} has connected to Discord!")
    change_activity.start()


client.run(token=os.getenv("DISCORD_TOKEN"), reconnect=True, log_handler=None)
client.log.info(f"{client.user.name} has disconnected from Discord!")
