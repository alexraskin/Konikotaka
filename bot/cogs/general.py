import os
import platform

from discord import Embed
from discord.ext import commands

from models.db import Base
from models.users import DiscordUser


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot):
        """
        General commands
        :param self: Used to refer to the object itself.
        :param client: Used to pass the client object to the class.
        :return: the object of the class.
        """
        self.client = client
        self.guild = os.getenv("GUILD_ID")
        self.channel = self.client.get_channel(os.getenv("GENERAL_CHANNEL_ID"))
        Base.metadata.create_all(self.client.engine, checkfirst=True)

    @commands.Cog.listener()
    async def on_memeber_join(self, member):
        try:
            user = DiscordUser(
                discord_id=member.id,
                username=member.name,
                joined=member.joined_at,
            )
            self.client.db_session.add(user)
            self.client.db_session.commit()
        except Exception as e:
            print(e)
            self.client.db_session.rollback()
        message = self.channel.send(f"Welcome {member.mention}, to {self.guild.name}!\nI hope you enjoy your stay!")
        await message.add_reaction("👋")

    @commands.command(name="ping", help="Returns the latency of the bot.")
    async def ping(self, ctx):
        print(f"User {ctx.author} pinged the bot.")
        await ctx.send(
            f"Pong!\n**Node: {platform.node()}** {round(self.client.latency * 1000)}ms\n**Python Version: {platform.python_version()}**"
        )

    @commands.command("website", help="See more photos of Cosmo!")
    async def website(self, ctx):
        print(f"User {ctx.author} requested the website.")
        await ctx.send("View more photos of Cosmo, here -> https://cosmo.twizy.dev")

    @commands.command(name="cosmo", help="Get a random Photo of Cosmo the Cat")
    async def get_cat_photo(self, ctx):
        print(f"User {ctx.author} requested a photo of Cosmo the Cat.")
        async with self.client.session.get("https://api.twizy.dev/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Cosmo!")

    @commands.command(name="cats", help="Get a random photo of Pat and Ash's cats")
    async def get_cats_photo(self, ctx):
        print(f"User {ctx.author} requested a photo of Pat and Ash's cats.")
        async with self.client.session.get("https://api.twizy.dev/cats") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Pat and Ash's cats!")

    @commands.command(
        name="uptime", aliases=["up"], description="Shows the uptime of the bot"
    )
    async def uptime(self, ctx):
        embed = Embed(
            title="Bot Uptime",
            description=f"Uptime: {self.client.get_uptime()}",
            color=0x42F56C,
            timestamp=ctx.message.created_at,
        )

        await ctx.send(embed=embed)
    
    @commands.command(name="meme", help="Get a random meme!")
    async def get_meme(self, ctx):
        print(f"User {ctx.author} requested a meme.")
        async with self.client.session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                meme = await response.json()
                await ctx.send(meme["url"])
            else:
                await ctx.send("Error getting meme!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if 'cosmo' in message.content.lower():
            m = await message.channel.send("Meow!")
            await m.add_reaction("🐈")

        if 'pat' in message.content.lower():
            m = await message.channel.send("Pat is the best!")
            await m.add_reaction("👍")

        if 'snad' in message.content.lower():
            m = await message.channel.send("Snad is dumb!")
            await m.add_reaction("🤡")

        if 'seaira' in message.content.lower():
            m = await message.channel.send("Seaira is the queen of the world!")
            await m.add_reaction("👑")
            await m.add_reaction("🌎")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            print(
                f"User {ctx.author} tried to run command {ctx.command} without the correct role."
            )
            await ctx.send("You do not have the correct role for this command.")
        elif isinstance(error, commands.errors.CommandNotFound):
            print(
                f"User {ctx.author} tried to run command {ctx.command} which does not exist."
            )
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            print(
                f"User {ctx.author} tried to run command {ctx.command} without the correct arguments."
            )
            await ctx.send("Missing required argument.")


async def setup(client):
    await client.add_cog(General(client))
