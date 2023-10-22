from __future__ import annotations

import os
import platform

import pkg_resources
from discord import Colour, Embed, Member, app_commands
from discord.ext import commands

from .utils.utils import date


class Info(commands.Cog, name="Info"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.invite_url = "https://discord.com/api/oauth2/authorize?client_id=482960108117295105&permissions=10415295163479&scope=bot"

    @commands.hybrid_command(
        name="info", help="Get info about the bot", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_info(self, ctx: commands.Context) -> None:
        version = pkg_resources.get_distribution("discord.py").version

        description = str(
            "My personal bot, provides some useful commands and some fun commands. "
            "The name Konikotaka comes from the TV Show - [The Office](https://youtu.be/Qr2LQILdXD0)"
          )

        embed = Embed(
            description=description,
            timestamp=ctx.message.created_at,
        )
        embed.title = "Konikotaka"
        embed.url = self.invite_url
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
        embed.add_field(name="Latency", value=f"{self.client.get_bot_latency}ms")
        embed.add_field(name="Bot Version", value=self.client.version)
        embed.add_field(name="Git Revision", value=self.client.git_revision)
        embed.add_field(name="Python Version", value=platform.python_version())
        embed.set_footer(
            text=f"Made with discord.py v{version}",
            icon_url="http://i.imgur.com/5BFecvA.png",
        )
        embed.set_thumbnail(url=self.client.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command("invite", with_app_command=True)
    async def invite(self, ctx: commands.Context) -> None:
        """Invite me to your server!"""
        await ctx.send(self.invite_url)

    @commands.hybrid_command(name="user", aliases=["member"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def user(self, ctx: commands.Context, *, user: Member = None):
        """Get user information"""
        user = user or ctx.author

        show_roles = "None"
        if len(user.roles) > 1:
            show_roles = ", ".join(
                [
                    f"<@&{x.id}>"
                    for x in sorted(user.roles, key=lambda x: x.position, reverse=True)
                    if x.id != ctx.guild.default_role.id
                ]
            )

        embed = Embed(colour=user.top_role.colour.value)
        embed.title = f"{user.name}#{user.discriminator}"
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Full name", value=user)
        embed.add_field(
            name="Nickname", value=user.nick if hasattr(user, "nick") else "None"
        )
        embed.add_field(name="Account created", value=date(user.created_at, ago=True))
        embed.add_field(name="Joined this server", value=date(user.joined_at, ago=True))
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", aliases=["guildinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        """Check info about current server"""
        if ctx.invoked_subcommand is None:
            find_bots = sum(1 for member in ctx.guild.members if member.bot)

            embed = Embed()
            embed.colour = Colour.blurple()
            embed.title = f"{ctx.guild.name}"

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner.with_format("png").with_size(1024))

            embed.add_field(name="Server Name", value=ctx.guild.name)
            embed.add_field(name="Server ID", value=ctx.guild.id)
            embed.add_field(name="Members", value=ctx.guild.member_count)
            embed.add_field(name="Bots", value=find_bots)
            embed.add_field(name="Owner", value=ctx.guild.owner)
            embed.add_field(name="Created", value=date(ctx.guild.created_at, ago=True))
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["joined"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def joinedate(self, ctx: commands.Context, *, user: Member = None):
        """Check when a user joined the current server"""
        user = user or ctx.author
        await ctx.send(
            "\n".join(
                [
                    f"**{user}** joined **{ctx.guild.name}**",
                    f"{date(user.joined_at, ago=True)}",
                ]
            )
        )

    @commands.hybrid_command()
    @commands.guild_only()
    @app_commands.guild_only()
    async def mods(self, ctx: commands.Context):
        """Check which mods are online on current guild"""
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"},
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += (
                    f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
                )
        embed = Embed(title=f"Mods in {ctx.guild.name}")
        embed.colour = Colour.blurple()
        embed.description = message
        embed.set_footer(text=f"Requested by {ctx.author}")
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
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_thumbnail(url=self.client.logo_url)
        await ctx.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Info(client))
