from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Rating(Base):
    """Coach evaluation for an athlete on a specific date."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today)
    attitude = Column(Integer, nullable=False)
    attendance = Column(Integer, nullable=False)
    performance = Column(Integer, nullable=False)
    comment = Column(String(255), default="")

    athlete = relationship("Athlete", back_populates="ratings")
