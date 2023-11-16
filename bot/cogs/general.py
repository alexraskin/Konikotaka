from __future__ import annotations

import os
from typing import Union
from io import BytesIO
import asyncio

import validators
from openai import AsyncOpenAI
from discord import (
    Embed,
    Interaction,
    Member,
    Message,
    PartialEmoji,
    User,
    app_commands,
    File,
    ui,
)
from discord.abc import GuildChannel
from discord.ext import commands, tasks

from .utils import gpt


class Download(ui.View):
    def __init__(self, url: str):
        super().__init__()
        self.add_item(ui.Button(label="Download your image here!", url=url))


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.guild: str = os.getenv("GUILD_ID")
        self.message_reports_channel: int = 1152498407416533053
        self.general_channel: GuildChannel = 825189935476637729
        self.openai_token: str = os.getenv("OPENAI_TOKEN")
        self.openai_gateway_url: str = os.getenv("CLOUDFLARE_AI_GATEWAY_URL")
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

    @app_commands.command(
        name="imagine", description="Generate an image using StabilityAI"
    )
    @app_commands.guild_only()
    async def imagine(self, interaction: Interaction, prompt: str) -> None:
        await interaction.response.defer()
        url = "https://image-gen.twizy.workers.dev/"

        data = {"prompt": prompt}
        spinner_frames = ["-", "\\", "|", "/"]
        frame_index = 0
        await interaction.edit_original_response(
            content=f"Generating image {spinner_frames[frame_index]}"
        )

        async def update_spinner():
            nonlocal frame_index
            while True:
                await asyncio.sleep(0.2)
                frame_index = (frame_index + 1) % len(spinner_frames)
                await interaction.edit_original_response(
                    content=f"Generating image {spinner_frames[frame_index]}"
                )

        spinner_task = asyncio.create_task(update_spinner())
        image_data = await self.client.session.post(url=url, json=data)

        if image_data.status == 200:
            self.client.log.info(f"Image generated: {image_data.status}")
            image = await image_data.read()

            with BytesIO(image) as image_binary:
                ray_id = image_data.headers["CF-RAY"].split("-")[0]
                image_file = File(fp=image_binary, filename=f"{ray_id}.png")
            spinner_task.cancel()
            content = f"Image generated - Prompt: **{prompt}**"
            await interaction.edit_original_response(
                content=content,
                attachments=[image_file],
                view=Download(url=f"https://i.konikotaka.dev/{ray_id}.png"),
            )

        else:
            spinner_task.cancel()
            self.client.log.error(
                content=f"Error generating image: {image_data.status}"
            )
            await interaction.edit_original_response("Error generating image")

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
            if message.author.nick is None:
                name = message.author.name
            else:
                name = message.author.nick
            client = AsyncOpenAI(
                api_key=self.openai_token, base_url=self.openai_gateway_url
            )
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": gpt.about_text
                        + f"when you answer someone, answer them by {name}",
                    },
                    {
                        "role": "user",
                        "content": message.content.strip(f"<@!{self.client.user.id}>"),
                    },
                ],
                model="gpt-4-1106-preview",
            )
            await message.channel.typing()
            await message.channel.send(chat_completion.choices[0].message.content)

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
