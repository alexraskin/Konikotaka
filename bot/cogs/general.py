import logging
import os

import upsidedown
from discord import Embed, DMChannel
from discord.ext import commands, tasks
from models.db import Base
from models.users import DiscordUser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild = os.getenv("GUILD_ID")
        self.channel = self.client.get_channel(os.getenv("GENERAL_CHANNEL_ID"))

    @tasks.loop(count=1)
    async def init_database(self):
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @commands.Cog.listener()
    async def on_memeber_join(self, member):
        user = DiscordUser(
            discord_id=member.id,
            username=member.name,
            joined=member.joined_at,
        )
        async with self.client.async_session() as session:
            await session.add(user)
            try:
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()
            self.client.log.info(f"User {member} joined the server.")
        guild = member.guild
        if guild.system_channel is not None:
            embed = Embed(
                title="Welcome!",
                description=f"Welcome {member.mention} to {guild.name}!",
                color=0x00FF00,
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"User joined at {member.joined_at}")
            await guild.system_channel.send(embed=embed)

    @commands.hybrid_command(name="source", help="Get the source code for the bot.")
    async def source(self, ctx):
        self.client.log.info(f"User {ctx.author} requested the source code.")
        await ctx.send("https://github.com/alexraskin/WiseOldManBot")

    @commands.hybrid_command(
        "website", help="See more photos of Cosmo!", with_app_command=True
    )
    async def website(self, ctx):
        self.client.log.info(f"User {ctx.author} requested the website.")
        await ctx.send("View more photos of Cosmo, here -> https://cosmo.twizy.dev")

    @commands.hybrid_command(
        name="cosmo", help="Get a random Photo of Cosmo the Cat", with_app_command=True
    )
    async def get_cat_photo(self, ctx):
        self.client.log.info(f"User {ctx.author} requested a photo of Cosmo the Cat.")
        async with self.client.session.get("https://api.twizy.dev/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Cosmo!")

    @commands.hybrid_command(
        name="cats",
        help="Get a random photo of Pat and Ash's cats",
        with_app_command=True,
    )
    async def get_cats_photo(self, ctx):
        self.client.log.info(
            f"User {ctx.author} requested a photo of Pat and Ash's cats."
        )
        async with self.client.session.get("https://api.twizy.dev/cats") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Pat and Ash's cats!")

    @commands.hybrid_command(
        name="meme", help="Get a random meme!", with_app_command=True
    )
    async def get_meme(self, ctx):
        self.client.log.info(f"User {ctx.author} requested a meme.")
        async with self.client.session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                meme = await response.json()
                await ctx.send(meme["url"])
            else:
                await ctx.send("Error getting meme!")

    @commands.hybrid_command(
        name="gcattalk", help="Be able to speak with G Cat", with_app_command=True
    )
    async def gcat_talk(self, ctx, *, message: str):
        self.client.log.info(f"User {ctx.author} sent a message to G Cat.")
        up_down = upsidedown.transform(message)
        await ctx.send(up_down)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if isinstance(message.channel, DMChannel):
            self.client.log.info(f"User {message.author} sent a DM.")
            if message.content.startswith("https://discord.gg/"):
                await message.channel.send("No.")
                return
            if message.content.startswith("https://discord.com/invite/"):
                await message.channel.send("No.")
                return
            if message.content.startswith("https://discordapp.com/invite/"):
                await message.channel.send("No.")
                return
            await message.channel.send("https://media.tenor.com/UYtnaW3fLeEAAAAC/get-out-of-my-dms-squidward.gif")

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
