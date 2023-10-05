from __future__ import annotations

import datetime
import itertools
import os
import platform
from typing import Optional

import pkg_resources
import pygit2
from discord import Colour, Embed, app_commands
from discord.ext import commands


class Info(commands.Cog, name="Info"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    def format_dt(self, dt: datetime.datetime, style: Optional[str] = None) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)

        if style is None:
            return f"<t:{int(dt.timestamp())}>"
        return f"<t:{int(dt.timestamp())}:{style}>"

    def format_relative(self, dt: datetime.datetime) -> str:
        return self.format_dt(dt, "R")

    def format_commit(self, commit: pygit2.Commit) -> str:
        short, _, _ = commit.message.partition("\n")
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset)
        )
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(
            commit_tz
        )

        # [`hash`](url) message (offset)
        offset = self.format_relative(commit_time.astimezone(datetime.timezone.utc))
        return f"[`{short_sha2}`](https://github.com/alexraskin/RoboTwizy/commit/{commit.hex}) {short} ({offset})"

    def get_last_commits(self, count=3):
        repo = pygit2.Repository(".git")
        commits = list(
            itertools.islice(
                repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count
            )
        )
        return "\n".join(self.format_commit(c) for c in commits)

    @commands.hybrid_command(
        name="info", help="Get info about the bot", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_info(self, ctx: commands.Context) -> None:
        version = pkg_resources.get_distribution("discord.py").version
        revision = self.get_last_commits()
        embed = Embed(
            title="RoboTwizy",
            description="Latest Changes:\n" + revision,
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
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
