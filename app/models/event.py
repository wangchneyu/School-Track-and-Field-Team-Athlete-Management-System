from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Event(Base):
    """Track & field event definition."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)
    gender_limit = Column(String(10), default="all")
