from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RatingCreate(BaseModel):
    """Payload for creating ratings."""

    athlete_id: int
    attitude: int
    attendance: int
    performance: int
    comment: Optional[str] = ""
    date: Optional[date] = None


class RatingRead(BaseModel):
    """Rating data returned to clients."""

    id: int
    athlete_id: int
    coach_id: int
    date: date
    attitude: int
    attendance: int
    performance: int
    comment: str

    model_config = ConfigDict(from_attributes=True)
