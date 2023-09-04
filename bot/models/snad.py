from models.db import Base
from sqlalchemy import Column, Integer, DATETIME


class SnadCounter(Base):
    __tablename__ = "snad"
    id = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False, default=0)
    caught = Column(DATETIME, nullable=False)
