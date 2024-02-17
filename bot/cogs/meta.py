from __future__ import annotations

import os
import random
from io import BytesIO
from typing import TYPE_CHECKING, Union

from discord import Colour, Embed, File, Guild, Member, User
from discord.abc import GuildChannel
from discord.ext import commands
from models.users import DiscordUser
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from ..bot import Konikotaka
    from utils.context import Context


class Meta(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client
        self.sex: str = random.choice(["M", "F", "Never"])
        self.random_number: int = random.randint(10**9, (10**10) - 1)
        self.file_path: str = os.path.dirname(os.path.abspath(__file__))
        self.rand_number: int = (
            f"{str(self.random_number)[:-4]}-{str(self.random_number)[-4:]}"
        )  # type: ignore
        self.visa_image = Image.open(f"{self.file_path}/files/visa.jpg")
        self.width, self.height = self.visa_image.size
        self.background_color = (255, 255, 255)
        self.image = Image.new("RGB", (self.width, self.height), self.background_color)
        self.font = ImageFont.truetype(
            f"{self.file_path}/files/runescape_uf.ttf", size=34
        )
        self.user_font = ImageFont.truetype(
            f"{self.file_path}/files/runescape_uf.ttf", size=45
        )
        self.iss = random.choice(
            [
                "Orvech Vonor",
                "East Grestin",
                "Paradizna" "St. Marmero",
                "Glorian",
                "Outer Grouse",
                "Enkyo",
                "Haihan",
                "Tsunkeido",
            ]
        )

    def random_birthday(self) -> str:
        """Generates a random birthday."""
        year = random.randint(1900, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month}.{day}.{year}"

    def random_expiration(self) -> str:
        """Generates a random expiration date."""
        year = random.randint(1900, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month}.{day}.{year}"

    async def create_image(self, member: Union[Member, User]) -> str:
        discord_avatar = await self.client.session.get(member.avatar.url)
        discord_avatar = Image.open(BytesIO(await discord_avatar.read()))
        discord_avatar = discord_avatar.resize((150, 200))
        draw = ImageDraw.Draw(self.image)
        self.image.paste(self.visa_image, (0, 0))
        draw.text((115, 525), str(member.name), fill=(0, 0, 0), font=self.user_font)
        draw.text((400, 590), self.random_birthday(), fill=(0, 0, 0), font=self.font)
        draw.text((400, 632), self.sex, fill=(0, 0, 0), font=self.font)
        draw.text((400, 674), self.iss, fill=(0, 0, 0), font=self.font)
        draw.text((400, 713), self.random_expiration(), fill=(0, 0, 0), font=self.font)
        draw.text((75, 880), str(self.rand_number), fill=(1, 20, 20), font=self.font)
        self.image.paste(discord_avatar, (100, 589))
        file_path = f"{self.file_path}/files/{member.id}.jpg"
        self.image.save(file_path)
        return file_path

    @commands.Cog.listener()
    async def on_member_join(self, member: Union[Member, User]) -> None:
        if member.guild.id == self.client.main_guild: # type: ignore
            user = DiscordUser(
                discord_id=str(member.id),
                username=member.name,
                joined=member.joined_at, # type: ignore
                guild_id=str(member.guild.id), # type: ignore
                xp=0,
                level=0,
            )
            async with self.client.async_session() as session:
                async with session.begin():
                    try:
                        session.add(user)
                        await session.flush()
                        await session.commit()
                    except Exception as e:
                        self.client.log.error(e)
                        await session.rollback()

        image = await self.create_image(member)
        channel = await self.client.fetch_channel(member.guild.system_channel.id) # type: ignore
        await channel.send(  # type: ignore
            content=f"Welcome {member.mention} to the {member.guild.name} discord server!", # type: ignore
            file=File(image),
        )
        os.remove(image)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: Guild, user: Member) -> None:
        if guild.id != self.client.main_guild:
            return
        async with self.client.async_session() as session:
            async with session.begin():
                try:
                    user = await session.query(DiscordUser, str(user.id))
                    if user is None:
                        return
                    await session.delete(user)
                    await session.flush()
                    await session.commit()
                    embed = Embed(
                        title="User Banned 🚨",
                    )
                    embed.colour = Colour.blurple()
                    embed.add_field(name="User:", value=user.mention, inline=False)
                    channel: GuildChannel = self.client.get_channel(
                        self.general_channel # type: ignore
                    )
                    await channel.send(embed=embed)  # type: ignore
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.guild.id != self.client.main_guild:
            return
        async with self.client.async_session() as session:
            async with session.begin():
                try:
                    user: DiscordUser = await session.query(DiscordUser, before.id)
                    if user is None:
                        return
                    user.username = after.name
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()


async def setup(client: Konikotaka) -> None:
    await client.add_cog(Meta(client))
