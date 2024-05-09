from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import Colour, Embed, Emoji, Guild, HTTPException, app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from utils.context import Context

    from ..bot import Konikotaka


class Admin(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: Context, extension: Optional[str] = None) -> None:
        """
        Reloads all the cogs or a specified cog.
        """
        if extension is None:
            for cog in self.client.extensions.copy():
                try:
                    await self.client.unload_extension(cog)
                    await self.client.load_extension(cog)
                except Exception as e:
                    self.client.log.error(f"Error: {e}")
                    await ctx.send(
                        f"An error occurred while reloading the {cog} cog.",
                        ephemeral=True,
                    )
                    return
            embed = Embed(
                title="Cog Reload 🔃",
                description="Reloaded all the cogs successfully ✅",
                timestamp=ctx.message.created_at,
            )
            embed.colour = Colour.blurple()
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)
        else:
            await self.client.unload_extension(f"cogs.{extension}")
            await self.client.load_extension(f"cogs.{extension}")
            embed = Embed(
                title="Cog Reload 🔃",
                description=f"Reloaded **{str(extension).upper()}** cog successfully ✅",
                timestamp=ctx.message.created_at,
            )
            embed.colour = Colour.blurple()
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)

    @commands.command(name="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: Context) -> None:
        """
        Sync app commands with Discord.
        """
        await ctx.message.delete()
        message = await ctx.send(content="Syncing... 🔄")
        try:
            await self.client.tree.sync()
        except HTTPException as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send("An error occurred while syncing.", ephemeral=True)
            return
        sync_message = await message.edit(content="Synced successfully! ✅")
        await sync_message.delete(delay=5)

    @commands.hybrid_command(
        name="add_emoji", description="Add an emoji to the server."
    )
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(emoji="The emoji to add")
    @app_commands.describe(name="The name of the emoji")
    @app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
    async def add_emoji(
        self, ctx: Context, emoji: Emoji, name: Optional[str] = None
    ) -> None:
        """
        Adds an emoji to the server.
        """
        if name is None:
            name = emoji.name
        guild: Guild = ctx.guild
        try:
            res = await self.client.session.get(emoji.url)
            if res.status == 200:
                image_data = await res.read()
                new_emoji = await guild.create_custom_emoji(name=name, image=image_data)
                embed = Embed()
                embed.title = "Emoji Added"
                embed.description = f"Added {new_emoji} to the server."
                embed.colour = Colour.blurple()
                embed.set_thumbnail(url=new_emoji.url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    "The emoji image could not be downloaded.", ephemeral=True
                )
                return
        except Exception as e:
            await ctx.send(
                f"An error occurred while adding the emoji: {e}", ephemeral=True
            )
            return

    @commands.command(name="git", aliases=["gr"], hidden=True)
    @commands.guild_only()
    async def git_revision(self, ctx: Context) -> None:
        """
        Get the current git revision.
        """
        await ctx.send(f"Git Revision: {self.client.git_revision}")


async def setup(client: Konikotaka) -> None:
    await client.add_cog(Admin(client))
