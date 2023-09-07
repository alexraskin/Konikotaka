import os
import logging
import upsidedown

from discord import Embed
from discord.ext import commands

from models.db import Base
from models.users import DiscordUser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot):
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
            self.client.log.info(f"User {member} joined the server.")
        except Exception as e:
            self.client.log.error(e)
            self.client.db_session.rollback()
        message = self.channel.send(
            f"Welcome {member.mention}, to {self.guild.name}!\nI hope you enjoy your stay!"
        )
        await message.add_reaction("👋")

    @commands.hybrid_command("website", help="See more photos of Cosmo!", with_app_command=True)
    async def website(self, ctx):
        log.info(f"User {ctx.author} requested the website.")
        await ctx.send("View more photos of Cosmo, here -> https://cosmo.twizy.dev")

    @commands.hybrid_command(name="cosmo", help="Get a random Photo of Cosmo the Cat", with_app_command=True)
    async def get_cat_photo(self, ctx):
        log.info(f"User {ctx.author} requested a photo of Cosmo the Cat.")
        async with self.client.session.get("https://api.twizy.dev/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Cosmo!")

    @commands.hybrid_command(name="cats", help="Get a random photo of Pat and Ash's cats", with_app_command=True)
    async def get_cats_photo(self, ctx):
        log.info(f"User {ctx.author} requested a photo of Pat and Ash's cats.")
        async with self.client.session.get("https://api.twizy.dev/cats") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Pat and Ash's cats!")

    @commands.hybrid_command(name="meme", help="Get a random meme!", with_app_command=True)
    async def get_meme(self, ctx):
        log.info(f"User {ctx.author} requested a meme.")
        async with self.client.session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                meme = await response.json()
                await ctx.send(meme["url"])
            else:
                await ctx.send("Error getting meme!")

    @commands.hybrid_command(name="gcattalk", help="Be able to speak with G Cat", with_app_command=True)
    async def gcat_talk(self, ctx, *, message: str):
        log.info(f"User {ctx.author} sent a message to G Cat.")
        up_down = upsidedown.transform(message)
        await ctx.send(up_down)
    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} without the correct role."
            )
            await ctx.send("You do not have the correct role for this command.")
        elif isinstance(error, commands.errors.CommandNotFound):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} which does not exist."
            )
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            self.client.log.error(
                f"User {ctx.author} tried to run command {ctx.command} without the correct arguments."
            )
            await ctx.send("Missing required argument.")


async def setup(client):
    await client.add_cog(General(client))
