import platform

from discord import Embed
from discord import __version__ as discord_version
from discord.ext import commands


class Info(commands.Cog, name="Info"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="info", help="Get info about the bot")
    async def get_info(self, ctx):
        embed = Embed(
            title="WiseOldManBot",
            description=self.client.description,
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )
        embed.add_field(name="Node Name", value=platform.node())
        embed.add_field(name="Uptime", value=self.client.get_uptime())
        embed.add_field(name="Bot Version", value="1.0.0")
        embed.add_field(name="Python Version", value=platform.python_version())
        embed.add_field(name="Discord.py Version", value=discord_version)
        embed.set_footer(text=f"Made with 💖 with Discord.py")
        embed.set_thumbnail(
            url="https://i.gyazo.com/5ebe2c95171d17d96f83822de0366974.jpg"
        )
        print(f"User {ctx.author} requested info about the bot.")
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Info(client))
