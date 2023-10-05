from models.db import Base
from sqlalchemy import DATE, VARCHAR, Column, Integer, BigInteger


class DiscordUser(Base):
    """
    Discord User Model
    """

    __tablename__ = "discord_users"
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, nullable=False)
    username = Column(VARCHAR(255), nullable=False)
    joined = Column(DATE, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    kira_percentage = Column(Integer, nullable=True)
