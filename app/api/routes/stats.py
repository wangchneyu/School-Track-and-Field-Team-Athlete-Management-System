"""Administrative statistics endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.attendance import Attendance
from app.models.user import User
from app.schemas.stats import AttendanceStat, EventParticipationStat

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/attendance", response_model=List[AttendanceStat])
def attendance_stats(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[AttendanceStat]:
    """Return attendance rates per athlete."""

    attendance_case = case(
        (Attendance.status.in_(("present", "late", "leave")), 1),
        else_=0,
    )

    rows = (
        db.query(
            Athlete.id.label("athlete_id"),
            Athlete.name,
            Athlete.group,
            func.count(Attendance.id).label("recorded_sessions"),
            func.coalesce(func.sum(attendance_case), 0).label("attended_sessions"),
        )
        .outerjoin(Attendance, Attendance.athlete_id == Athlete.id)
        .group_by(Athlete.id)
        .order_by(Athlete.group, Athlete.name)
        .all()
    )

    stats: List[AttendanceStat] = []
    for row in rows:
        recorded = int(row.recorded_sessions or 0)
        attended = int(row.attended_sessions or 0)
        rate = round(attended / recorded, 2) if recorded else 0.0
        stats.append(
            AttendanceStat(
                athlete_id=row.athlete_id,
                name=row.name,
                group=row.group or "",
                recorded_sessions=recorded,
                attended_sessions=attended,
                attendance_rate=rate,
            )
        )
    return stats


@router.get("/events", response_model=List[EventParticipationStat])
def event_participation_stats(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[EventParticipationStat]:
    """Return how many athletes focus on each event."""

    rows = (
        db.query(Athlete.main_event, func.count(Athlete.id).label("athletes"))
        .group_by(Athlete.main_event)
        .all()
    )
    total = sum(row.athletes for row in rows) or 1
    stats: List[EventParticipationStat] = []
    for row in rows:
        label = row.main_event or "未设置"
        count = int(row.athletes)
        percentage = round(count / total, 2)
        stats.append(EventParticipationStat(event=label, athletes=count, percentage=percentage))
    return stats

