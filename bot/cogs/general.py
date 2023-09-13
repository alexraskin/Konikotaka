import os
import random

from discord import DMChannel, Member, Message
from discord.abc import GuildChannel
from discord.ext import commands, tasks
from models.db import Base
from models.users import DiscordUser


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.guild: str = os.getenv("GUILD_ID")
        self.channel: GuildChannel = self.client.get_channel(
            os.getenv("GENERAL_CHANNEL_ID")
        )

    @tasks.loop(count=1)
    async def init_database(self) -> None:
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

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

    @commands.hybrid_command(name="source", help="Get the source code for the bot.")
    async def source(self, ctx: commands.Context) -> None:
        self.client.log.info(f"User {ctx.author} requested the source code.")
        await ctx.send("https://github.com/alexraskin/WiseOldManBot")

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
        """
        The on_command_completion function tracks the commands that are executed in each server.

        :param ctx: Used to access the context of the command.
        :return: a string of the executed command.
        """
        full_command_name = ctx.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        self.client.log.info(
            f"Executed {executed_command} command in {ctx.guild.name}"
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
