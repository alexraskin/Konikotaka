from models.db import Base
from sqlalchemy import Column, Integer, VARCHAR, String


class CustomTags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content = Column(VARCHAR(1000), nullable=False)
    discord_id = Column(VARCHAR(25), nullable=False)
