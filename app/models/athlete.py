from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Athlete(Base):
    """Athlete profile linked to a user account."""

    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False, index=True)
    student_id = Column(String(30), unique=True, nullable=False, index=True)
    gender = Column(String(10), nullable=False)
    group = Column(String(30), default="")
    main_event = Column(String(30), default="")
    phone = Column(String(30), default="")

    user = relationship("User", back_populates="athlete")
    scores = relationship("Score", back_populates="athlete")
    attendances = relationship("Attendance", back_populates="athlete")
    ratings = relationship("Rating", back_populates="athlete")
