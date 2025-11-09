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


class SessionRead(SessionBase):
    """Session data returned to clients."""

    id: int

    model_config = ConfigDict(from_attributes=True)
