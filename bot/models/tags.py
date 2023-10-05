from models.db import Base
from sqlalchemy import VARCHAR, Column, Integer, String


class CustomTags(Base):
    """
    Custom Tags Model
    """

    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(VARCHAR(2000), nullable=False)
    called = Column(Integer, nullable=False, default=0)
    date_added = Column(VARCHAR(255), nullable=False)
