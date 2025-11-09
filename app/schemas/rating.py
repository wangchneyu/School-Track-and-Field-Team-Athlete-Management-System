from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RatingCreate(BaseModel):
    """Payload for creating ratings."""

    athlete_id: int
    date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format")
    attitude: int
    attendance: int
    performance: int
    comment: Optional[str] = ""


class RatingUpdate(BaseModel):
    """Payload for partially updating ratings."""

    athlete_id: Optional[int] = None
    date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format")
    attitude: Optional[int] = None
    attendance: Optional[int] = None
    performance: Optional[int] = None
    comment: Optional[str] = None


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
    athlete_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
