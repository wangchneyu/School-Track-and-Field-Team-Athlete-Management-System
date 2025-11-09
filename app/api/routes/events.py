from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventCreate, EventRead

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
