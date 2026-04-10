from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.event import Event
from app.models.score import Score
from app.models.user import User
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead)
def create_event(
    data: EventCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> EventRead:
    """Create a new track & field event."""

    if data.type not in ("time", "distance"):
        raise HTTPException(status_code=400, detail="type must be 'time' or 'distance'")
    if db.query(Event).filter(Event.name == data.name).first():
        raise HTTPException(status_code=400, detail="Event name already exists")
    event = Event(name=data.name, type=data.type, gender_limit=data.gender_limit)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=List[EventRead])
def list_events(
    db: Session = Depends(deps.get_db),
) -> List[EventRead]:
    """Return all configured events."""

    return db.query(Event).order_by(Event.name).all()


@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> EventRead:
    """Update an existing event."""

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    payload = data.model_dump(exclude_unset=True)
    for field in ("name", "type", "gender_limit"):
        if field in payload and payload[field] is not None:
            setattr(event, field, payload[field])
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete an event definition when unused by scores."""

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if db.query(Score).filter(Score.event_id == event_id).count():
        raise HTTPException(status_code=400, detail="存在关联成绩记录，无法删除该项目")
    db.delete(event)
    db.commit()
    return None
