from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.event import Event
from app.models.score import Score
from app.schemas.ranking import RankingItem
from app.services.rankings import build_rankings

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/{event_id}", response_model=List[RankingItem])
def get_rankings(
    event_id: int,
    db: Session = Depends(deps.get_db),
) -> List[RankingItem]:
    """Return rankings for a specific event."""

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    rows = (
        db.query(Score, Athlete)
        .join(Athlete, Score.athlete_id == Athlete.id)
        .filter(Score.event_id == event_id)
        .all()
    )
    return build_rankings(event, rows)
