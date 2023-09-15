import os
import random

from discord import (DMChannel, Embed, Interaction, Member, Message,
                     app_commands)
from discord.abc import GuildChannel
from discord.ext import commands, tasks
from models.db import Base
from models.users import DiscordUser

from .utils.utils import get_year_round, progress_bar


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.guild: str = os.getenv("GUILD_ID")
        self.channel: GuildChannel = self.client.get_channel(
            os.getenv("GENERAL_CHANNEL_ID")
        )
        self.ctx_menu = app_commands.ContextMenu(
            name="React to message",
            callback=self.react,
        )
        self.client.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.client.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    @tasks.loop(count=1)
    async def init_database(self) -> None:
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def react(self, interaction: Interaction, message: Message) -> None:
        await interaction.response.send_message("Very cool message!", ephemeral=True)

    @commands.Cog.listener()
    async def on_memeber_join(self, member: Member) -> None:
        user = DiscordUser(
            discord_id=member.id,
            username=member.name,
            joined=member.joined_at,
        )
        async with self.client.async_session() as session:
            try:
                session.add(user)
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()

    @commands.hybrid_command(name="year")
    async def year(self, ctx):
        await ctx.typing()
        embed = Embed(color=0x42F56C, timestamp=ctx.message.created_at)
        embed.set_author(
            name="Year Progress",
            icon_url="https://i.gyazo.com/db74b90ebf03429e4cc9873f2990d01e.png",
        )
        embed.add_field(
            name="Progress:", value=progress_bar(get_year_round()), inline=True
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        gif_list = [
            "https://media.tenor.com/0He0W1M2LFcAAAAC/lost-gnome.gif",
            "https://media.tenor.com/UYtnaW3fLeEAAAAC/get-out-of-my-dms-squidward.gif",
            "https://media.tenor.com/derbPKeEnW4AAAAd/tony-soprano-sopranos.gif",
        ]
        if message.author == self.client.user:
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


async def setup(client) -> None:
    await client.add_cog(General(client))
