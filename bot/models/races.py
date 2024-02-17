from models.db import Base
from sqlalchemy import BIGINT, VARCHAR, Column, Integer  # type: ignore


class Races(Base):
    """
    Race Model

    Attributes:
    - id: int
        The primary key of the table
    - discord_id: str
        The discord id of the user who is the race
    - location_id: int
        The guild id of the user
    - wins: int
        The number of wins the user has
    - points: int
        The number of points the user has
    """

    __tablename__ = "racers"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    location_id = Column(BIGINT, nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    points = Column(Integer, nullable=False, default=0)
