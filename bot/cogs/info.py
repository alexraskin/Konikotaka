from __future__ import annotations

import os
import platform
from typing import TYPE_CHECKING, Optional, Union

import pkg_resources
from discord import Colour, Embed, Member, User, Permissions, app_commands
from discord.ext import commands
from discord.utils import oauth_url
from utils.utils import date

if TYPE_CHECKING:
    from ..bot import Konikotaka
    from utils.context import Context


class Info(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client
        self.client_id: int = int(os.environ["CLIENT_ID"])

    @commands.hybrid_command(
        name="info", help="Get info about the bot", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_info(self, ctx: Context) -> None:
        version = pkg_resources.get_distribution("discord.py").version

        description = str(
            "My personal bot, provides some useful and fun commands. "
            "The name **Konikotaka** comes from the [The Office](https://api.konikotaka.dev/video)"
        )

        embed = Embed(
            description=description,
            timestamp=ctx.message.created_at,
        )
        embed.title = "Konikotaka"
        embed.url = "https://konikotaka.dev/"
        embed.colour = Colour.blurple()
        embed.set_author(
            name=str(self.client.owner), icon_url=self.client.owner.display_avatar.url
        )
        embed.add_field(name="Node Name", value=os.getenv("NODE_NAME", "Unknown"))
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
        embed.set_thumbnail(url=self.client.user.display_avatar.url)  # type: ignore
        await ctx.send(embed=embed)

    @commands.hybrid_command("join", with_app_command=True)
    async def join(self, ctx: Context) -> None:
        """Posts my invite to allow you to invite me"""
        perms = Permissions.none()
        perms.read_messages = True
        perms.external_emojis = True
        perms.send_messages = True
        perms.manage_roles = True
        perms.manage_channels = True
        perms.ban_members = True
        perms.kick_members = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.speak = True
        perms.connect = True
        perms.read_message_history = True
        perms.attach_files = True
        perms.add_reactions = True
        perms.use_application_commands = True
        await ctx.send(f"<{oauth_url(self.client_id, permissions=perms)}>")

    @commands.hybrid_command(name="user", aliases=["member"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def user(
        self, ctx: Context, *, user: Optional[Union[Member, User]] = None
    ) -> None:
        """Get user information"""
        user: Union[Member, User] = user or ctx.author

        show_roles = "None"
        if len(user.roles) > 1:  # type: ignore
            show_roles = ", ".join(
                [
                    f"<@&{x.id}>"
                    for x in sorted(user.roles, key=lambda x: x.position, reverse=True)  # type: ignore
                    if x.id != ctx.guild.default_role.id  # type: ignore
                ]
            )

        embed = Embed(colour=user.top_role.colour.value)  # type: ignore
        embed.title = f"{user.name}#{user.discriminator}"
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Full name", value=user)
        embed.add_field(
            name="Nickname", value=user.nick if hasattr(user, "nick") else "None"  # type: ignore
        )
        embed.add_field(name="Account created", value=date(user.created_at, ago=True))
        embed.add_field(name="Joined this server", value=date(user.joined_at, ago=True))  # type: ignore
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", aliases=["guildinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx: Context) -> None:
        """Check info about current server"""
        if ctx.invoked_subcommand is None:
            find_bots = sum(1 for member in ctx.guild.members if member.bot)  # type: ignore
            embed: Embed = Embed()
            embed.colour = Colour.blurple()
            embed.title = f"{ctx.guild.name}"  # type: ignore

            if ctx.guild.icon:  # type: ignore
                embed.set_thumbnail(url=ctx.guild.icon)
            if ctx.guild.banner:  # type: ignore
                embed.set_image(url=ctx.guild.banner.with_format("png").with_size(1024))  # type: ignore

            embed.add_field(name="Server Name", value=ctx.guild.name)  # type: ignore
            embed.add_field(name="Server ID", value=ctx.guild.id)  # type: ignore
            embed.add_field(name="Members", value=ctx.guild.member_count)  # type: ignore
            embed.add_field(name="Bots", value=find_bots)
            embed.add_field(name="Owner", value=ctx.guild.owner)  # type: ignore
            embed.add_field(name="Created", value=date(ctx.guild.created_at, ago=True))  # type: ignore
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["joined"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def joinedate(
        self, ctx: Context, *, user: Union[Member, User] = None  # type: ignore
    ) -> None:
        """Check when a user joined the current server"""
        user = user or ctx.author
        await ctx.send(
            "\n".join(
                [
                    f"**{user}** joined **{ctx.guild.name}**",  # type: ignore
                    f"{date(user.joined_at, ago=True)}",  # type: ignore
                ]
            )
        )

    @commands.hybrid_command()
    @commands.guild_only()
    @app_commands.guild_only()
    async def mods(self, ctx: Context) -> None:
        """Check which mods are online on current guild"""
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"},
        }

        for user in ctx.guild.members:  # type: ignore
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += (
                    f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
                )
        embed = Embed(title=f"Mods in {ctx.guild.name}")  # type: ignore
        embed.colour = Colour.blurple()
        embed.description = message
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="ping", help="Returns the latency of the bot.", with_app_command=True
    )
    async def ping(self, ctx: Context) -> None:
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
    async def uptime(self, ctx: Context) -> None:
        embed = Embed(
            title="Bot Uptime 🕒",
            description=f"{self.client.get_uptime}",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_thumbnail(url=self.client.user.avatar.url)  # type: ignore
        await ctx.send(embed=embed)


async def setup(client: Konikotaka) -> None:
    await client.add_cog(Info(client))
