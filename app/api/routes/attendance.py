from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.attendance import Attendance
from app.models.qr_code import QrCode
from app.models.user import User
from app.schemas.attendance import AttendanceCreate, AttendanceRead
from app.schemas.qr_code import QrCheckinInfo, QrCheckinRequest

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("", response_model=AttendanceRead)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.require_admin),
) -> AttendanceRead:
    """Create a new attendance record."""

    payload = data.model_dump()
    if not payload.get("recorded_by"):
        payload["recorded_by"] = admin.id
    attendance = Attendance(**payload)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("", response_model=List[AttendanceRead])
def list_attendance(
    session_id: Optional[int] = None,
    athlete_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[AttendanceRead]:
    """List attendance records with optional filters."""

    query = db.query(Attendance)
    if session_id:
        query = query.filter(Attendance.session_id == session_id)
    if athlete_id:
        query = query.filter(Attendance.athlete_id == athlete_id)
    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time())
        query = query.filter(Attendance.created_at >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Attendance.created_at <= end_dt)
    return query.order_by(Attendance.created_at.desc()).all()


@router.get("/me", response_model=List[AttendanceRead])
def my_attendance(
    athlete: Athlete = Depends(deps.get_current_athlete),
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[AttendanceRead]:
    """Return the current athlete's attendance history."""

    query = db.query(Attendance).filter(Attendance.athlete_id == athlete.id)
    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time())
        query = query.filter(Attendance.created_at >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Attendance.created_at <= end_dt)
    return query.order_by(Attendance.created_at.desc()).all()


@router.post("/qr-checkin", response_model=AttendanceRead)
def qr_checkin(
    payload: QrCheckinRequest,
    db: Session = Depends(deps.get_db),
    athlete: Athlete = Depends(deps.get_current_athlete),
) -> AttendanceRead:
    """Allow athletes to check in by scanning a QR token."""

    qr = db.query(QrCode).filter(QrCode.token == payload.token).first()
    if not qr:
        raise HTTPException(status_code=404, detail="签到二维码不存在")
    if qr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="签到二维码已过期")
    if qr.use_limit and qr.use_count >= qr.use_limit:
        raise HTTPException(status_code=400, detail="该二维码已达到签到上限")

    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.session_id == qr.session_id,
            Attendance.athlete_id == athlete.id,
        )
        .first()
    )

    if attendance:
        attendance.status = "present"
        attendance.method = "qr"
        attendance.qr_token_id = qr.id
        attendance.device_info = payload.device_info or ""
        attendance.recorded_by = qr.created_by
    else:
        attendance = Attendance(
            session_id=qr.session_id,
            athlete_id=athlete.id,
            status="present",
            method="qr",
            device_info=payload.device_info or "",
            recorded_by=qr.created_by,
            qr_token_id=qr.id,
            remark="二维码签到",
        )
        db.add(attendance)

    qr.use_count += 1
    db.add(qr)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/qr-checkin/{token}", response_model=QrCheckinInfo)
def qr_checkin_info(token: str, db: Session = Depends(deps.get_db)) -> QrCheckinInfo:
    """Provide session details for a QR token (public endpoint)."""

    qr = db.query(QrCode).filter(QrCode.token == token).first()
    if not qr or qr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=404, detail="二维码已失效")
    session = qr.session
    start_label = f"{session.date} {session.start_time or ''}".strip()
    return QrCheckinInfo(
        session_location=session.location or "",
        session_start=start_label,
        expires_at=qr.expires_at,
        note=qr.note or "",
    )
