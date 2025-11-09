"""SQLAlchemy models exported for Alembic and runtime usage."""

from app.models.attendance import Attendance
from app.models.athlete import Athlete
from app.models.event import Event
from app.models.featured_event import FeaturedEvent
from app.models.rating import Rating
from app.models.score import Score
from app.models.training_session import TrainingSession
from app.models.user import User
from app.models.qr_code import QrCode

__all__ = [
    "Attendance",
    "Athlete",
    "Event",
    "FeaturedEvent",
    "Rating",
    "Score",
    "TrainingSession",
    "User",
    "QrCode",
]
