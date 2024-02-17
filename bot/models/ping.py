from models.db import Base
from sqlalchemy import DATE, Column, Integer  # type: ignore


class Ping(Base):
    """
    Ping Model

    Attributes:
    - id: int
        The primary key of the table
    - ping_ws: int
        The ping of the websocket
    - ping_rest: int
        The ping of the rest api
    - date: str
        The date the ping was recorded
    """

    __tablename__ = "ping"
    id = Column(Integer, primary_key=True)
    ping_ws = Column(Integer, nullable=False)
    ping_rest = Column(Integer, nullable=False)
    date = Column(DATE, nullable=False)
