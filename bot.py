import datetime
import logging
import os
import random

import aiohttp
import discord
from discord import AllowedMentions
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
    "RuneLite",
    ".help",
    "Fishing in Lumbridge",
    "with the Grand Exchange",
    "Smite",
    "Overwatch 2",
]

help_command = commands.DefaultHelpCommand(
    no_category="Commands",
)

bot = commands.Bot(
    command_prefix=".",
    intents=discord.Intents.all(),
    help_command=help_command,
    description="The Wizard of Cosmo",
    allowed_mentions=AllowedMentions(everyone=True, users=True, roles=True),
)


async def check_if_live() -> set:
    body = {
        "client_id": twitch_client_id,
        "client_secret": twitch_client_secret,
        "grant_type": "client_credentials",
    }
    logging.info("Getting Twitch API keys.")
    async with aiohttp.ClientSession() as session:
        async with session.post("https://id.twitch.tv/oauth2/token", data=body) as response:
            keys = await response.json()
            headers = {
                "Client-ID": twitch_client_id,
                "Authorization": "Bearer " + keys["access_token"],
            }
            async with session.get(
                f"https://api.twitch.tv/helix/streams?user_login={streamer_name}",
                headers=headers,
            ) as response:
                stream_data = await response.json()
                if len(stream_data["data"]) > 0:
                    if stream_data["data"][0]["type"] == "live":
                        print(stream_data["data"][0])
                        return (
                            True,
                            stream_data["data"][0]["game_name"],
                            stream_data["data"][0]["title"],
                            stream_data["data"][0]["thumbnail_url"],
                        )
                else:
                    logger.info(f"{streamer_name} is not live.")
                    return False, None, None, None


@tasks.loop(minutes=1)
async def check_twitch():
      live = await check_if_live()
      if live[0]:
          message = f"Hey @everyone, {streamer_name} is live on Twitch! Come watch at https://twitch.tv/{streamer_name}!"
          embed = discord.Embed(
              title=live[2],
              description=f"Playing {live[1]}",
              color=0x6441A5,
              timestamp=datetime.datetime.utcnow(),
          )
          embed.set_image(
              url=live[3].replace("{width}", "1920").replace("{height}", "1080")
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
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.twizy.dev/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of!")


@bot.event
async def on_ready():
    change_activity.start()
    check_twitch.start()
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
