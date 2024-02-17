from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, Optional, Union

import discord
from discord import Colour, Interaction, Member, User, app_commands
from discord.ext import commands
from models.races import Races
from sqlalchemy.future import select  # type: ignore

guilds: dict = {}
snail_positions: dict = {}

if TYPE_CHECKING:
    from ..bot import Konikotaka


def add_guild(guild_id: int) -> None:
    if guild_id not in guilds:
        guilds[guild_id] = {}


def add_user_to_guild(guild_id: int, user_id: int) -> None:
    if guild_id in guilds:
        guilds[guild_id][user_id] = True
    else:
        add_guild(guild_id)
        guilds[guild_id][user_id] = True


class RaceButton(discord.ui.View):
    def __init__(self, *, timeout: int = 45):
        super().__init__(timeout=timeout)
        global guilds

    @discord.ui.button(label="Join Race", style=discord.ButtonStyle.blurple, emoji="🐌")
    async def join_race(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()

        if interaction.user.id not in guilds[interaction.guild.id]:
            await interaction.followup.send(
                "You've entered into the race!", ephemeral=True
            )
            add_user_to_guild(interaction.guild.id, interaction.user.id)
        else:
            await interaction.followup.send(
                content="You already joined the race! 🐌", ephemeral=True
            )

    @discord.ui.button(label="Leave Race", style=discord.ButtonStyle.red, emoji="🚫")
    async def leave_race(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()

        if interaction.user.id not in guilds[interaction.guild.id]:
            await interaction.followup.send(
                content="You need to join the race first!", ephemeral=True
            )
        else:
            del guilds[interaction.guild.id][interaction.user.id]
            await interaction.followup.send(
                content="You have left the race! 🚫", ephemeral=True
            )


class SnailRace(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client

    async def randomize_snails(self) -> None:
        global shuffled_participants
        participants = list(guilds[self.client.guild.id].keys())
        shuffled_participants = random.sample(participants, len(participants))
        return shuffled_participants

    async def update_leaderboard(self, winner: Member) -> None:
        updated_racer = Races(
            discord_id=str(winner.id),
            wins=1,
            points=1,
            location_id=winner.guild.id,
        )
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(Races).filter(
                        Races.discord_id == str(winner.id)
                        and Races.location_id == winner.guild.id
                    )
                )
                racer = query.scalar_one_or_none()
                if racer:
                    racer.wins += 1
                    racer.points += 1
                    session.add(racer)
                else:
                    session.add(updated_racer)
                try:
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()
                    self.client.log.error(
                        f"An error occurred while updating the leaderboard.\n{e}"
                    )

    async def simulate_race(self, interaction: Interaction) -> None:
        global snail_positions
        global shuffled_participants
        winner: Union[Member, User] = None
        race_length: int = 10
        if len(shuffled_participants) == 0:
            await interaction.channel.send(content="No one joined the race! 😢")
            return
        message = await interaction.channel.send("The Race is starting! 🚩")
        shuffled_participants.append(self.client.user.id)
        randomize_snail = await self.randomize_snails()
        snail_positions = {user_id: 0 for user_id in randomize_snail}
        while not winner:
            for user_id in snail_positions:
                snail_positions[user_id] += random.randint(1, 3)

                if snail_positions[user_id] >= race_length:
                    winner = self.client.get_user(user_id)
                    break
            race_progress: str = ""
            for user_id, position in snail_positions.items():
                user: Union[Member, User] = self.client.get_user(user_id)
                race_progress += f"[{user.name}]: {'🐌' * position}\n"
            await asyncio.sleep(random.randint(1, 3))
            await message.edit(
                content=f"🏁 **The race is now in progress!** 🏁\n{race_progress}"
            )
        embed = discord.Embed(
            title="Congratulations!",
            description=f"{winner.mention} won the race! 🏁",
            color=discord.Color.green(),
            timestamp=interaction.created_at,
        )
        embed.set_thumbnail(url=winner.display_avatar.url)
        await interaction.channel.send(embed=embed)
        if winner.name != self.client.user.name:
            await self.update_leaderboard(winner)

    @app_commands.command(name="race", description="Start a Snail Race")
    @app_commands.guild_only()
    async def race(self, interaction: Interaction, delay: Optional[int] = 10) -> None:
        global running_guilds
        view: RaceButton = RaceButton(timeout=delay)
        if interaction.guild.id in running_guilds:
            await interaction.response.send_message(
                content="A race is already running in this server!",
                ephemeral=True,
            )
            return
        if delay > 30 or delay < 5:
            await interaction.response.send_message(
                content="Please specify a delay between 5 and 30 seconds.",
                ephemeral=True,
            )
            return
        running_guilds.append(interaction.guild.id)
        await interaction.response.send_message(
            content=f"{interaction.user.mention} has started a race.\nRace will start in {delay} seconds.",
            view=view,
        )
        await asyncio.sleep(delay)
        await self.simulate_race(interaction)

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: app_commands.Command,
    ) -> None:
        try:
            snail_positions.clear()
            shuffled_participants.clear()
            running_guilds.remove(interaction.guild.id)
        except ValueError:
            pass

    @app_commands.command(name="leaderboard", description="Get Race Leaderboard")
    @app_commands.guild_only()
    async def leaderboard(self, interaction: Interaction) -> None:
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(Races).order_by(Races.points.desc()).limit(3)
                )
                racers = query.scalars().all()
                leaderboard = ""
                for racer in racers:
                    racer_info = self.client.get_user(
                        int(str(racer.discord_id).strip())
                    )
                    leaderboard += f"{racer_info.mention}: {racer.points} points 🏅\n"

                embed = discord.Embed(
                    title="Snail Racing Leaderboard 🏆",
                    description=leaderboard,
                    timestamp=interaction.created_at,
                )
                embed.colour = Colour.blurple()
                await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(SnailRace(client))
