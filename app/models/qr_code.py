from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class QrCode(Base):
    """Temporary QR token for session check-in."""

    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String(255), default="")
    use_limit = Column(Integer, default=0)  # 0 means unlimited
    use_count = Column(Integer, default=0)

    session = relationship("TrainingSession", back_populates="qr_codes")
    attendances = relationship("Attendance", backref="qr_token")
