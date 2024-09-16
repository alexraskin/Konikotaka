from __future__ import annotations

import asyncio
import random
import urllib.parse
from typing import TYPE_CHECKING, Literal, Optional, Union

import upsidedown
from async_foaas import Fuck
from discord import Colour, Embed, Member, User, app_commands
from discord.ext import commands
from models.users import DiscordUser
from sqlalchemy.future import select
from utils.utils import get_year_round, progress_bar

if TYPE_CHECKING:
    from utils.context import Context

    from ..bot import Konikotaka


class Fun(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client
        self.fuck: Fuck = Fuck()

    @commands.hybrid_command(
        name="cosmo", help="Get a random Photo of Cosmo the Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def cosmo_photo(self, ctx: Context) -> None:
        """
        Get a random photo of my cat Cosmo!
        """
        async with self.client.session.get("https://api.00z.sh/v1/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.reply(content=photo["photoUrl"])
            else:
                self.client.log.error(
                    f"An error occurred getting photo of Cosmo: {response.status}"
                )
                await ctx.reply("Error getting photo of Cosmo!", ephemeral=True)

    @commands.hybrid_command(name="fuckoff", help="Tell Someone to Fuck Off")
    @commands.guild_only()
    @app_commands.guild_only()
    async def fuck_off(self, ctx: Context, user: Union[Member, User]):
        _fuck = await self.fuck.random(name=user.mention, from_=ctx.author.name).json
        await ctx.send(_fuck["message"])

    @commands.hybrid_command(
        name="bczs",
        help="Get a random photo of Pat and Ash's cats",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def bczs_photos(self, ctx: Context):
        """
        Get a random photo of Pat and Ash's cats from the twizy.dev API
        """
        self.client.log.info("Getting photo of Pat and Ash's cats")
        async with self.client.session.get("https://api.00z.sh/v1/bczs") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.reply(content=photo["photoUrl"])
            else:
                self.client.log.error(
                    f"An error occurred getting photo of Pat and Ash's cats: {response.status}"
                )
                await ctx.reply(
                    "Error getting photo of Pat and Ash's cats!", ephemeral=True
                )

    @commands.hybrid_command(
        name="meme", help="Get a random meme!", with_app_command=True
    )
    @commands.guild_only()
    async def get_meme(self, ctx: Context):
        """
        Get a random meme from the meme-api.com API
        """
        async with self.client.session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                meme = await response.json()
                await ctx.reply(meme["url"])
            else:
                await ctx.reply("Error getting meme!", ephemeral=True)

    @commands.hybrid_command(
        name="gcattalk", help="Be able to speak with G Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def gcat_talk(self, ctx: Context, *, message: str):
        """
        Translate your message into G Cat's language
        """
        up_down = upsidedown.transform(message)
        await ctx.reply(up_down)

    @commands.hybrid_command(name="waifu", aliases=["getwaifu"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_waifu(
        self,
        ctx: Context,
        category: Literal["waifu", "neko", "shinobu", "megumin", "bully", "cuddle"],
    ):
        """
        Get a random waifu image from the waifu API
        """
        response = await self.client.session.get(
            f"https://api.waifu.pics/sfw/{category}"
        )
        if response.status == 200:
            waifu = await response.json()
            await ctx.reply(waifu["url"])
        else:
            await ctx.reply("Error getting waifu!", ephemeral=True)

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name="cat", description="Get a random cat image")
    async def cat(self, ctx: Context):
        """
        Get a random cat image from the catapi
        """
        base_url = "https://cataas.com"
        response = await self.client.session.get(f"{base_url}/cat?json=true")
        if response.status != 200:
            return await ctx.reply("Error getting cat!", ephemeral=True)
        response = await response.json()
        id = response["_id"]
        await ctx.reply(f"{base_url}/cat/{id}")

    @commands.hybrid_command(name="roll", description="Roll a dice with NdN")
    @commands.guild_only()
    @app_commands.guild_only()
    async def roll(self, ctx: Context, dice: str):
        """
        Roll a dice
        """
        dice = dice.strip()
        try:
            rolls, limit = map(int, dice.split("d"))
        except Exception:
            return await ctx.send("Format has to be in NdN!\n(e.g. 1d20)")
        result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
        embed = Embed(
            title="🎲 Roll Dice",
            description=f"{ctx.author.name} threw a **{result}** ({rolls}-{limit})",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball a question")
    @commands.guild_only()
    @app_commands.guild_only()
    async def eight_ball(self, ctx: Context, *, question: str):
        """
        Ask the magic 8ball a question
        """
        data = await self.client.session.get("https://nekos.life/api/v2/8ball")
        json_data = await data.json()
        embed = Embed(
            title="🎱 Meowgical 8ball",
            description=f"Question: {question}\n\nAnswer: {json_data['response']}",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_image(url=json_data["url"])
        embed.set_footer(text=f"{ctx.author}")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="fact", description="Get a random fact")
    @commands.guild_only()
    @app_commands.guild_only()
    async def fact(self, ctx: Context):
        """
        Get a random fact
        """
        data = await self.client.session.get("https://nekos.life/api/v2/fact")
        json_data = await data.json()
        embed = Embed(
            title="📖 Fact",
            description=f"{json_data['fact']}",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="reverse", description="Reverse a string")
    @commands.guild_only()
    @app_commands.guild_only()
    async def reverse(self, ctx: Context, string: str):
        """
        Reverse a string
        """
        await ctx.reply(string[::-1])

    @commands.hybrid_command(name="say", description="Make the bot say something")
    @commands.guild_only()
    @app_commands.guild_only()
    async def say(self, ctx: Context, message: str):
        """
        Make the bot say something
        """
        await ctx.send(message)

    @commands.hybrid_command(
        name="embed", description="Make the bot say something in an embed"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def _embed(self, ctx: Context, message: str):
        """
        Make the bot say something in an embed
        """
        embed = Embed(
            title="📝 Embed",
            description=f"{message}",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hug", description="Hug someone")
    @commands.guild_only()
    @app_commands.guild_only()
    async def hug(self, ctx: Context, member: Union[Member, User]):
        """
        Hug someone
        """
        data = await self.client.session.get("https://nekos.life/api/v2/img/hug")
        json_data = await data.json()
        embed = Embed(
            title="🫂 Hug",
            description=f"{ctx.author.mention} hugged {member.mention} 😊",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_image(url=json_data["url"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slap", description="Slap someone")
    @commands.guild_only()
    @app_commands.guild_only()
    async def slap(self, ctx: Context, member: Union[Member, User]):
        """
        Slap someone
        """
        data = await self.client.session.get("https://nekos.life/api/v2/img/slap")
        json_data = await data.json()
        embed = Embed(
            title="👊 Slap",
            description=f"{ctx.author.mention} slapped {member.mention} 😡",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_image(url=json_data["url"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kiss", description="Kiss someone")
    @commands.guild_only()
    @app_commands.guild_only()
    async def kiss(self, ctx: Context, member: Union[Member, User]):
        """
        Kiss someone
        """
        data = await self.client.session.get("https://nekos.life/api/v2/img/kiss")
        json_data = await data.json()
        embed = Embed(
            title="💋 Kiss",
            description=f"{ctx.author.mention} kissed {member.mention} 😘",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_image(url=json_data["url"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="pat", description="Pat someone")
    @commands.guild_only()
    @app_commands.guild_only()
    async def pat(self, ctx: Context, member: Union[Member, User]):
        """
        Pat someone
        """
        data = await self.client.session.get("https://nekos.life/api/v2/img/pat")
        json_data = await data.json()
        embed = Embed(
            title="👋 Pat",
            description=f"{ctx.author.mention} patted {member.mention} 😊",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_image(url=json_data["url"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="textcat")
    @commands.guild_only()
    @app_commands.guild_only()
    async def textcat(self, ctx: Context):
        """
        Get a random text cat
        """
        data = await self.client.session.get("https://nekos.life/api/v2/cat")
        json_data = await data.json()
        await ctx.reply(json_data["cat"])

    @commands.hybrid_command(name="coffee", description="Get a random coffee image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def coffee(self, ctx: Context):
        """
        Get a random coffee image from the twizy.dev API
        """
        async with self.client.session.get(
            "https://coffee.alexflipnote.dev/random.json"
        ) as response:
            if response.status == 200:
                coffee = await response.json()
                await ctx.reply(coffee["file"])

    @commands.hybrid_command(name="slots", description="Play the slots")
    @commands.guild_only()
    @app_commands.guild_only()
    async def slots(self, ctx: Context):
        """
        Play the slots
        """
        emojis = ["🍒", "🍊", "🍋", "🍇", "🍉", "🍎"]
        embed = Embed(title="🎰 Slot Machine", timestamp=ctx.message.created_at, colour=Colour.blurple())
        embed.add_field(
            name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n",
            value=f"{random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)}\n\n",
        )
        embed.set_footer(text=f"{ctx.author}")
        message = await ctx.reply(embed=embed)

        slots = [random.choice(emojis) for _ in range(3)]
        for _ in range(3):
            await asyncio.sleep(1)
            slots = [random.choice(emojis) for _ in range(3)]
            embed.set_field_at(
                0, name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"{' '.join(slots)}\n\n"
            )
            await message.edit(embed=embed)

        result = "You won! 🎉" if slots[0] == slots[1] == slots[2] else "You lost. ☠️"

        embed.set_field_at(
            0, name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"\n{' '.join(slots)}\n\n"
        )
        embed.add_field(name="Result:", value=f"**{result}**", inline=False)
        await message.edit(embed=embed)

    @commands.hybrid_command(name="coinflip", description="Flip a coin")
    @commands.guild_only()
    @app_commands.guild_only()
    async def coinflip(self, ctx: Context):
        """
        Flip a coin
        """
        result = random.choice(["Heads", "Tails"])
        embed = Embed(
            title="🪙 Coinflip",
            description=f"{ctx.author.mention} flipped a coin and got **{result}**",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="rps", description="Play rock paper scissors")
    @commands.guild_only()
    @app_commands.guild_only()
    async def rps(
        self,
        ctx: Context,
        choice: Optional[Literal["rock", "paper", "scissors"]],
    ):
        """
        Play rock paper scissors
        """
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)
        if choice is None or choice.lower() not in choices:
            return await ctx.send("Please choose either rock, paper, or scissors.")
        if choice.lower() not in choices:
            return await ctx.send("Please choose either rock, paper, or scissors.")
        if choice.lower() == bot_choice:
            result = "It's a tie!"
        elif choice.lower() == "rock":
            if bot_choice == "paper":
                result = "You lost. ☠️"
            else:
                result = "You won! 🎉"
        elif choice.lower() == "paper":
            if bot_choice == "scissors":
                result = "You lost. ☠️"
            else:
                result = "You won! 🎉"
        elif choice.lower() == "scissors":
            if bot_choice == "rock":
                result = "You lost. ☠️"
            else:
                result = "You won! 🎉"
        embed = Embed(
            title="✂️ Rock Paper Scissors",
            description=f"{ctx.author.mention} chose **{choice}** and {self.client.user.mention} chose **{bot_choice}**\n\n{result}",  # type: ignore
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="kira", description="Likelihood of you or someone being Kira"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def kira(self, ctx: Context, member: Union[Member, User] = None):
        """
        Likelihood of you or someone being Kira
        """
        result = random.randint(0, 100)
        if member is None:
            member: Member = ctx.author
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(DiscordUser).where(DiscordUser.discord_id == str(member.id))
                )
                user: DiscordUser = query.scalar_one_or_none()
                if user is None:
                    new_user = DiscordUser(
                        discord_id=str(member.id),
                        username=member.name,
                        joined=member.joined_at,
                        kira_percentage=result,
                        guild_id=str(
                            member.guild.id,
                        ),
                    )
                    session.add(new_user)
                    await session.flush()
                    await session.commit()
                    embed = Embed(
                        title="✍️️️ Kira",
                        description=f"There is a **{result}%** chance that {member.mention} is Kira",
                        timestamp=ctx.message.created_at,
                    )
                    embed.colour = Colour.blurple()
                    embed.set_footer(
                        text="Try tagging someone else to see if they are Kira"
                    )
                    embed.set_thumbnail(
                        url="https://i.gyazo.com/66470edafe907ac8499c925b5221693d.jpg"
                    )
                    return await ctx.reply(embed=embed)

                if user.kira_percentage == 0 or user.kira_percentage is None:
                    user.kira_percentage = result
                    await session.flush()
                    await session.commit()
                    embed = Embed(
                        title="✍️️️ Kira",
                        description=f"There is a **{result}%** chance that {member.mention} is Kira",
                        timestamp=ctx.message.created_at,
                    )
                    embed.colour = Colour.blurple()
                    embed.set_footer(
                        text="Try tagging someone else to see if they are Kira"
                    )
                    embed.set_thumbnail(
                        url="https://i.gyazo.com/66470edafe907ac8499c925b5221693d.jpg"
                    )
                else:
                    embed = Embed(
                        title="✍️️️ Kira",
                        description=f"There is a **{user.kira_percentage}%** chance that {member.mention} is Kira",
                        timestamp=ctx.message.created_at,
                    )
                    embed.colour = Colour.blurple()
                    embed.set_footer(
                        text="Try tagging someone else to see if they are Kira"
                    )
                    embed.set_thumbnail(
                        url="https://i.gyazo.com/66470edafe907ac8499c925b5221693d.jpg"
                    )
                    await ctx.reply(embed=embed)

    @commands.hybrid_command(name="xkcd", description="Get a Todays XKCD comic")
    @commands.guild_only()
    @app_commands.guild_only()
    async def xkcd(self, ctx: Context):
        """
        Get a random xkcd comic
        """
        response = await self.client.session.get("https://xkcd.com/info.0.json")
        if response.status == 200:
            comic = await response.json()
            embed = Embed(
                title=f"{comic['title']}",
                description=f"{comic['alt']}",
                timestamp=ctx.message.created_at,
            )
            embed.colour = Colour.blurple()
            embed.set_image(url=comic["img"])
            embed.set_footer(text="Provided by xkcd.com")
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("Error getting xkcd comic!", ephemeral=True)

    @commands.hybrid_command(name="year", description="Show the year progress")
    @commands.guild_only()
    @app_commands.guild_only()
    async def year(self, ctx: Context):
        embed: Embed = Embed(timestamp=ctx.message.created_at)
        embed.colour = Colour.blurple()
        embed.set_author(
            name="Year Progress",
            icon_url="https://i.gyazo.com/db74b90ebf03429e4cc9873f2990d01e.png",
        )
        embed.add_field(
            name="Progress:", value=progress_bar(get_year_round()), inline=True
        )
        await ctx.send(embed=embed)

    @commands.command("f", description="Press F to pay respects")
    @commands.guild_only()
    async def f(self, ctx: Context):
        """
        Press F to pay respects
        """
        await ctx.message.delete()
        message = await ctx.send("Press 🇫 to pay respect to the chat.")
        await message.add_reaction("🇫")
        wait = await self.client.wait_for(
            "reaction_add",
            check=lambda r, u: r.message == message
            and r.emoji == "🇫"
            and u != self.client.user,
        )
        await ctx.send(f"{wait[1].mention} is paying respect.")

    @commands.hybrid_command(name="inspiro", description="Get a random inspiro quote")
    @commands.guild_only()
    @app_commands.guild_only()
    async def inspiro(self, ctx: Context):
        """
        Get a random inspiro quote
        """
        async with self.client.session.get(
            "https://inspirobot.me/api?generate=true"
        ) as response:
            if response.status == 200:
                quote = await response.text()
                await ctx.reply(quote)

    @commands.hybrid_command(name="dog", description="Get a random dog image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def dog(self, ctx: Context):
        """
        Get a random dog image
        """
        async with self.client.session.get(
            "https://dog.ceo/api/breeds/image/random"
        ) as response:
            dog = await response.json()
            await ctx.send(dog["message"])

    @commands.hybrid_command(name="supreme", description="Make a supreme image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def supreme(self, ctx: Context, *, text: str):
        """
        Make a supreme image
        """
        await ctx.reply(
            f"https://api.alexflipnote.dev/supreme?text={urllib.parse.quote(text)}"
        )

    @commands.hybrid_command(name="didyoumean", description="Make a did you mean image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def didyoumean(self, ctx: Context, *, top: str, bottom: str):
        """
        Make a did you mean image
        """
        await ctx.reply(
            f"https://api.alexflipnote.dev/didyoumean?top={urllib.parse.quote(top)}&bottom={urllib.parse.quote(bottom)}"
        )

    @commands.hybrid_command(
        name="theoffice", description="🏢 Get a random Quote from The Office"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def the_office(self, ctx: Context):
        """
        Get a random Quote from The Office
        """
        async with self.client.session.get(
            "https://theoffice.foo/quote/random"
        ) as response:
            if response.status == 200:
                quote = await response.json()
                embed = Embed(
                    description=f'"{quote["quote"]}" - {quote["character"]}',
                    timestamp=ctx.message.created_at,
                )
                embed.colour = Colour.blurple()
                embed.set_image(url=quote["character_avatar_url"])
                embed.set_footer(text="https://theoffice.foo/")
                await ctx.reply(embed=embed)
            else:
                await ctx.reply("Error getting The Office quote!", ephemeral=True)

    @commands.hybrid_command(
        "officeclip", description="Get a random clip from The Office"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def officeclip(self, ctx: Context):
        """
        Get a random clip from The Office
        """
        async with self.client.session.get("https://theoffice.foo/extras") as response:
            if response.status == 200:
                data = await response.json()
                random_clip = random.choice(data)
                await ctx.reply(random_clip["video_url"])
            else:
                await ctx.reply("Error getting The Office clip!", ephemeral=True)

    @commands.hybrid_command(name="anime", description="Get a random anime quote")
    @commands.guild_only()
    @app_commands.guild_only()
    async def anime(self, ctx: Context):
        """
        Get a random anime quote
        """
        async with self.client.session.get(
            "https://animechan.xyz/api/random"
        ) as response:
            if response.status == 200:
                quote = await response.json()
                embed = Embed(
                    description=f'"{quote["quote"]}" - {quote["character"]} ({quote["anime"]})',
                    timestamp=ctx.message.created_at,
                )
                embed.colour = Colour.blurple()
                embed.set_footer(text="https://animechan.xyz/")
                await ctx.reply(embed=embed)


async def setup(client: Konikotaka) -> None:
    await client.add_cog(Fun(client))
