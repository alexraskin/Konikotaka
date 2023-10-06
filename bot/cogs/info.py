from __future__ import annotations

import os
import platform

import pkg_resources
from discord import Colour, Embed, app_commands
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
        version = pkg_resources.get_distribution("discord.py").version
        embed = Embed(
            description=self.client.description,
            timestamp=ctx.message.created_at,
        )
        embed.title = "RoboTwizy"
        embed.url = "https://status.twizy.dev/"
        embed.colour = Colour.blurple()
        embed.set_author(
            name=str(self.client.owner), icon_url=self.client.owner.display_avatar.url
        )
        embed.add_field(name="Node Name", value=os.getenv("NODE_NAME"))
        embed.add_field(
            name="Process",
            value=f"{self.client.memory_usage:.2f} MiB\n{self.client.cpu_usage:.2f}% CPU",
        )
        embed.add_field(name="Uptime", value=self.client.get_uptime)
        embed.add_field(name="Bot Version", value=self.client.version)
        embed.add_field(name="Git Revision", value=self.client.git_revision)
        embed.add_field(name="Python Version", value=platform.python_version())
        embed.set_footer(
            text=f"Made with discord.py v{version}",
            icon_url="http://i.imgur.com/5BFecvA.png",
        )
        embed.set_thumbnail(url=self.client.logo_url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="ping", help="Returns the latency of the bot.", with_app_command=True
    )
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send(
            f"Pong! 🏓\nNode: **{os.getenv('NODE_NAME')}**\nLatency: **{round(self.client.get_bot_latency)}ms**\nPython Version: **{platform.python_version()}**"
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
            title="Bot Uptime 🕒",
            description=f"Uptime: {self.client.get_uptime} 🕒",
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )
        embed.set_thumbnail(url=self.client.logo_url)
        await ctx.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Info(client))
