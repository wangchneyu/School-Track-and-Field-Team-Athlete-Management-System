"""Athlete schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class AthleteBase(BaseModel):
    name: str
    student_id: str
    gender: str
    group: Optional[str] = ""
    main_event: Optional[str] = ""
    phone: Optional[str] = ""


class AthleteCreate(AthleteBase):
    password: Optional[str] = None
    username: Optional[str] = None


class AthleteUpdate(BaseModel):
    name: Optional[str] = None
    student_id: Optional[str] = None
    gender: Optional[str] = None
    group: Optional[str] = None
    main_event: Optional[str] = None
    phone: Optional[str] = None


class AthleteRead(AthleteBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
