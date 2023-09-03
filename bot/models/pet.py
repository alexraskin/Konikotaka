from sqlalchemy import Column, Integer, String
from models.db import Base


class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, nullable=False)
    pet_name = Column(String(50), nullable=False)
    hunger = Column(Integer, nullable=False, default=0)
    happiness = Column(Integer, nullable=False, default=0)
    treat_count = Column(Integer, nullable=False, default=0)
