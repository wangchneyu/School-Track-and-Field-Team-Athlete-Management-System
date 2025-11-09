from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Attendance(Base):
    """Attendance status for an athlete in a session."""

    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    status = Column(String(20), default="present")
    remark = Column(String(255), default="")
    recorded_by = Column(Integer, ForeignKey("users.id"))
    method = Column(String(20), default="manual")
    device_info = Column(String(255), default="")
    qr_token_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("TrainingSession", back_populates="attendances")
    athlete = relationship("Athlete", back_populates="attendances")
