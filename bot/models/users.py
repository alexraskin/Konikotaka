from models.db import Base
from sqlalchemy import DATE, VARCHAR, Column, Integer  # type: ignore


class DiscordUser(Base):
    """
    Discord User Model

    Attributes:
    - id: int
        The primary key of the table
    - discord_id: str
        The discord id of the user
    - username: str
        The username of the user
    - joined: str
        The date the user joined the guild
    - guild_id: str
        The guild id of the user
    - kira_percentage: int
        The kira percentage of the user
    - level: int
        The level of the user
    - xp: int
        The xp of the user
    """

    __tablename__ = "discord_users"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    username = Column(VARCHAR(255), nullable=False)
    joined = Column(DATE, nullable=False)
    guild_id = Column(VARCHAR(255), nullable=False)
    kira_percentage = Column(Integer, nullable=True)
    level = Column(Integer, nullable=True)
    xp = Column(Integer, nullable=True)
