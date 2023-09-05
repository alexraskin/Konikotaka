from models.db import Base
from sqlalchemy import Column, Integer, DATETIME, VARCHAR


class DiscordUser(Base):
    __tablename__ = "discord_users"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    username = Column(VARCHAR(255), nullable=False)
    joined = Column(DATETIME, nullable=False)
