from __future__ import annotations

import os

import validators
from discord import (
    PartialEmoji,
    app_commands,
)

from discord.ext import commands, tasks


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

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

    @property
    def display_emoji(self) -> PartialEmoji:
        return PartialEmoji(name="cosmo")

    @commands.hybrid_command("shorten_url", description="Shorten a URL")
    @app_commands.guild_only()
    @commands.guild_only()
    async def shorten_url(self, ctx: commands.Context, url: str) -> None:
        api_url: str = "https://edgesnip.dev/"
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
    async def on_command_completion(self, ctx: commands.Context) -> None:
        self.client.log.info(
            f"Executed {ctx.command.qualified_name} command in {ctx.guild.name}"
            + f"(ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})"
        )

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.errors
    ) -> None:
        errors = {
            "CheckFailure": "Fact: Only those who possess the true spirit of a samurai can access this command. You, unfortunately, do not.",
            "CommandNotFound": "This command is like a Dragon Ball - mythical and not found in this realm. Try something within your power level.",
            "MissingRequiredArgument": "Missing a required argument is like going into battle without a sword. Unwise and disgraceful. Sharpen your skills and try again.",
            "UserInputError": "In the world of anime, precision is key. Your input was as clumsy as a giant robot in a Tokyo alleyway. Correct it.",
            "CommandOnCooldown": "Like a warrior after an intense battle, this command needs time to recover. Patience is a virtue of the samurai.",
            "generic_error_message": "This is an error unknown to even the most ancient anime scrolls. Consult the Schrute Codex for guidance, or simply try again.",
        }
        self.client.log.error(error.__class__.__name__ + ": " + str(error))
        try:
            message = "Error: " + errors[error.__class__.__name__]
            await ctx.send(message)
        except AttributeError:
            await ctx.send(errors["generic_error_message"])
        except KeyError:
            await ctx.send(errors["generic_error_message"])


async def setup(client: commands.Bot) -> None:
    await client.add_cog(General(client))
