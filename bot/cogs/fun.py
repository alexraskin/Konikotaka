from inspect import getsourcelines
from typing import Literal

import upsidedown
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog, name="Fun"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.hybrid_command(
        name="cosmo", help="Get a random Photo of Cosmo the Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_cat_photo(self, ctx: commands.Context) -> None:
        """
        Get a random photo of Cosmo the Cat from the twizy.dev API
        """
        async with self.client.session.get("https://api.twizy.dev/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Cosmo!")

    @commands.hybrid_command(
        name="bczs",
        help="Get a random photo of Pat and Ash's cats",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def bczs_photos(self, ctx: commands.Context) -> None:
        """
        Get a random photo of Pat and Ash's cats from the twizy.dev API
        """
        async with self.client.session.get("https://api.twizy.dev/cats") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Pat and Ash's cats!")

    @commands.hybrid_command(
        name="meme", help="Get a random meme!", with_app_command=True
    )
    @commands.guild_only()
    async def get_meme(self, ctx: commands.Context) -> None:
        """
        Get a random meme from the meme-api.com API
        """
        async with self.client.session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                meme = await response.json()
                await ctx.send(meme["url"])
            else:
                await ctx.send("Error getting meme!")

    @commands.hybrid_command(
        name="gcattalk", help="Be able to speak with G Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def gcat_talk(self, ctx: commands.Context, *, message: str) -> None:
        """
        Translate your message into G Cat's language
        """
        up_down = upsidedown.transform(message)
        await ctx.send(up_down)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.hybrid_command(name="waifu", aliases=["getwaifu"])
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(category="The category of waifu to get.")
    async def get_waifu(
        self,
        ctx: commands.Context,
        category: Literal["waifu", "neko", "shinobu", "megumin", "bully", "cuddle"],
    ) -> None:
        """
        Get a random waifu image from the waifu.pics API
        """
        response = await self.client.session.get(
            f"https://api.waifu.pics/sfw/{category}"
        )
        response = await response.json()
        if response["code"] != 200:
            return await ctx.send("Error getting waifu!")
        url = response["url"]
        await ctx.send(url)

    @commands.command(name="inspect")
    async def inspect(self, ctx, *, command_name: str):
        """
        Print a link and the source code of a command
        """
        cmd = self.client.get_command(command_name)
        if cmd is None:
            return
        module = cmd.module
        saucelines, startline = getsourcelines(cmd.callback)
        url = (
            "<https://github.com/alexraskin/WiseOldManBot/blob/main/bot"
            f'{"/".join(module.split("."))}.py#L{startline}>\n'
        )
        sauce = "".join(saucelines)
        # Little hack so triple quotes don't end discord codeblocks when printed
        sanitized = sauce.replace("`", "\u200B`")
        if len(url) + len(sanitized) > 1950:
            sanitized = sanitized[: 1950 - len(url)] + "\n[...]"
        await ctx.send(url + f"```python\n{sanitized}\n```")

    @commands.command(name="cat", description="Get a random cat image")
    async def cat(self, ctx):
        """
        Get a random cat image from the catapi
        """
        base_url = "https://cataas.com"
        response = await self.client.session.get(f"{base_url}/cat?json=true")
        if response.status != 200:
            return await ctx.send("Error getting cat!")
        response = await response.json()
        url = response["url"]
        await ctx.send(f"{base_url}{url}")


async def setup(client) -> None:
    await client.add_cog(Fun(client))
