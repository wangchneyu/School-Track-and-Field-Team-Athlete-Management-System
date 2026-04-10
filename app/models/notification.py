"""Notification system models for training alerts and announcements."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class Notification(Base):
    """A notification sent by admin to athletes."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(
        String(30), nullable=False, default="general", index=True
    )  # training, announcement, general
    priority = Column(
        String(20), nullable=False, default="normal"
    )  # low, normal, high, urgent
    target_group = Column(
        String(50), default=""
    )  # empty = all, or specific group like "短跑组"
    session_id = Column(
        Integer, ForeignKey("sessions.id"), nullable=True
    )  # linked training session
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    read_statuses = relationship(
        "NotificationRead", back_populates="notification", cascade="all, delete-orphan"
    )
    session = relationship("TrainingSession", foreign_keys=[session_id])
    creator = relationship("User", foreign_keys=[created_by])


class NotificationRead(Base):
    """Tracks which users have read which notifications."""

    __tablename__ = "notification_reads"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(
        Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    read_at = Column(DateTime, default=datetime.utcnow)

    notification = relationship("Notification", back_populates="read_statuses")
    user = relationship("User", foreign_keys=[user_id])
