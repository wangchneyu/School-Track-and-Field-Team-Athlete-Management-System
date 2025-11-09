"""Featured event schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FeaturedEventBase(BaseModel):
    name: str
    start_time: datetime
    location: Optional[str] = ""
    description: Optional[str] = ""


class FeaturedEventCreate(FeaturedEventBase):
    pass


class FeaturedEventRead(FeaturedEventBase):
    id: int
    updated_by: Optional[int] = None
    updated_at: datetime
    countdown_seconds: int = 0
    countdown_days: float = 0.0

    model_config = ConfigDict(from_attributes=True)

