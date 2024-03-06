from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
import random


class RandomChoiceCog(commands.Cog):
    def __init__(self, client: discord.Bot) -> None:
        self.client: discord.Bot = client

    @app_commands.command(name="choose", description="Choose between multiple options")
    async def choose_command(
        self,
        interaction: discord.Interaction,
        choice_1: Optional[str],
        choice_2: Optional[str],
        choice_3: Optional[str],
        choice_4: Optional[str],
        choice_5: Optional[str],
        choice_6: Optional[str],
        choice_7: Optional[str],
        choice_8: Optional[str],
        choice_9: Optional[str],
        choice_10: Optional[str],
    ):
        choices = [
            choice_1,
            choice_2,
            choice_3,
            choice_4,
            choice_5,
            choice_6,
            choice_7,
            choice_8,
            choice_9,
            choice_10,
        ]
        choices = [choice for choice in choices if choice is not None]
        if len(choices) < 2:
            await interaction.response.send_message(
                "You need to provide at least 2 choices", ephemeral=True
            )
            return
        choice = random.choice(choices)
        await interaction.response.send_message(choice)


async def setup(client: discord.Bot) -> None:
    await client.add_cog(RandomChoiceCog(client))
