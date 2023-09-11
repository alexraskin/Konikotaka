import logging
from typing import Literal, Optional

from discord import Embed, Object, HTTPException
from discord.ext import commands


class Admin(commands.Cog, name="Admin"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(name="reload", hidden=True, with_app_command=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension: Optional[str] = None) -> None:
        if extension is None:
            for cog in self.client.extensions.copy():
                await self.client.unload_extension(cog)
                await self.client.load_extension(cog)
            self.client.log.info(f"Reload Command Executed by {ctx.author}")
            embed = Embed(
                title="Cog Reload 🔃",
                description="I have reloaded all the cogs successfully ✅",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)
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
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await self.client.tree.sync(guild=ctx.guild)

            elif spec == "*":
                self.client.tree.copy_global_to(guild=ctx.guild)
                synced = await self.client.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.client.tree.clear_commands(guild=ctx.guild)
                await self.client.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.client.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await self.client.tree.sync(guild=guild)
            except HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.hybrid_command(name="purge", hidden=True)
    @commands.is_owner()
    async def purge(self, ctx: commands.Context, amount: int, reason: Optional[str] = None):
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to delete.")
            return
        try:
            amount += 1
            await ctx.channel.purge(limit=amount, reason=reason)
        except Exception as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send("An error occurred while purging messages.", ephemeral=True)
            return
        message = await ctx.send("I have purged those messages for you.")
        await message.delete(delay=3)

    @purge.error
    async def purge_error(self, ctx: commands.Context, error):
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
