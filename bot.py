import datetime
import logging
import os
import random

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)


load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")
streamer_name = "pr3daturd574"

activities = [
    "with Cosmo",
    ".cosmo",
]

help_command = commands.DefaultHelpCommand(no_category="Commands", )

bot = commands.Bot(
    command_prefix=".",
    intents=discord.Intents.all(),
    help_command=help_command,
    description="The Wizard of Cosmo",
)


async def make_request(url: str, headers: dict = None, body: dict = None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, body=body) as response:
                logger.info(
                    f"Made request to {url} with headers {headers} and body {body}"
                )
                return await response
        except aiohttp.ClientError as e:
            logger.error(f"Error making request: {e}")
            return None


async def check_if_live() -> set:
    body = {
        "client_id": twitch_client_id,
        "client_secret": twitch_client_secret,
        "grant_type": "client_credentials",
    }
    keys = await make_request("https://id.twitch.tv/oauth2/token", body=body)
    headers = {
        "Client-ID": twitch_client_id,
        "Authorization": "Bearer " + keys["access_token"],
    }
    stream_data = await make_request(
        f"https://api.twitch.tv/helix/streams?user_login={streamer_name}",
        headers=headers,
    )
    if len(stream_data["data"].json()) == 1:
        if stream_data["data"][0]["type"] == "live":
            print(stream_data["data"][0])
            return (
                True,
                stream_data["data"][0]["game_name"],
                stream_data["data"][0]["title"],
                stream_data["data"][0]["thumbnail_url"],
            )
    else:
        return False, None, None, None


@tasks.loop(minutes=1)
async def check_twitch():
    await bot.wait_until_ready()
    while not bot.is_closed():
        is_live, game, title, thumbnail = await check_if_live()
        if is_live:
            message = f"Hey @everyone,{streamer_name} is live on Twitch! Come watch at https://twitch.tv/{streamer_name}!"
            embed = discord.Embed(
                title=title,
                description=f"Playing {game}",
                color=0x6441A5,
                timestamp=datetime.datetime.utcnow(),
            )
            embed.set_image(
                url=thumbnail.replace("{width}", "1920").replace("{height}", "1080")
            )
            embed.set_footer(
                text=f"Live since {datetime.datetime.utcnow().strftime('%H:%M:%S')}"
            )
            channel = bot.fetch_channel(1145087802141315093)
            await channel.send(message, embed=embed)


@tasks.loop(minutes=1)
async def change_activity():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await bot.change_presence(
            activity=discord.Game(
                name=random.choice(list(activities)),
                type=discord.ActivityType.playing,
                emoji=":cosmo:1146224388220391434",
            )
        )


@bot.command(name="ping", help="Returns the latency of the bot.")
async def ping(ctx):
    logger.info(f"User {ctx.author} pinged the bot.")
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


@bot.command("website", help="See more photos of Cosmo!")
async def website(ctx):
    logger.info(f"User {ctx.author} requested the website.")
    await ctx.send("https://cosmo.twizy.dev")


@bot.command(name="cosmo", help="Get a random Photo of Cosmo the Cat")
async def get_cat_photo(ctx):
    logger.info(f"User {ctx.author} requested a photo of Cosmo the Cat.")
    url = await make_request("https://api.twizy.dev/cosmo")
    if url is None:
        await ctx.send("Sorry, I couldn't find a photo of Cosmo the Cat.")
        return
    await ctx.send(str(url).strip('"'))
    await ctx.add_reaction(":cosmo:1146224388220391434")


@bot.event
async def on_ready():
    change_activity.start()
    logger.info(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "hello":
        await message.channel.send("Hello!")

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        logger.error(
            f"User {ctx.author} tried to run command {ctx.command} without the correct role."
        )
        await ctx.send("You do not have the correct role for this command.")

    elif isinstance(error, commands.errors.CommandNotFound):
        logger.error(
            f"User {ctx.author} tried to run command {ctx.command} which does not exist."
        )
        await ctx.send("Command not found.")

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        logger.error(
            f"User {ctx.author} tried to run command {ctx.command} without the correct arguments."
        )
        await ctx.send("Missing required argument.")


bot.run(discord_token, reconnect=True)
