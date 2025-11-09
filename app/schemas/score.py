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

    model_config = ConfigDict(from_attributes=True)
