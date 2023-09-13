from typing import Literal, Optional

from discord import Embed, HTTPException, app_commands
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
            self.client.log.info(f"Reload Command Executed by {ctx.author}")
        else:
            self.client.log.info(
                f"Reloaded: {str(extension).upper()} COG - Command Executed by {ctx.author}"
            )
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
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        message = await ctx.send("Syncing... 🔄")
        try:
            await self.client.tree.sync()
        except HTTPException as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send("An error occurred while syncing.", ephemeral=True)
            return
        await message.edit("Synced successfully! ✅")

    @commands.hybrid_command(name="purge", hidden=True)
    @commands.is_owner()
    @app_commands.describe(amount="The amount of messages to purge.")
    @app_commands.describe(reason="The reason for purging the messages.")
    async def purge(
        self, ctx: commands.Context, amount: int, reason: Optional[str] = None
    ) -> None:
        """
        Purges a specified amount of messages from the channel.
        """
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to delete.")
            return
        try:
            amount += 1
            await ctx.channel.purge(limit=amount, reason=reason)
            await ctx.send(f"I have purged {amount} messages.")
        except Exception as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send("An error occurred while purging messages.", ephemeral=True)
            return

    @purge.error
    async def purge_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You do not have permission to use this command.", ephemeral=True
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please specify the amount of messages to delete.", ephemeral=True
            )
        else:
            await ctx.send("An error occurred while purging messages.", ephemeral=True)


async def setup(client):
    await client.add_cog(Admin(client))
