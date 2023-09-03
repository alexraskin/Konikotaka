import os
import platform

from discord import Embed
from discord.ext import commands


class Info(commands.Cog, name="Info"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="info", help="Get info about the bot")
    async def get_info(self, ctx):
        embed = Embed(
            title="WiseOldManBot",
            description="A simple discord bot!",
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        print(self.client.user.avatar_url)
        embed.add_field(name="Bot Version", value="1.0.0", inline=False)
        embed.add_field(name="Author", value="Twizy", inline=False)
        embed.set_footer(text=f"Made with 💖 with Discord.py")
        print(f"User {ctx.author} requested info about the bot.")
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Info(client))
