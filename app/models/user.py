from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """System account that can be either an admin or athlete."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), index=True, nullable=False, default="athlete")
    is_active = Column(Boolean, default=True)

    athlete = relationship("Athlete", back_populates="user", uselist=False)
