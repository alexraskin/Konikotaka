from models.db import Base
from sqlalchemy import Column, Integer, VARCHAR


class Races(Base):
    """
    Race Model
    """

    __tablename__ = "racers"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    points = Column(Integer, nullable=False, default=0)
