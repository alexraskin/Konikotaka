from __future__ import annotations

import os
import random
import urllib.parse

from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, menus
from discord.ext.commands import GroupCog
from discord.app_commands import command


class PalPages(menus.ListPageSource):
    def __init__(self, data, per_page):
        super().__init__(data, per_page=per_page)

    async def format_page(self, menu, page):
        embed = discord.Embed(title="Palworld Pals", color=discord.Color.purple())
        embed.set_thumbnail(
            url="https://i.gyazo.com/272047b9ab38dd7d5a1ad5513436fcdf.png"
        )
        for item in page:
            embed.add_field(
                name=item["name"], value=f"[Wiki]({item['wiki']})", inline=True
            )
        return embed


class PalMenu(menus.MenuPages):
    pass


class Palworld(GroupCog, name="palworld"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.base_url: str = "https://palapi.world"
        self.server_ip: str = os.getenv("PALWORLD_SERVER_IP")

    def build_url(self, **kwargs) -> str:
        url = self.base_url
        param_list = [
            f"{key}={urllib.parse.quote_plus(str(value))}"
            for key, value in kwargs.items()
            if value is not None
        ]
        url_params = "&".join(param_list)
        return url + ("?" + url_params if url_params else "")

    @command(name="palworld")
    async def palworld(self, interaction: discord.Interaction) -> None:
        """Get the Palworld API information"""

        embed = discord.Embed()
        embed.set_author(name="Palworld")
        embed.title = "Palworld API"
        embed.description = "The Palworld API is a RESTful API that allows you to get information about the Pals in the game."
        embed.url = "https://palapi.world"
        embed.set_thumbnail(
            url="https://i.gyazo.com/272047b9ab38dd7d5a1ad5513436fcdf.png"
        )
        embed.timestamp = interaction.created_at
        embed.set_footer(text="Powered by Palworld API")
        await interaction.response.send_message(embed=embed)

    @command(name="connect")
    async def connect(self, interaction: discord.Interaction) -> None:
        """Palworld Server IP Address"""

        if interaction.guild.id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )

        embed = discord.Embed()
        embed.colour = discord.Colour.blurple()
        embed.title = "Palworld Server IP Address"
        embed.description = f"{self.server_ip} (This is not an invite code. You need to join using the multiplayer feature in the game.)"
        embed.set_thumbnail(
            url="https://i.gyazo.com/272047b9ab38dd7d5a1ad5513436fcdf.png"
        )
        embed.timestamp = interaction.created_at
        await interaction.response.send_message(embed=embed)

    @command(name="allpals")
    async def allpals(self, ctx: commands.Context, page: Optional[int] = 5):
        """Get all pals"""

        url = self.build_url(page=page)
        response = await self.client.session.get(url)
        data = await response.json()

        if response.status == 200:
            pages = PalPages(data["content"], per_page=5)
            menu = PalMenu(pages)
            await menu.start(ctx)
        else:
            await ctx.send("No results found.")

    @command(name="search")
    @app_commands.describe(query="The pal to search for")
    async def search(
        self,
        interaction: discord.Interaction,
        query: Optional[str],
    ):
        """Search for a pal"""

        url = self.build_url(term=query)
        response = await self.client.session.get(url)
        if response.status == 200:
            data = await response.json()
            embed = discord.Embed()
            embed.set_author(name="Palworld")
            embed.title = "Search Results"
            description = ""
            count = 0
            for result in data["content"]:
                count += 1
                description += f"{count}. [{result['name']}]({result['wiki']})\n"
            embed.description = description
            embed.set_thumbnail(
                url="https://i.gyazo.com/272047b9ab38dd7d5a1ad5513436fcdf.png"
            )
            embed.timestamp = interaction.created_at
            embed.set_footer(text=f"Found {count} results.")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No results found.")

    @command(name="random")
    async def random(
        self,
        interaction: discord.Interaction,
    ):
        """Get a random pal"""

        url = self.build_url(page=random.randint(1, 10))

        response = await self.client.session.get(url)
        data = await response.json()

        if response.status == 200:
            random_choice = random.choice(data["content"])
            image = self.base_url + random_choice["image"]
            types = str(random_choice["types"]).strip("[]").replace("'", "")
            drops = str(random_choice["drops"]).strip("[]").replace("'", "")
            aura_name = random_choice["aura"]["name"]
            aura_description = random_choice["aura"]["description"]
            suitability_type = random_choice["suitability"][0]["type"]
            suitability_level = random_choice["suitability"][0]["level"]

            embed = discord.Embed(
                title=random_choice["name"],
                description=random_choice["description"],
                color=discord.Color.random(),
            )
            embed.url = random_choice["wiki"]
            embed.set_thumbnail(url=image)
            embed.add_field(name="ID", value=random_choice["id"])
            embed.add_field(name="Types", value=types)
            embed.add_field(name="Drops", value=drops)
            embed.add_field(name="Aura", value=f"{aura_name}: {aura_description}")
            embed.add_field(
                name="Suitability", value=f"{suitability_type}: {suitability_level}"
            )
            embed.timestamp = interaction.created_at
            embed.set_footer(text="Powered by Palworld API")
            await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(Palworld(client))
