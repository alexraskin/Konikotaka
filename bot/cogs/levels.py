from __future__ import annotations

from discord.ext import commands
from discord import Message, app_commands, Interaction, User, Embed, Colour
from sqlalchemy.future import select

from models.users import DiscordUser


class Levels(commands.Cog, name="Levels"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    def get_xp_needed(self, level):
        return 100 * level

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author == self.client.user:
            return
        if message.guild.id != self.client.cosmo_guild:
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
                user = query.scalar_one_or_none()
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
                    user = DiscordUser(
                        discord_id=str(message.author.id),
                        username=message.author.name,
                        joined=message.author.joined_at,
                        guild_id=str(message.guild.id),
                        xp=5,
                        level=1,
                    )
                    session.add(user)
                    await session.commit()
                    await session.flush()

    @app_commands.command(name="rank")
    async def rank(self, interaction: Interaction, user: User = None) -> None:
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(DiscordUser).where(
                        DiscordUser.discord_id == str(interaction.user.id)
                    )
                )
                user = query.scalar_one_or_none()
                embed = Embed()
                embed.title = "Level"
                embed.color = Colour.blurple()
                if user:
                    embed.description = f"You are level {user.level} with {user.xp} xp."
                    await interaction.response.send_message(embed=embed)
                else:
                    return

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
                users = query.scalars().all()
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
                    return


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Levels(client))
