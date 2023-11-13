from __future__ import annotations

import asyncio
import os
import random
import urllib.parse
from io import BytesIO
from typing import Literal, Optional, Union

import upsidedown
from discord import Colour, Embed, File, Member, Message, app_commands
from discord.ext import commands
from models.users import DiscordUser
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.future import select

from .utils.map_cords import map_cords
from .utils.utils import get_year_round, progress_bar


class Fun(commands.Cog, name="Fun"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.hybrid_command(
        name="cosmo", help="Get a random Photo of Cosmo the Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def cosmo_photo(self, ctx: commands.Context) -> None:
        """
        Get a random photo of my cat Cosmo!
        """
        async with self.client.session.get("https://api.twizy.sh/v1/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                embed = Embed()
                embed.title = "🐈 Cosmo"
                embed.url = "https://cosmo.alexraskin.com"
                embed.colour = Colour.blurple()
                embed.set_image(url=photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Cosmo!")

    @commands.hybrid_command(
        name="bczs",
        help="Get a random photo of Pat and Ash's cats",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def bczs_photos(self, ctx: commands.Context) -> Message:
        """
        Get a random photo of Pat and Ash's cats from the twizy.dev API
        """
        async with self.client.session.get("https://api.twizy.dev/v1/bczs") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Pat and Ash's cats!")

    @commands.hybrid_command(
        name="meme", help="Get a random meme!", with_app_command=True
    )
    @commands.guild_only()
    async def get_meme(self, ctx: commands.Context) -> Message:
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
    async def gcat_talk(self, ctx: commands.Context, *, message: str) -> Message:
        """
        Translate your message into G Cat's language
        """
        up_down = upsidedown.transform(message)
        await ctx.send(up_down)

    @commands.hybrid_command(name="waifu", aliases=["getwaifu"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_waifu(
        self,
        ctx: commands.Context,
        category: Literal["waifu", "neko", "shinobu", "megumin", "bully", "cuddle"],
    ) -> Message:
        """
        Get a random waifu image from the waifu API
        """
        response = await self.client.session.get(
            f"https://api.waifu.pics/sfw/{category}"
        )
        if response.status == 200:
            waifu = await response.json()
            await ctx.send(waifu["url"])
        else:
            await ctx.send("Error getting waifu!")

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name="cat", description="Get a random cat image")
    async def cat(self, ctx: commands.Context) -> Message:
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

    @commands.hybrid_command(name="roll", description="Roll a dice with NdN")
    @commands.guild_only()
    @app_commands.guild_only()
    async def roll(self, ctx: commands.Context, dice: str) -> Embed:
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
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball a question")
    @commands.guild_only()
    @app_commands.guild_only()
    async def eight_ball(self, ctx: commands.Context, *, question: str) -> Embed:
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
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="fact", description="Get a random fact")
    @commands.guild_only()
    @app_commands.guild_only()
    async def fact(self, ctx: commands.Context) -> Embed:
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
    async def reverse(self, ctx: commands.Context, string: str) -> Embed:
        """
        Reverse a string
        """
        embed = Embed(
            title="🔁 Reverse",
            description=f"String: {string}\nReversed: {string[::-1]}",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="say", description="Make the bot say something")
    @commands.guild_only()
    @app_commands.guild_only()
    async def say(self, ctx: commands.Context, message: str) -> Message:
        """
        Make the bot say something
        """
        await ctx.send(message)

    @commands.hybrid_command(
        name="embed", description="Make the bot say something in an embed"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def _embed(self, ctx: commands.Context, message: str) -> Embed:
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
    async def hug(self, ctx: commands.Context, member: Member) -> Embed:
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
    async def slap(self, ctx: commands.Context, member: Member) -> Embed:
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
    async def kiss(self, ctx: commands.Context, member: Member) -> Embed:
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
    async def pat(self, ctx: commands.Context, member: Member) -> Embed:
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
    async def textcat(self, ctx: commands.Context) -> Message:
        """
        Get a random text cat
        """
        data = await self.client.session.get("https://nekos.life/api/v2/cat")
        json_data = await data.json()
        await ctx.send(json_data["cat"])

    @commands.hybrid_command(name="coffee", description="Get a random coffee image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def coffee(self, ctx: commands.Context) -> Message:
        """
        Get a random coffee image from the twizy.dev API
        """
        async with self.client.session.get(
            "https://coffee.alexflipnote.dev/random.json"
        ) as response:
            if response.status == 200:
                coffee = await response.json()
                await ctx.send(coffee["file"])
            else:
                await ctx.send("Error getting coffee!")

    @commands.hybrid_command(name="slots", description="Play the slots")
    @commands.guild_only()
    @app_commands.guild_only()
    async def slots(self, ctx: commands.Context) -> Embed:
        """
        Play the slots
        """
        emojis = ["🍒", "🍊", "🍋", "🍇", "🍉", "🍎"]
        embed = Embed(title="🎰 Slot Machine", timestamp=ctx.message.created_at)
        embed.colour = Colour.blurple()
        embed.add_field(
            name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n",
            value=f"{random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)}\n\n",
        )
        embed.set_footer(text=f"{ctx.author}")
        message = await ctx.reply(embed=embed)
        # Spin the slots
        for _ in range(3):
            await asyncio.sleep(1)  # Delay for a second to simulate spinning
            slot1 = random.choice(emojis)
            slot2 = random.choice(emojis)
            slot3 = random.choice(emojis)

            # Update the embed with spinning slots
            embed.set_field_at(
                0, name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"{slot1} {slot2} {slot3}\n\n"
            )
            await message.edit(embed=embed)

        # Check if the player wins or loses
        if slot1 == slot2 == slot3:
            result = "You won! 🎉"
        else:
            result = "You lost. ☠️"

        # Update the embed with the final result
        embed.set_field_at(
            0, name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"\n{slot1} {slot2} {slot3}\n\n"
        )
        embed.add_field(name="Result:", value=f"**{result}**", inline=False)
        await message.edit(embed=embed)
        print("hello4")

    @commands.hybrid_command(name="coinflip", description="Flip a coin")
    @commands.guild_only()
    @app_commands.guild_only()
    async def coinflip(self, ctx: commands.Context) -> Embed:
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
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rps", description="Play rock paper scissors")
    @commands.guild_only()
    @app_commands.guild_only()
    async def rps(
        self,
        ctx: commands.Context,
        choice: Optional[Literal["rock", "paper", "scissors"]],
    ) -> Embed:
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
            description=f"{ctx.author.mention} chose **{choice}** and {self.client.user.mention} chose **{bot_choice}**\n\n{result}",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="kira", description="Likelihood of you or someone being Kira"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def kira(self, ctx: commands.Context, member: Member = None) -> Embed:
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
                user = query.scalar_one_or_none()
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
                    return await ctx.send(embed=embed)

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
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name="xkcd", description="Get a Todays XKCD comic")
    @commands.guild_only()
    @app_commands.guild_only()
    async def xkcd(self, ctx: commands.Context) -> Union[Embed, Message]:
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
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error getting xkcd comic!")

    @commands.hybrid_command(name="year", description="Show the year progress")
    @commands.guild_only()
    @app_commands.guild_only()
    async def year(self, ctx: commands.Context):
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
    async def f(self, ctx: commands.Context):
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
    async def inspiro(self, ctx: commands.Context) -> Message:
        """
        Get a random inspiro quote
        """
        async with self.client.session.get(
            "https://inspirobot.me/api?generate=true"
        ) as response:
            if response.status == 200:
                quote = await response.text()
                await ctx.send(quote)
            else:
                await ctx.send("Error getting quote!")

    @commands.hybrid_command(name="dog", description="Get a random dog image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def dog(self, ctx: commands.Context) -> Message:
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
    async def supreme(self, ctx: commands.Context, *, text: str) -> Message:
        """
        Make a supreme image
        """
        await ctx.send(
            f"https://api.alexflipnote.dev/supreme?text={urllib.parse.quote(text)}"
        )

    @commands.hybrid_command(name="didyoumean", description="Make a did you mean image")
    @commands.guild_only()
    @app_commands.guild_only()
    async def didyoumean(
        self, ctx: commands.Context, *, top: str, bottom: str
    ) -> Message:
        """
        Make a did you mean image
        """
        await ctx.send(
            f"https://api.alexflipnote.dev/didyoumean?top={urllib.parse.quote(top)}&bottom={urllib.parse.quote(bottom)}"
        )

    @commands.hybrid_command(
        name="wherewedropping", description="Get a random location to drop in Fortnite"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def where_we_dropping(self, ctx: commands.Context):
        """
        Get a random location to drop in Fortnite
        """
        file_path = os.path.dirname(os.path.abspath(__file__))
        data = await self.client.session.get("https://fortnite-api.com/images/map.png")
        map = Image.open(BytesIO(await data.read()))
        width, height = map.size
        background_color = (255, 255, 255)
        image = Image.new("RGB", (width, height), background_color)
        image.paste(map, (0, 0))
        draw = ImageDraw.Draw(image)
        random_location = random.choice(list(map_cords.keys()))
        draw.text(
            map_cords[random_location],
            random_location,
            fill=(255, 255, 255),
            font=ImageFont.truetype(
                f"{file_path}/files/AROneSans.ttf",
                size=60,
            ),
        )
        image.save(f"{file_path}/files/map.png")
        embed = Embed(
            title="🗺️ Where We Droppin'?",
            description=f"**{random_location}**",
            timestamp=ctx.message.created_at,
        )
        embed.colour = Colour.blurple()
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed, file=File(f"{file_path}/files/map.png"))
        os.remove(f"{file_path}/files/map.png")

    @commands.hybrid_command(
        name="theoffice", description="🏢 Get a random Quote from The Office"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def the_office(self, ctx: commands.Context) -> Message:
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
                await ctx.send(embed=embed)

    @commands.hybrid_command("officeclip", description="Get a random clip from The Office")
    @commands.guild_only()
    @app_commands.guild_only()
    async def officeclip(self, ctx: commands.Context) -> Message:
        """
        Get a random clip from The Office
        """
        async with self.client.session.get(
            "https://theoffice.foo/extras"
        ) as response:
            if response.status == 200:
                data = await response.json()
                random_clip = random.choice(data)
                await ctx.send(random_clip["video_url"])

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Fun(client))
