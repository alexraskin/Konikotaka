import os
import logging
import platform

from discord import Embed
from discord import __version__ as discord_version
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Info(commands.Cog, name="Info"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(name="info", help="Get info about the bot", with_app_command=True)
    async def get_info(self, ctx):
        embed = Embed(
            title="WiseOldManBot",
            description=self.client.description,
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )
        embed.add_field(name="Node Name", value=os.getenv("NODE_NAME"))
        embed.add_field(name="Uptime", value=self.client.get_uptime())
        embed.add_field(name="Bot Version", value="1.0.0")
        embed.add_field(name="Python Version", value=platform.python_version())
        embed.add_field(name="Discord.py Version", value=discord_version)
        embed.set_footer(text=f"Made with 💖 with Discord.py")
        embed.set_thumbnail(
            url="https://i.gyazo.com/5ebe2c95171d17d96f83822de0366974.jpg"
        )
        log.info(f"User {ctx.author} requested info about the bot.")
        await ctx.send(embed=embed)

    @get_info.error
    async def get_info_error(self, ctx, error):
        log.error(f"Error getting info about the bot: {error}")
        await ctx.send("Error getting info about the bot.", delete_after=5)
    
    @commands.hybrid_command(name="ping", help="Returns the latency of the bot.", with_app_command=True)
    async def ping(self, ctx):
        log.info(f"User {ctx.author} pinged the bot.")
        await ctx.send(
            f"Pong!\n**Node: {os.getenv('NODE_NAME')}** {round(self.client.latency * 1000)}ms\n**Python Version: {platform.python_version()}**"
        )
    
    @ping.error
    async def ping_error(self, ctx, error):
        log.error(f"Error getting ping: {error}")
        await ctx.send("Error getting ping.", delete_after=5)
    
    @commands.hybrid_command(
        name="uptime", aliases=["up"], description="Shows the uptime of the bot", with_app_command=True
    )
    async def uptime(self, ctx):
        embed = Embed(
            title="Bot Uptime",
            description=f"Uptime: {self.client.get_uptime()}",
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )

        await ctx.send(embed=embed)
    
    @uptime.error
    async def uptime_error(self, ctx, error):
        log.error(f"Error getting uptime: {error}")
        await ctx.send("Error getting uptime.", delete_after=5)

async def setup(client):
    await client.add_cog(Info(client))
