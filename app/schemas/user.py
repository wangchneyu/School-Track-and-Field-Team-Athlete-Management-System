"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    role: str = "athlete"
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
