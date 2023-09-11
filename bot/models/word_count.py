from models.db import Base
from sqlalchemy import BIGINT, VARCHAR, Column, Integer


class WordCount(Base):
    """
    Word Count Model
    """

    __tablename__ = "word_count"
    id = Column(Integer, primary_key=True)
    word = Column(VARCHAR(255), nullable=False)
    count = Column(BIGINT, nullable=False, default=0)
    discord_id = Column(VARCHAR(25), nullable=False)
