from __future__ import annotations

import os
from typing import Union

import validators
from discord import (
    Embed,
    Interaction,
    Member,
    Message,
    PartialEmoji,
    User,
    app_commands,
)
from discord.abc import GuildChannel
from discord.ext import commands, tasks

from .utils import gpt


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.guild: str = os.getenv("GUILD_ID")
        self.message_reports_channel: int = 1152498407416533053
        self.general_channel: GuildChannel = 825189935476637729
        self.cloudflare_token: str = os.getenv("CLOUDFLARE_TOKEN")
        self.cloudflare_url: str = os.getenv("CLOUDFLARE_URL")
        self.message_report_ctx: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Report Message",
            callback=self.report,
        )
        self.warn_user_ctx: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Warn User",
            callback=self.warn,
        )
        self.client.tree.add_command(self.message_report_ctx)
        self.client.tree.add_command(self.warn_user_ctx)

    async def cog_unload(self) -> None:
        self.client.tree.remove_command(
            self.message_report_ctx.name, type=self.message_report_ctx.type
        )
        self.client.tree.remove_command(
            self.warn_user_ctx.name, type=self.warn_user_ctx.type
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.health_check.start()

    @tasks.loop(hours=1)
    async def health_check(self) -> None:
        check = await self.client.session.get(os.getenv("HEALTHCHECK_URL"))
        if check.status == 200:
            self.client.log.info("Health check successful.")
        else:
            self.client.log.error("Health check failed.")

    async def warn(self, interaction: Interaction, user: Union[Member, User]) -> None:
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

    @commands.hybrid_command("shorten_url", description="Shorten a URL")
    @app_commands.guild_only()
    @commands.guild_only()
    async def shorten_url(self, ctx: commands.Context, url: str) -> None:
        api_url = "https://edgesnip.dev/"
        validate_url = validators.url(url)
        if validate_url:
            data = {"url": url}
            short_url = await self.client.session.post(url=api_url, json=data)
            if short_url.status == 200:
                short_url = await short_url.json()
                await ctx.send(f"Shortened URL: {short_url['url']}")
            else:
                await ctx.send("Error shortening URL")
        else:
            await ctx.send("Invalid URL")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.client.user:
            return

        if self.client.user in message.mentions:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.cloudflare_token,
            }
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": gpt.about_text
                        + f"when you answer someone, answer them by {message.author.name}",
                    },
                    {
                        "role": "user",
                        "content": message.content.strip(f"<@!{self.client.user.id}>"),
                    },
                ]
            }
            await message.channel.typing()
            response = await self.client.session.post(
                url=self.cloudflare_url, headers=headers, json=payload
            )
            if response.status == 200:
                json_response = await response.json()
                await message.channel.send(json_response["result"]["response"])
            else:
                await message.channel.send("An error occurred, this has been logged.")

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
        message = "oopsie whoopsie UwU you made a fucky wucky"
        if isinstance(error, commands.errors.CheckFailure):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} without the correct role."
            )
            await ctx.send(message)
        elif isinstance(error, commands.errors.CommandNotFound):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} which does not exist."
            )
            await ctx.send("Command not found! UwU")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} without the correct arguments."
            )
            await ctx.send("Missing Required Arguments")
        else:
            self.client.log.error(f"Something happened! {error}")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(General(client))
