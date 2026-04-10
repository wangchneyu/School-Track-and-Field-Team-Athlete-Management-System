"""Administrative statistics endpoints."""

from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.attendance import Attendance
from app.models.training_session import TrainingSession
from app.models.user import User
from app.schemas.stats import (
    AthleteCheckinDetail,
    AttendanceStat,
    DailyAttendanceSummary,
    EventParticipationStat,
    SessionAttendanceStat,
)

router = APIRouter(prefix="/stats", tags=["stats"])


def _build_session_attendance_stat(
    session: TrainingSession,
    all_athletes: List[Athlete],
    db: Session,
) -> SessionAttendanceStat:
    """Build attendance statistics for a single training session."""

    attendance_records = (
        db.query(Attendance)
        .filter(Attendance.session_id == session.id)
        .all()
    )
    attendance_map = {a.athlete_id: a for a in attendance_records}

    athletes_detail: List[AthleteCheckinDetail] = []
    present_count = 0
    late_count = 0
    absent_count = 0
    leave_count = 0
    unchecked_count = 0

    for athlete in all_athletes:
        record = attendance_map.get(athlete.id)
        if record:
            status = record.status
            method = record.method
            checkin_time = record.created_at
            if status == "present":
                present_count += 1
            elif status == "late":
                late_count += 1
            elif status == "absent":
                absent_count += 1
            elif status == "leave":
                leave_count += 1
        else:
            status = "unchecked"
            method = None
            checkin_time = None
            unchecked_count += 1

        athletes_detail.append(
            AthleteCheckinDetail(
                athlete_id=athlete.id,
                name=athlete.name,
                student_id=athlete.student_id,
                group=athlete.group or "",
                status=status,
                method=method,
                checkin_time=checkin_time,
            )
        )

    total = len(all_athletes)
    attended = present_count + late_count
    rate = round(attended / total, 2) if total else 0.0

    return SessionAttendanceStat(
        session_id=session.id,
        session_date=str(session.date),
        start_time=session.start_time or "",
        end_time=session.end_time or "",
        location=session.location or "",
        total_athletes=total,
        present_count=present_count,
        late_count=late_count,
        absent_count=absent_count,
        leave_count=leave_count,
        unchecked_count=unchecked_count,
        attendance_rate=rate,
        athletes=athletes_detail,
    )


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


@router.get("/daily-attendance", response_model=DailyAttendanceSummary)
def daily_attendance_stats(
    target_date: Optional[date_type] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> DailyAttendanceSummary:
    """Return aggregated attendance statistics for a specific date (defaults to today)."""

    if target_date is None:
        target_date = date_type.today()

    sessions = (
        db.query(TrainingSession)
        .filter(TrainingSession.date == target_date)
        .order_by(TrainingSession.start_time)
        .all()
    )

    all_athletes = db.query(Athlete).order_by(Athlete.group, Athlete.name).all()

    session_stats: List[SessionAttendanceStat] = []
    total_present = 0
    total_late = 0
    total_absent = 0
    total_leave = 0
    total_unchecked = 0

    for session in sessions:
        stat = _build_session_attendance_stat(session, all_athletes, db)
        session_stats.append(stat)
        total_present += stat.present_count
        total_late += stat.late_count
        total_absent += stat.absent_count
        total_leave += stat.leave_count
        total_unchecked += stat.unchecked_count

    total_athletes = len(all_athletes)
    total_attended = total_present + total_late
    total_slots = total_athletes * len(sessions) if sessions else 0
    rate = round(total_attended / total_slots, 2) if total_slots else 0.0

    return DailyAttendanceSummary(
        date=str(target_date),
        total_sessions=len(sessions),
        total_athletes=total_athletes,
        present_count=total_present,
        late_count=total_late,
        absent_count=total_absent,
        leave_count=total_leave,
        unchecked_count=total_unchecked,
        attendance_rate=rate,
        sessions=session_stats,
    )


@router.get("/session-attendance/{session_id}", response_model=SessionAttendanceStat)
def session_attendance_stats(
    session_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> SessionAttendanceStat:
    """Return attendance statistics for a specific training session."""

    from fastapi import HTTPException

    session = (
        db.query(TrainingSession)
        .filter(TrainingSession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="训练课次不存在")

    all_athletes = db.query(Athlete).order_by(Athlete.group, Athlete.name).all()
    return _build_session_attendance_stat(session, all_athletes, db)

