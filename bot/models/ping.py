from models.db import Base
from sqlalchemy import DATE, Column, Integer


class Ping(Base):
    """
    Ping Model
    """

    __tablename__ = "ping"
    id = Column(Integer, primary_key=True)
    ping_ws = Column(Integer, nullable=False)
    ping_rest = Column(Integer, nullable=False)
    date = Column(DATE, nullable=False)
