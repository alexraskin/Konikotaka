import datetime
import logging
import os
import random
import time

from aiohttp import ClientSession, ClientTimeout
from discord import ActivityType, Game, Intents
from discord.ext import tasks
from discord.ext.commands import Bot, DefaultHelpCommand
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")


class WiseOldManBot(Bot):
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
        self.start_time = None
        self.start_time = time.time()

    async def start(self, *args, **kwargs) -> None:
        self.session = ClientSession(timeout=ClientTimeout(total=30))
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def setup_hook(self) -> None:
        startup_extensions = []
        for file in os.listdir(os.path.join(os.path.dirname(__file__), "cogs/")):
            filename, ext = os.path.splitext(file)
            if ".py" in ext:
                startup_extensions.append(f"cogs.{filename}")

        for extension in reversed(startup_extensions):
            try:
                print(f"Loading: {extension}")
                await self.load_extension(f"{extension}")
            except Exception as error:
                exc = f"{type(error).__name__}: {error}"
                print(f"Failed to load extension {extension}\n{exc}")

    def get_uptime(self) -> str:
        """Returns the uptime of the bot."""
        return str(
            datetime.timedelta(seconds=int(round(time.time() - self.start_time)))
        )

    def get_bot_latency(self) -> float:
        """Returns the latency of the bot."""
        return round(self.latency * 1000)


help_command = DefaultHelpCommand(
    no_category="Commands",
)

client = WiseOldManBot(
    command_prefix=".",
    intents=Intents.all(),
    max_messages=10000,
    help_command=help_command,
    description="Hello, I am WiseOldManBot!",
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
        "Smite",
        "Overwatch 2",
        ".cats",
        "with Bartholomeow",
    ]
    await client.change_presence(
        activity=Game(
            name=random.choice(list(activities)),
            type=ActivityType.playing,
            emoji=":cosmo:1146224388220391434",
        )
    )


@client.event
async def on_ready():
    print(f"{client.user.name} has connected to Discord!")
    change_activity.start()


client.run(token=discord_token, reconnect=True, log_handler=None)
print(f"{client.user.name} has disconnected from Discord!")
