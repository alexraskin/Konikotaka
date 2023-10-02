from __future__ import annotations
import os

from typing import Optional

from discord import Embed, HTTPException, Interaction, app_commands
from discord.ext import commands


class Admin(commands.Cog, name="Admin"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def reload(
        self, ctx: commands.Context, extension: Optional[str] = None
    ) -> None:
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
                description="I have reloaded all the cogs successfully ✅",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)
        else:
            await self.client.unload_extension(f"cogs.{extension}")
            await self.client.load_extension(f"cogs.{extension}")
            embed = Embed(
                title="Cog Reload 🔃",
                description=f"I have reloaded the **{str(extension).upper()}** cog successfully ✅",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)

    @commands.command(name="sync", hidden=True)
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx: commands.Context) -> None:
        """
        Sync app commands with Discord.
        """
        message = await ctx.send(content="Syncing... 🔄")
        try:
            await self.client.tree.sync()
        except HTTPException as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send("An error occurred while syncing.", ephemeral=True)
            return
        await ctx.message.delete()
        await message.edit(content="Synced successfully! ✅")

    @app_commands.command(name="add_emoji", description="Add an emoji to the server.")
    @app_commands.describe(name="The name of the emoji.")
    @app_commands.describe(url="The URL of the emoji.")
    @app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
    async def add_emoji(self, interaction: Interaction, name: str, url: str) -> None:
        """
        Adds an emoji to the server.
        """
        try:
            await interaction.response.defer()
            await interaction.guild.create_custom_emoji(name=name, image=url)
            embed = Embed(
                title="Emoji Added ✅",
                description=f"Added the emoji `:{name}:` successfully.",
                color=0x00FF00,
                timestamp=interaction.message.created_at,
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            self.client.log.error(f"Error: {e}")
            await interaction.response.send_message(
                "An error occurred while adding the emoji.", ephemeral=True
            )
            return

    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def git_revision(self, ctx: commands.Context):
        """
        Get the current git revision.
        """
        latest_revision = os.getenv('RAILWAY_GIT_COMMIT_SHA')
        if latest_revision is None:
            await ctx.send("Git revision not found.")
            return
        await ctx.send(f"Git Revision: `{latest_revision[:7]}`")

async def setup(client: commands.Bot):
    await client.add_cog(Admin(client))
