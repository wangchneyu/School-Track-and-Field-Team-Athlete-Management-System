from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Score(Base):
    """Performance measurement recorded for an athlete."""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    performance = Column(Float, nullable=False)
    is_official = Column(Boolean, default=True)
    remark = Column(String(255), default="")
    recorded_at = Column(DateTime, default=datetime.utcnow)

    athlete = relationship("Athlete", back_populates="scores")
    event = relationship("Event")
