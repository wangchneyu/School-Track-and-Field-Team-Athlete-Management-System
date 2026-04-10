from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttendanceBase(BaseModel):
    """Shared attendance fields."""

    session_id: int
    athlete_id: int
    status: str = "present"
    remark: Optional[str] = ""
    method: str = "manual"
    device_info: Optional[str] = ""
    qr_token_id: Optional[int] = None


class AttendanceCreate(AttendanceBase):
    """Payload for creating attendance records."""

    recorded_by: Optional[int] = None


class AttendanceUpdate(BaseModel):
    """Partial update for attendance records."""

    session_id: Optional[int] = None
    athlete_id: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None
    method: Optional[str] = None
    device_info: Optional[str] = None
    qr_token_id: Optional[int] = None
    recorded_by: Optional[int] = None


class AttendanceRead(AttendanceBase):
    """Attendance data returned to clients."""

    id: int
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    athlete_name: Optional[str] = None
    session_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
