from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from discord import Colour, Embed, Interaction, Message, User, Member, app_commands
from discord.ext import commands
from models.users import DiscordUser
from sqlalchemy.future import select  # type: ignore

if TYPE_CHECKING:
    from ..bot import Konikotaka


class Levels(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client

    def get_xp_needed(self, level) -> int:
        """
        Returns the amount of xp needed to level up.
        """
        return 100 * level

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        Gives xp to users when they send a message.
        """
        if message.author == self.client.user:
            return
        if message.guild.id != self.client.main_guild:  # type: ignore
            return
        if message.author.bot:
            return
        if message.webhook_id:
            return
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(DiscordUser).where(
                        DiscordUser.discord_id == str(message.author.id)
                    )
                )
                user: DiscordUser = query.scalar_one_or_none()
                if user:
                    xp, level = user.xp, user.level
                    new_xp = xp + 5
                    new_level = level
                    if new_xp >= self.get_xp_needed(level):
                        new_xp -= self.get_xp_needed(level)
                        new_level += 1
                    user.xp = new_xp
                    user.level = new_level
                    await session.commit()
                    await session.flush()
                else:
                    user: DiscordUser = DiscordUser(
                        discord_id=str(message.author.id),
                        username=message.author.name,
                        joined=message.author.joined_at,  # type: ignore
                        guild_id=str(message.guild.id),  # type: ignore
                        xp=5,
                        level=1,
                    )
                    session.add(user)
                    await session.commit()
                    await session.flush()

    @app_commands.command(name="rank")
    @app_commands.describe(user="The user to get the rank of")
    async def rank(self, interaction: Interaction, user: Optional[Union[Member, User]] = None) -> None:  # type: ignore
        """
        Sends a user's rank
        """
        if user is None:
            user: Union[Member, User] = interaction  # type: ignore
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(DiscordUser).where(
                        DiscordUser.discord_id == str(interaction.user.id)
                    )
                )
                user: DiscordUser = query.scalar_one_or_none()
                embed = Embed()
                embed.title = "Level"
                embed.color = Colour.blurple()
                if user:
                    embed.description = f"You are level {user.level} with {user.xp} xp."
                    await interaction.response.send_message(embed=embed)
                else:
                    return await interaction.response.send_message(
                        "You are not in the database."
                    )

    @app_commands.command(name="levelsboard")
    async def levelsboard(self, interaction: Interaction) -> None:
        """
        Sends a leaderboard of users sorted by level.
        """
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(DiscordUser).order_by(DiscordUser.level.desc())
                )
                users: DiscordUser = query.scalars().all()
                embed = Embed()
                embed.title = "Levels Leaderboard - Sorted by Level"
                embed.color = Colour.blurple()
                if users:
                    leaderboard = ""
                    for user in users:
                        leaderboard += f"{user.username} is level {user.level} with {user.xp} xp.\n"
                    embed.description = leaderboard
                    await interaction.response.send_message(embed=embed)
                else:
                    return await interaction.response.send_message(
                        "There are no users in the database."
                    )


async def setup(client: Konikotaka) -> None:
    await client.add_cog(Levels(client))
