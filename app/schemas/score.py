from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ScoreCreate(BaseModel):
    """Payload for creating scores."""

    athlete_id: int
    event_id: int
    performance: float
    is_official: bool = True
    remark: Optional[str] = ""


class ScoreRead(BaseModel):
    """Score data returned to clients."""

    id: int
    athlete_id: int
    event_id: int
    performance: float
    is_official: bool
    remark: str
    recorded_at: datetime
    athlete_name: Optional[str] = None
    event_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ScoreUpdate(BaseModel):
    """Payload for updating scores."""

    athlete_id: Optional[int] = None
    event_id: Optional[int] = None
    performance: Optional[float] = None
    is_official: Optional[bool] = None
    remark: Optional[str] = None
