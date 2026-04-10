"""Notification management API routes."""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.notification import Notification, NotificationRead as NotificationReadModel
from app.models.training_session import TrainingSession
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationReadDetail,
    NotificationReadStatus,
    NotificationUpdate,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _enrich_notification(
    notif: Notification,
    db: Session,
    current_user: Optional[User] = None,
) -> dict:
    """Build a rich notification dict with read status and session info."""
    data = {
        "id": notif.id,
        "title": notif.title,
        "content": notif.content,
        "type": notif.type,
        "priority": notif.priority,
        "target_group": notif.target_group or "",
        "session_id": notif.session_id,
        "created_by": notif.created_by,
        "created_at": notif.created_at,
        "is_active": notif.is_active,
        "creator_name": notif.creator.username if notif.creator else None,
    }

    # Session info
    if notif.session_id and notif.session:
        sess = notif.session
        data["session_date"] = str(sess.date) if sess.date else None
        data["session_location"] = sess.location or ""
        data["session_time"] = f"{sess.start_time or ''} - {sess.end_time or ''}".strip(" -")
    else:
        data["session_date"] = None
        data["session_location"] = None
        data["session_time"] = None

    # Read status for current user
    if current_user:
        read_record = (
            db.query(NotificationReadModel)
            .filter(
                NotificationReadModel.notification_id == notif.id,
                NotificationReadModel.user_id == current_user.id,
            )
            .first()
        )
        data["is_read"] = read_record is not None
        data["read_at"] = read_record.read_at if read_record else None
    else:
        data["is_read"] = False
        data["read_at"] = None

    # Read count
    read_count = (
        db.query(NotificationReadModel)
        .filter(NotificationReadModel.notification_id == notif.id)
        .count()
    )
    data["read_count"] = read_count

    # Total target count
    target_query = db.query(Athlete)
    if notif.target_group:
        target_query = target_query.filter(Athlete.group == notif.target_group)
    data["total_target"] = target_query.count()

    return data


# ---- Admin endpoints ----


