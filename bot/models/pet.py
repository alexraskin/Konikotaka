from models.db import Base
from sqlalchemy import Column, Integer, String, VARCHAR


class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(18), nullable=False)
    pet_name = Column(String(50), nullable=False)
    hunger = Column(Integer, nullable=False, default=0)
    happiness = Column(Integer, nullable=False, default=0)
    treat_count = Column(Integer, nullable=False, default=0)
