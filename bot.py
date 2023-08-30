import os
import logging
import random

import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

activitys = [
    "with Cosmo",
    ".cosmo",
]

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

async def make_request(url):
    async with aiohttp.ClientSession() as session:
        try:
          async with session.get(url) as response:
              return await response.text()
        except aiohttp.ClientError as e:
          logger.error(f'Error making request: {e}')
          return None
        
@tasks.loop(minutes=1)
async def change_activity():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await bot.change_presence(activity=discord.Game(
            name=random.choice(list(activitys)),
            type=discord.ActivityType.playing,
            emoji=":cosmo:1146224388220391434"))

@bot.command(name='ping', help='Returns the latency of the bot.')
async def ping(ctx):
    logger.info(f'User {ctx.author} pinged the bot.')
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='cosmo', help='Get a random Photo of Cosmo the Cat')
async def get_cat_photo(ctx):
  logger.info(f'User {ctx.author} requested a photo of Cosmo the Cat.')
  url = await make_request("https://api.twizy.dev/cosmo")
  if url is None:
    await ctx.send("Sorry, I couldn't find a photo of Cosmo the Cat.")
    return
  await ctx.send(url)
  await ctx.add_reaction(":cosmo:1146224388220391434")

@bot.event
async def on_ready():
    change_activity.start()
    logger.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == 'hello':
        await message.channel.send('Hello!')

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        logger.error(f'User {ctx.author} tried to run command {ctx.command} without the correct role.')
        await ctx.send('You do not have the correct role for this command.')
    
    elif isinstance(error, commands.errors.CommandNotFound):
        logger.error(f'User {ctx.author} tried to run command {ctx.command} which does not exist.')
        await ctx.send('Command not found.')
    
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        logger.error(f'User {ctx.author} tried to run command {ctx.command} without the correct arguments.')
        await ctx.send('Missing required argument.')


bot.run(TOKEN, reconnect=True)
