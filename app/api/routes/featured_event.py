"""Endpoints for the homepage featured event countdown."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.featured_event import FeaturedEvent
from app.models.user import User
from app.schemas.featured_event import FeaturedEventCreate, FeaturedEventRead

router = APIRouter(prefix="/featured-event", tags=["featured-event"])


def _build_response(event: FeaturedEvent) -> FeaturedEventRead:
    payload = FeaturedEventRead.model_validate(event, from_attributes=True)
    now = datetime.now(timezone.utc)
    diff = event.start_time.astimezone(timezone.utc) - now
    countdown_seconds = max(int(diff.total_seconds()), 0)
    countdown_days = round(countdown_seconds / 86400, 2)
    return payload.model_copy(update={"countdown_seconds": countdown_seconds, "countdown_days": countdown_days})


@router.get("", response_model=Optional[FeaturedEventRead])
def get_featured_event(db: Session = Depends(deps.get_db)) -> Optional[FeaturedEventRead]:
    """Return the current featured event for the homepage countdown."""

    event = db.query(FeaturedEvent).order_by(FeaturedEvent.start_time.asc()).first()
    if not event:
        return None
    return _build_response(event)


@router.put("", response_model=FeaturedEventRead)
def upsert_featured_event(
    data: FeaturedEventCreate,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.require_admin),
) -> FeaturedEventRead:
    """Create or update the featured event shown on the homepage."""

    event = db.query(FeaturedEvent).first()
    if event:
        for field, value in data.model_dump().items():
            setattr(event, field, value)
        event.updated_by = admin.id
    else:
        event = FeaturedEvent(**data.model_dump(), updated_by=admin.id)
        db.add(event)
    db.commit()
    db.refresh(event)
    return _build_response(event)

