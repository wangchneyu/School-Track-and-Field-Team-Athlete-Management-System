from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SessionBase(BaseModel):
    """Shared training session fields."""

    date: date
    start_time: Optional[str] = ""
    end_time: Optional[str] = ""
    location: Optional[str] = ""
    description: Optional[str] = ""


class SessionCreate(SessionBase):
    """Payload for creating sessions."""

    pass


class SessionUpdate(BaseModel):
    """Payload for partially updating sessions."""

    date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class SessionRead(SessionBase):
    """Session data returned to clients."""

    id: int

    model_config = ConfigDict(from_attributes=True)
