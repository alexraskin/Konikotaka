import random

from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class RandomChoiceCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @app_commands.command(name="choose", description="Choose between multiple options")
    @app_commands.describe(choice_1="The first choice")
    @app_commands.describe(choice_2="The second choice")
    @app_commands.describe(choice_3="The third choice")
    @app_commands.describe(choice_4="The fourth choice")
    @app_commands.describe(choice_5="The fifth choice")
    @app_commands.describe(choice_6="The sixth choice")
    @app_commands.describe(choice_7="The seventh choice")
    @app_commands.describe(choice_8="The eighth choice")
    @app_commands.describe(choice_9="The ninth choice")
    @app_commands.describe(choice_10="The tenth choice")
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
        embed = discord.Embed()
        embed.title = "Random Choice"
        embed.description = f"From the choices {', '.join(choices)}, I choose {choice}"
        embed.color = discord.Colour.blurple()
        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(RandomChoiceCog(client))
