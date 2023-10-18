import datetime
import logging
import os
import random
import time

import discord
import psutil
import wavelink
from aiohttp import ClientSession, ClientTimeout
from cogs import EXTENSIONS
from cogs.utils.lists import activities
from discord.ext import tasks
from discord.ext.commands import Bot, NoEntryPointError, when_mentioned_or
from dotenv import load_dotenv
from models.db import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Discord")


class RoboTwizy(Bot):
    bot_app_info: discord.AppInfo

    def __init__(self, *args, **options) -> None:
        super().__init__(*args, **options)
        self.log = log
        self.session = None
        self.pid = os.getpid()
        self.start_time = time.time()
        self.cosmo_guild: int = 1020830000104099860
        self.general_channel: int = 1145087802141315093
        self.version: str = "1.0.6"
        self.lavalink_uri: str = os.getenv("LAVALINK_URI")
        self.lavalink_password: str = os.getenv("LAVALINK_PASSWORD")
        self.logo_url: str = "https://i.gyazo.com/702abd99879359948dfb4e1742a99815.png"
        self.engine: create_async_engine = create_async_engine(
            os.getenv("POSTGRES_URL"),
            echo=False,
            future=True,
            connect_args={"server_settings": {"application_name": "RoboTwizy"}},
        )

    async def start(self, *args, **kwargs) -> None:
        self.session: ClientSession = ClientSession(timeout=ClientTimeout(total=30))
        self.async_session: sessionmaker = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.session.close()
        await self.engine.dispose()
        await super().close()

    async def on_ready(self) -> None:
        self.log.info(f"Ready: {self.user} ID: {self.user.id}")

    async def setup_hook(self) -> None:
        node: wavelink.Node = wavelink.Node(
            uri=self.lavalink_uri, password=self.lavalink_password
        )
        await wavelink.NodePool.connect(client=self, nodes=[node])
        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id
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
    def get_bot_latency(self) -> int:
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

    @property
    def memory_usage(self):
        process = psutil.Process(self.pid)
        memory_info = process.memory_info()
        return round(memory_info.rss / (1024**2))

    @property
    def cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    @property
    def git_revision(self):
        latest_revision = os.getenv("RAILWAY_GIT_COMMIT_SHA")
        if latest_revision is None:
            return None
        url = f"<https://github.com/alexraskin/RoboTwizy/commit/{(short := latest_revision[:7])}>"
        return f"[{short}]({url})"


client: RoboTwizy = RoboTwizy(
    command_prefix=when_mentioned_or(os.getenv("PREFIX", "?")),
    intents=discord.Intents.all(),
    max_messages=10000,
    description="Hello! I am a bot written by Twizy to provide some nice utilities.",
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
)


@tasks.loop(minutes=1)
async def change_activity() -> None:
    await client.change_presence(activity=discord.Game(name=random.choice(activities)))


@tasks.loop(count=1)
async def init_database() -> None:
    async with client.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.close()


@client.event
async def on_ready() -> None:
    client.log.info(f"{client.user.name} has connected to Discord!")
    change_activity.start()
    init_database.start()


client.run(token=os.getenv("DISCORD_TOKEN"), reconnect=True, log_handler=None)
client.log.info(f"{client.user.name} has disconnected from Discord!")
