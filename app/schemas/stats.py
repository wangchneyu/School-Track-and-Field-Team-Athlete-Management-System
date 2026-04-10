"""Statistical data schemas."""

from pydantic import BaseModel


class AttendanceStat(BaseModel):
    athlete_id: int
    name: str
    group: str
    recorded_sessions: int
    attended_sessions: int
    attendance_rate: float


class EventParticipationStat(BaseModel):
    event: str
    athletes: int
    percentage: float

