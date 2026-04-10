"""Statistical data schemas."""

from datetime import datetime
from typing import List, Optional

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


class AthleteCheckinDetail(BaseModel):
    """Individual athlete check-in detail within a session."""

    athlete_id: int
    name: str
    student_id: str
    group: str
    status: str  # present / late / absent / leave / unchecked
    method: Optional[str] = None  # qr / manual / None
    checkin_time: Optional[datetime] = None


class SessionAttendanceStat(BaseModel):
    """Attendance statistics for a single training session."""

    session_id: int
    session_date: str
    start_time: str
    end_time: str
    location: str
    total_athletes: int
    present_count: int
    late_count: int
    absent_count: int
    leave_count: int
    unchecked_count: int
    attendance_rate: float
    athletes: List[AthleteCheckinDetail]


class DailyAttendanceSummary(BaseModel):
    """Aggregated daily attendance statistics across all sessions."""

    date: str
    total_sessions: int
    total_athletes: int
    present_count: int
    late_count: int
    absent_count: int
    leave_count: int
    unchecked_count: int
    attendance_rate: float
    sessions: List[SessionAttendanceStat]

