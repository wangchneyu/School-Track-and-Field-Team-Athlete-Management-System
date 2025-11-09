"""Event schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    name: str
    type: str
    gender_limit: str = "all"
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    gender_limit: Optional[str] = None
    is_active: Optional[bool] = None


class EventRead(EventBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
