import os
import random

from discord import (
    DMChannel,
    Embed,
    Interaction,
    Member,
    Message,
    app_commands,
    PartialEmoji,
    Guild,
)
from discord.abc import GuildChannel
from discord.ext import commands, tasks
from models.db import Base
from models.users import DiscordUser


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.guild: str = os.getenv("GUILD_ID")
        self.message_reports_channel: int = 1152498407416533053
        self.general_channel: GuildChannel = 825189935476637729
        self.message_report_ctx: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Report Message",
            callback=self.report,
        )
        self.client.tree.add_command(self.message_report_ctx)
        self.warn_user_ctx: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Warn User",
            callback=self.warn,
        )

    async def cog_unload(self) -> None:
        self.client.tree.remove_command(
            self.message_report_ctx.name, type=self.message_report_ctx.type
        )
        self.client.tree.remove_command(
            self.warn_user_ctx.name, type=self.warn_user_ctx.type
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.init_database.start()
        self.health_check.start()

    @tasks.loop(hours=1)
    async def health_check(self) -> None:
        check = await self.client.session.get(os.getenv("HEALTHCHECK_URL"))
        if check.status == 200:
            self.client.log.info("Health check successful.")
        else:
            self.client.log.error("Health check failed.")

    @tasks.loop(count=1)
    async def init_database(self) -> None:
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def warn(self, interaction: Interaction, user: Member) -> None:
        await interaction.response.defer(ephemeral=True)
        embed: Embed = Embed(
            title="User Warned 🚨",
            color=0x2ECC71,
            timestamp=interaction.created_at,
        )
        embed.add_field(name="User:", value=user.mention, inline=False)
        embed.add_field(
            name="Moderator:",
            value=f"{interaction.user.mention} ({interaction.user})",
            inline=False,
        )
        embed.set_thumbnail(url=self.client.logo_url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def report(self, interaction: Interaction, message: Message) -> None:
        await interaction.response.defer(ephemeral=True)
        channel = self.client.get_channel(self.message_reports_channel)
        embed = Embed(
            title="Message Report",
            color=0x2ECC71,
            timestamp=message.created_at,
        )
        embed.add_field(name="Message:", value=message.content, inline=False)
        embed.add_field(
            name="Author:",
            value=f"{message.author.mention} ({message.author})",
            inline=False,
        )
        embed.add_field(
            name="Channel:",
            value=f"{message.channel.mention} ({message.channel})",
            inline=False,
        )
        embed.add_field(
            name="Jump:",
            value=f"[Click here]({message.jump_url})",
            inline=False,
        )
        embed.set_thumbnail(url=self.client.logo_url)
        await channel.send(embed=embed)
        await interaction.followup.send("Message reported", ephemeral=True)

    @property
    def display_emoji(self) -> PartialEmoji:
        return PartialEmoji(name="cosmo")

    @commands.Cog.listener()
    async def on_memeber_join(self, member: Member) -> None:
        if member.guild.id != self.cosmo_guild:
            return
        user = DiscordUser(
            discord_id=member.id,
            username=member.name,
            joined=member.joined_at,
            guild_id=member.guild.id,
        )
        async with self.client.async_session() as session:
            try:
                session.add(user)
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        if member.guild.id != self.cosmo_guild:
            return
        async with self.client.async_session() as session:
            try:
                user = await session.query(DiscordUser, member.id)
                if user is None:
                    return
                session.delete(user)
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.guild.id != self.cosmo_guild:
            return
        async with self.client.async_session() as session:
            try:
                user = await session.query(DiscordUser, before.id)
                if user is None:
                    return
                user.username = after.name
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()

    @commands.Cog.listener()
    async def on_member_ban(self, guild: Guild, user: Member) -> None:
        if guild.id != self.cosmo_guild:
            return
        async with self.client.async_session() as session:
            try:
                user = await session.query(DiscordUser, user.id)
                if user is None:
                    return
                session.delete(user)
                await session.flush()
                await session.commit()
                embed = Embed(
                    title="User Banned 🚨",
                    color=0x2ECC71,
                )
                embed.add_field(name="User:", value=user.mention, inline=False)
                channel: GuildChannel = self.client.get_channel(self.general_channel)
                await channel.send(embed=embed)
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        gif_list: list = [
            "https://media.tenor.com/0He0W1M2LFcAAAAC/lost-gnome.gif",
            "https://media.tenor.com/UYtnaW3fLeEAAAAC/get-out-of-my-dms-squidward.gif",
            "https://media.tenor.com/derbPKeEnW4AAAAd/tony-soprano-sopranos.gif",
        ]
        if message.author == self.client.user:
            return

        if message.content.__contains__("?gothgf"):
            await message.channel.send(
                "https://i.gyazo.com/83858c9e4b22334ee8b514fb232b2f4a.jpg"
            )
            return

        if message.content.__contains__("?servericon"):
            await message.channel.send(
                "https://media.discordapp.net/attachments/1064936966136795257/1151551567493865613/alexraskin.jpg?width=589&height=589"
            )
            return

        if message.content.__contains__("?snadcaught"):
            await message.channel.send(
                "https://i.imgur.com/N6bI2DQ.png <@!253223272328462338> <a:JBF_actingSusNotMeOwO:1145086854467686501>"
            )
            return

        if message.content.__contains__("?twizy"):
            await message.channel.send("https://twizy.dev/")
            return

        if isinstance(message.channel, DMChannel):
            self.client.log.info(f"User {message.author} sent a DM.")
            if message.content.startswith("https://discord.gg/"):
                await message.channel.send("No.")
                return
            if message.content.startswith("https://discord.com/invite/"):
                await message.channel.send("No.")
                return
            if message.content.startswith("https://discordapp.com/invite/"):
                await message.channel.send("No.")
                return
            await message.channel.send(random.choice(list(gif_list)))

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context) -> None:
        self.client.log.info(
            f"Executed {ctx.command.qualified_name} command in {ctx.guild.name}"
            + f"(ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})"
        )

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.errors
    ) -> None:
        if isinstance(error, commands.errors.CheckFailure):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} without the correct role."
            )
            await ctx.send("You do not have the correct role for this command.")
        elif isinstance(error, commands.errors.CommandNotFound):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} which does not exist."
            )
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} without the correct arguments."
            )
            await ctx.send("Missing required argument.")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(General(client))
