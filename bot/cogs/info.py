import os
import platform

from discord import Embed
from discord import __version__ as discord_version
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog, name="Info"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.hybrid_command(
        name="info", help="Get info about the bot", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_info(self, ctx: commands.Context) -> None:
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
        self.client.log.info(f"User {ctx.author} requested info about the bot.")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="ping", help="Returns the latency of the bot.", with_app_command=True
    )
    async def ping(self, ctx: commands.Context) -> None:
        self.client.log.info(f"User {ctx.author} pinged the bot.")
        await ctx.send(
            f"Pong!\n**Node: {os.getenv('NODE_NAME')}** {round(self.client.latency * 1000)}ms\n**Python Version: {platform.python_version()}**"
        )

    @commands.hybrid_command(
        name="uptime",
        aliases=["up"],
        description="Shows the uptime of the bot",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def uptime(self, ctx: commands.Context) -> None:
        embed = Embed(
            title="Bot Uptime",
            description=f"Uptime: {self.client.get_uptime()}",
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Info(client))
