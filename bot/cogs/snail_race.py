import asyncio
import random
from typing import Dict, Optional

import discord
from discord import Interaction, Member, app_commands
from discord.ext import commands, tasks
from models.db import Base
from models.race import Race

snail_positions: Dict = {}


class JoinRaceButton(discord.ui.View):
    def __init__(self, *, timeout: int = 45):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Join Race", style=discord.ButtonStyle.blurple, emoji="🐌")
    async def race_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id in snail_positions:
            await interaction.response.edit_message(
                content="You already joined the race! 🐌",
                ephemeral=True,
            )
            return
        snail_positions[interaction.user.id] = 0
        await interaction.response.send_message(
            f"You've entered into the race!", ephemeral=True
        )


class SnailRace(commands.Cog, name="Snail Racing"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    async def simulate_race(self, interaction: Interaction):
        winner: Member = None
        race_length: int = 10
        message = await interaction.channel.send("Race is starting")
        while not winner:
            if len(snail_positions) < 2:
                snail_positions[self.client.user.id] = 0
            for user_id in snail_positions:
                snail_positions[user_id] += random.randint(1, 3)

                if snail_positions[user_id] >= race_length:
                    winner = self.client.get_user(user_id)
                    break
            race_progress: str = ""
            for user_id, position in snail_positions.items():
                user = self.client.get_user(user_id)
                race_progress += f"{user.name}: {'🐌' * position}\n"
            await asyncio.sleep(random.randint(1, 3))
            await message.edit(
                content=f"🏁 **The race is now in progress!** 🏁\n{race_progress}"
            )
        snail_positions.clear()
        embed = discord.Embed(
            title="Congratulations!",
            description=f"{winner.mention} won the race! 🏁",
            color=discord.Color.green(),
            timestamp=interaction.created_at,
        )
        embed.set_thumbnail(url=winner.display_avatar.url)
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="race", description="Start a Snail Race")
    @app_commands.guild_only()
    @discord.app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    async def race(self, interaction: Interaction, delay: Optional[int] = 10) -> None:
        view: JoinRaceButton = JoinRaceButton()
        if delay > 30:
            await interaction.response.send_message(
                "Delay must be less than 30 seconds"
            )
            return
        await interaction.response.send_message(
            content=f"{interaction.user.mention} has started a race.",
            view=view,
        )
        await asyncio.sleep(delay)
        await self.simulate_race(interaction)
    
    @race.error
    async def on_race_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message("Another race is in progress, please wait until the race has finished.", ephemeral=True)
  
    @app_commands.command(name="leaderboard", description="Get Race Leaderboard")
    async def leaderboard(self, interaction: Interaction) -> None:
        await interaction.response.send("This command is not implemented yet.")
  

async def setup(client: commands.Bot) -> None:
    await client.add_cog(SnailRace(client))
