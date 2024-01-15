from models.db import Base
from sqlalchemy import DATE, VARCHAR, Column, Integer


class DiscordUser(Base):
    """
    Discord User Model
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
