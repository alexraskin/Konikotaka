import datetime
import logging
import os
import random
import time

from aiohttp import ClientSession, ClientTimeout
from discord import ActivityType, AllowedMentions, Game, Intents, Client
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")

class WiseOldManBot(Client):
    """
    The Bot class is a subclass of the AutoShardedBot class.
    """

    def __init__(self, *args, **options) -> None:
        """
        The __init__ function is the constructor for a class.
        It is called when an instance of a class is created.
        It can take arguments (in this case, *args and **options)

        :param self: Used to refer to the object itself.
        :param *args: Used to pass a non-keyworded, variable-length argument list to the function.
        :param **options: Used to pass a dictionary of keyword arguments to the function.
        :return: a new instance of the Session class.
        """
        super().__init__(*args, **options)
        self.session = None
        self.db_client = None
        self.start_time = None
        self.logger = logging.getLogger("discord")
        self.start_time = time.time()
        self.abs_path = os.listdir(os.path.join(os.path.dirname(__file__), "cogs/"))
        self.help_command = commands.DefaultHelpCommand(no_category="Commands")

    async def start(self, *args, **kwargs) -> None:
        self.session = ClientSession(
            timeout=ClientTimeout(total=30)
        )
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def setup_hook(self) -> None:
        startup_extensions = []

        for file in self.abs_path:
            filename, ext = os.path.splitext(file)
            if ".py" in ext:
                startup_extensions.append(f"cogs.{filename}")

        for extension in reversed(startup_extensions):
            try:
                self.logger.info(f"Loading: {extension}")
                await self.load_extension(f"{extension}")
            except Exception as error:
                exc = f"{type(error).__name__}: {error}"
                self.logger.error(f"Failed to load extension {extension}\n{exc}")

    def get_uptime(self) -> str:
        """Returns the uptime of the bot."""
        return str(
            datetime.timedelta(seconds=int(round(time.time() - self.start_time)))
        )

    def get_bot_latency(self) -> float:
        """Returns the latency of the bot."""
        return round(self.latency * 1000)


client = WiseOldManBot(
    command_prefix=".",
    description="Hello, I am WiseOldManBot!",
    max_messages=15000,
    intents=Intents.all(),
    allowed_mentions=AllowedMentions(everyone=True, users=True, roles=True),
)


@tasks.loop(minutes=1)
async def change_activity():
    activities = [
        "with Cosmo",
        ".cosmo",
        "RuneLite",
        ".help",
        "Fishing in Lumbridge",
        "with the Grand Exchange",
        "Smite",
        "Overwatch 2",
    ]
    await client.wait_until_ready()
    while not client.is_closed():
        await client.change_presence(
            activity=Game(
                name=random.choice(list(activities)),
                type=ActivityType.playing,
                emoji=":cosmo:1146224388220391434",
            )
        )


@client.event
async def on_ready() -> bool:
    """
    The on_ready function specifically accomplishes the following:
        - Sets up a status task that changes the bot's status every 60 seconds.
        - Sets up a clean_dir task that cleans out old files in the cache directory every 5 minutes.

    :return: a string with the details of our main guild.
    """
    logging.info(f"{client.user.name} started successfully")
    change_activity.start()
    return True

client.run(token=discord_token, reconnect=True, log_handler=None)
logging.info(f"{client.user.name} has disconnected from Discord!")