@router.post("", response_model=NotificationRead)
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.require_admin),
) -> dict:
    """Create a new notification (admin only)."""
    notif = Notification(
        **data.model_dump(),
        created_by=admin.id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return _enrich_notification(notif, db, admin)


@router.get("", response_model=List[NotificationRead])
def list_notifications(
    type: Optional[str] = Query(None, description="Filter by type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    active_only: bool = Query(True, description="Only active notifications"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[dict]:
    """List notifications. Admins see all, athletes see targeted ones."""
    query = db.query(Notification)

    if active_only:
        query = query.filter(Notification.is_active == True)

    if type:
        query = query.filter(Notification.type == type)
    if priority:
        query = query.filter(Notification.priority == priority)

    # Athletes only see notifications targeted to them
    if current_user.role == "athlete":
        athlete = db.query(Athlete).filter(Athlete.user_id == current_user.id).first()
        if athlete:
            from sqlalchemy import or_

            query = query.filter(
                or_(
                    Notification.target_group == "",
                    Notification.target_group == None,
                    Notification.target_group == athlete.group,
                )
            )
        else:
            query = query.filter(
                or_(
                    Notification.target_group == "",
                    Notification.target_group == None,
                )
            )

    notifications = (
        query.order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_enrich_notification(n, db, current_user) for n in notifications]


@router.get("/me/unread-count")
def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """Get unread notification count for current user."""
    from sqlalchemy import or_

    query = db.query(Notification).filter(Notification.is_active == True)

    # Filter by target group for athletes
    if current_user.role == "athlete":
        athlete = db.query(Athlete).filter(Athlete.user_id == current_user.id).first()
        if athlete:
            query = query.filter(
                or_(
                    Notification.target_group == "",
                    Notification.target_group == None,
                    Notification.target_group == athlete.group,
                )
            )
        else:
            query = query.filter(
                or_(
                    Notification.target_group == "",
                    Notification.target_group == None,
                )
            )

    # Get IDs of read notifications
    read_ids = [
        r[0]
        for r in db.query(NotificationReadModel.notification_id)
        .filter(NotificationReadModel.user_id == current_user.id)
        .all()
    ]

    if read_ids:
        query = query.filter(~Notification.id.in_(read_ids))

    return {"unread_count": query.count()}


@router.get("/today-training", response_model=List[NotificationRead])
def get_today_training_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[dict]:
    """Get today's training notifications for the current user."""
    from sqlalchemy import or_

    today = date.today()

    # Find training sessions for today
    today_sessions = db.query(TrainingSession).filter(TrainingSession.date == today).all()
    session_ids = [s.id for s in today_sessions]

    # Find notifications linked to today's sessions, or training type created today
    query = db.query(Notification).filter(
        Notification.is_active == True,
        or_(
            Notification.session_id.in_(session_ids) if session_ids else False,
            (Notification.type == "training")
            & (Notification.created_at >= datetime.combine(today, datetime.min.time())),
        ),
    )

    # Filter by group for athletes
    if current_user.role == "athlete":
        athlete = db.query(Athlete).filter(Athlete.user_id == current_user.id).first()
        if athlete:
            query = query.filter(
                or_(
                    Notification.target_group == "",
                    Notification.target_group == None,
                    Notification.target_group == athlete.group,
                )
            )

    notifications = query.order_by(Notification.created_at.desc()).all()
    return [_enrich_notification(n, db, current_user) for n in notifications]


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """Get a single notification."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return _enrich_notification(notif, db, current_user)


@router.get("/{notification_id}/read-status", response_model=NotificationReadDetail)
def get_notification_read_status(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.require_admin),
) -> dict:
    """Get detailed read status for a notification (admin only)."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    data = _enrich_notification(notif, db, admin)

    # Get read users
    read_records = (
        db.query(NotificationReadModel)
        .filter(NotificationReadModel.notification_id == notification_id)
        .all()
    )
    read_user_ids = set()
    read_users = []
    for record in read_records:
        user = db.query(User).filter(User.id == record.user_id).first()
        if user:
            read_user_ids.add(user.id)
            read_users.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "read_at": record.read_at,
                }
            )
    data["read_users"] = read_users

    # Get unread users (athletes in target group)
    target_query = db.query(Athlete)
    if notif.target_group:
        target_query = target_query.filter(Athlete.group == notif.target_group)
    target_athletes = target_query.all()

    unread_users = []
    for athlete in target_athletes:
        if athlete.user_id not in read_user_ids:
            unread_users.append(
                {
                    "user_id": athlete.user_id,
                    "username": athlete.student_id,
                    "name": athlete.name,
                }
            )
    data["unread_users"] = unread_users

    return data


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """Mark a notification as read by the current user."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Check if already read
    existing = (
        db.query(NotificationReadModel)
        .filter(
            NotificationReadModel.notification_id == notification_id,
            NotificationReadModel.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        return {"message": "Already marked as read", "read_at": existing.read_at}

    read_record = NotificationReadModel(
        notification_id=notification_id,
        user_id=current_user.id,
    )
    db.add(read_record)
    db.commit()
    db.refresh(read_record)
    return {"message": "Marked as read", "read_at": read_record.read_at}


@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """Mark all notifications as read for the current user."""
    from sqlalchemy import or_

    query = db.query(Notification).filter(Notification.is_active == True)

    if current_user.role == "athlete":
        athlete = db.query(Athlete).filter(Athlete.user_id == current_user.id).first()
        if athlete:
            query = query.filter(
                or_(
                    Notification.target_group == "",
                    Notification.target_group == None,
                    Notification.target_group == athlete.group,
                )
            )

    notifications = query.all()
    count = 0
    for notif in notifications:
        existing = (
            db.query(NotificationReadModel)
            .filter(
                NotificationReadModel.notification_id == notif.id,
                NotificationReadModel.user_id == current_user.id,
            )
            .first()
        )
        if not existing:
            db.add(
                NotificationReadModel(
                    notification_id=notif.id,
                    user_id=current_user.id,
                )
            )
            count += 1

    db.commit()
    return {"message": f"Marked {count} notifications as read", "count": count}


@router.put("/{notification_id}", response_model=NotificationRead)
def update_notification(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.require_admin),
) -> dict:
    """Update a notification (admin only)."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(notif, field, value)

    db.commit()
    db.refresh(notif)
    return _enrich_notification(notif, db, admin)


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete a notification (admin only)."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return None
