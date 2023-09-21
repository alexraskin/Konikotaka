from models.db import Base
from sqlalchemy import DATETIME, VARCHAR, Column, Integer


class DiscordUser(Base):
    """
    Discord User Model
    """

    __tablename__ = "discord_users"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    username = Column(VARCHAR(255), nullable=False)
    joined = Column(DATETIME, nullable=False)
    kira_percentage = Column(Integer, nullable=True)
