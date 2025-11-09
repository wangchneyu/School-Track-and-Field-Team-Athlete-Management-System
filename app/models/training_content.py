"""Training content model for athlete training plans."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TrainingContent(Base):
    """Training content/plan for athletes."""

    __tablename__ = "training_contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, comment="训练标题")
    content = Column(Text, nullable=False, comment="训练内容详情")
    category = Column(String(50), default="", comment="训练类别(力量/速度/耐力等)")
    target_group = Column(String(50), default="", comment="目标训练组")
    duration = Column(Integer, default=60, comment="预计时长(分钟)")
    intensity = Column(String(20), default="medium", comment="强度(low/medium/high)")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    creator = relationship("User", backref="training_contents")
