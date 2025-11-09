from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import get_settings
from app.models.qr_code import QrCode
from app.models.training_session import TrainingSession
from app.models.user import User
from app.schemas.qr_code import QrCodeCreate, QrCodeRead
from app.schemas.training_session import SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])
settings = get_settings()


@router.post("", response_model=SessionRead)
def create_session(
    data: SessionCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> SessionRead:
    """Create a training session."""

    session = TrainingSession(**data.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=List[SessionRead])
def list_sessions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> List[SessionRead]:
    """List sessions within an optional date range."""

    query = db.query(TrainingSession)
    if start_date:
        query = query.filter(TrainingSession.date >= start_date)
    if end_date:
        query = query.filter(TrainingSession.date <= end_date)
    return query.order_by(TrainingSession.date.desc()).all()


@router.post("/{session_id}/qr", response_model=QrCodeRead)
def create_session_qr(
    session_id: int,
    data: QrCodeCreate,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.require_admin),
) -> QrCodeRead:
    """Generate a QR token for a specific session."""

    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    expires_at = datetime.utcnow() + timedelta(minutes=data.expire_minutes)
    token = uuid4().hex
    qr = QrCode(
        session_id=session.id,
        token=token,
        expires_at=expires_at,
        created_by=admin.id,
        note=data.note or "",
        use_limit=data.use_limit or 0,
    )
    db.add(qr)
    db.commit()
    db.refresh(qr)
    qr_url = f"{settings.FRONTEND_BASE_URL}/static/checkin.html?token={token}"
    start_label = f"{session.date} {session.start_time or ''}".strip()
    return QrCodeRead(
        id=qr.id,
        session_id=qr.session_id,
        token=qr.token,
        expires_at=qr.expires_at,
        created_at=qr.created_at,
        note=qr.note,
        use_limit=qr.use_limit,
        use_count=qr.use_count,
        qr_url=qr_url,
        session_location=session.location or "",
        session_start=start_label,
    )


@router.get("/{session_id}/qr", response_model=Optional[QrCodeRead])
def get_active_qr(
    session_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> Optional[QrCodeRead]:
    """Return the latest active QR token for a session."""

    now = datetime.utcnow()
    qr = (
        db.query(QrCode)
        .filter(QrCode.session_id == session_id)
        .order_by(QrCode.created_at.desc())
        .first()
    )
    if not qr or qr.expires_at < now:
        return None
    session = qr.session
    qr_url = f"{settings.FRONTEND_BASE_URL}/static/checkin.html?token={qr.token}"
    start_label = f"{session.date} {session.start_time or ''}".strip()
    return QrCodeRead(
        id=qr.id,
        session_id=qr.session_id,
        token=qr.token,
        expires_at=qr.expires_at,
        created_at=qr.created_at,
        note=qr.note,
        use_limit=qr.use_limit,
        use_count=qr.use_count,
        qr_url=qr_url,
        session_location=session.location or "",
        session_start=start_label,
    )
