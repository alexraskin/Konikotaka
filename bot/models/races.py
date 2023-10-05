from models.db import Base
from sqlalchemy import Column, Integer, BigInteger


class Races(Base):
    """
    Race Model
    """

    __tablename__ = "racers"
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    points = Column(Integer, nullable=False, default=0)
