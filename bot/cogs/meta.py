from __future__ import annotations

import os
import random
from io import BytesIO
from typing import Union

from discord import File, Member, User
from discord.ext import commands
from models.users import DiscordUser
from PIL import Image, ImageDraw, ImageFont


class Meta(commands.Cog, name="Meta"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.sex = random.choice(["M", "F", "Never"])
        self.random_number = random.randint(10**9, (10**10) - 1)
        self.abs_path = os.path.abspath(__file__)
        self.file_path = os.path.dirname(self.abs_path)
        self.rand_number = (
            f"{str(self.random_number)[:-4]}-{str(self.random_number)[-4:]}"
        )
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

    def random_birthday(self):
        """Generates a random birthday."""
        year = random.randint(1900, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month}.{day}.{year}"

    def random_expiration(self):
        """Generates a random expiration date."""
        year = random.randint(1900, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month}.{day}.{year}"

    @commands.Cog.listener()
    async def on_member_join(self, member: Union[Member, User]) -> None:
        if member.guild.id != self.client.cosmo_guild:
            return
        user = DiscordUser(
            discord_id=str(member.id),
            username=member.name,
            joined=member.joined_at,
            guild_id=str(member.guild.id),
        )
        async with self.client.async_session() as session:
            try:
                session.add(user)
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()
        try:
            discord_avatar = await self.client.session.get(member.avatar.url)
            discord_avatar = Image.open(BytesIO(await discord_avatar.read()))
            discord_avatar = discord_avatar.resize((150, 200))
            draw = ImageDraw.Draw(self.image)
            self.image.paste(self.visa_image, (0, 0))
            draw.text((115, 525), str(member.name), fill=(0, 0, 0), font=self.user_font)
            draw.text(
                (400, 590), self.random_birthday(), fill=(0, 0, 0), font=self.font
            )
            draw.text((400, 632), self.sex, fill=(0, 0, 0), font=self.font)
            draw.text((400, 674), self.iss, fill=(0, 0, 0), font=self.font)
            draw.text(
                (400, 713), self.random_expiration(), fill=(0, 0, 0), font=self.font
            )
            draw.text(
                (75, 880), str(self.rand_number), fill=(1, 20, 20), font=self.font
            )
            self.image.paste(discord_avatar, (100, 589))
            self.image.save(f"{self.file_path}/files/{member.id}.jpg")
            channel = await self.client.fetch_channel(self.client.general_channel)
            await channel.send(
                file=File(f"{self.file_path}/files/{member.id}.jpg"),
            )
            os.remove(f"{self.file_path}/files/{member.id}.jpg")
        except Exception as e:
            self.client.log.error(e)
            return


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Meta(client))
