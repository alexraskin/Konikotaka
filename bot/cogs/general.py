import os
import platform

from discord import Embed
from discord.ext import commands


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot):
        """
        General commands
        :param self: Used to refer to the object itself.
        :param client: Used to pass the client object to the class.
        :return: the object of the class.
        """
        self.client = client
        self.streamer_name = "pr3daturd574"
        self.body = {
            "client_id": os.getenv("TWITCH_CLIENT_ID"),
            "client_secret": os.getenv("TWITCH_CLIENT_SECRET"),
            "grant_type": "client_credentials",
        }

    async def check_if_live(self) -> set:
        async with self.client.session.post(
            "https://id.twitch.tv/oauth2/token", data=self.body
        ) as response:
            keys = await response.json()
            headers = {
                "Client-ID": self.client.config.twitch_client_id,
                "Authorization": "Bearer " + keys["access_token"],
            }
        async with self.client.session.get(
            f"https://api.twitch.tv/helix/streams?user_login={self.streamer_name}",
            headers=headers,
        ) as response:
            stream_data = await response.json()
            if len(stream_data["data"]) == 1:
                if stream_data["data"][0]["type"] == "live":
                    return (
                        True,
                        stream_data["data"][0]["game_name"],
                        stream_data["data"][0]["title"],
                        stream_data["data"][0]["thumbnail_url"],
                    )
            else:
                return False, None, None, None

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

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
            await ctx.send("Command not found.")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            print(
                f"User {ctx.author} tried to run command {ctx.command} without the correct arguments."
            )
            await ctx.send("Missing required argument.")


async def setup(client):
    """
    The setup function is used to register the commands that will be used in the bot.
    This function is run when you load a cog, and it allows you to use commands in your cogs.

    :param client: Used to pass in the client object.
    :return: a dictionary that contains the following keys:.
    """
    await client.add_cog(General(client))
