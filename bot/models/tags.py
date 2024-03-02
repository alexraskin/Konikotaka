from models.db import Base
from sqlalchemy import BIGINT, VARCHAR, Column, Integer, String


class CustomTags(Base):
    """
    Custom Tags Model

    Attributes:
    - id: int
        The primary key of the table
    - discord_id: str
        The discord id of the user who added the tag
    - name: str
        The name of the tag
    - location_id: int
        The location id of the tag
    - content: str
        The content of the tag
    - called: int
        The number of times the tag has been called
    - date_added: str
        The date the tag was added
    """

    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    discord_id = Column(VARCHAR(255), nullable=False)
    name = Column(String(255), nullable=False)
    location_id = Column(BIGINT, nullable=False)
    content = Column(VARCHAR(2000), nullable=False)
    called = Column(Integer, nullable=False, default=0)
    date_added = Column(VARCHAR(255), nullable=False)
