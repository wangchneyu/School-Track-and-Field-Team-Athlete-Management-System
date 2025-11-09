from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class TrainingSession(Base):
    """Scheduled training session for attendance tracking."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(String(10), default="")
    end_time = Column(String(10), default="")
    location = Column(String(50), default="")
    description = Column(String(255), default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    attendances = relationship("Attendance", back_populates="session")
    qr_codes = relationship("QrCode", back_populates="session")
