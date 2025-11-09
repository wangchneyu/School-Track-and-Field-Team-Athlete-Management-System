from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.score import Score
from app.models.user import User
from app.schemas.score import ScoreCreate, ScoreRead

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("", response_model=ScoreRead)
def add_score(
    data: ScoreCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> ScoreRead:
    """Add a new performance result."""

    score = Score(**data.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.get("", response_model=List[ScoreRead])
def list_scores(
    athlete_id: Optional[int] = None,
    event_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[ScoreRead]:
    """List scores with optional filters."""

    query = db.query(Score)
    if athlete_id:
        query = query.filter(Score.athlete_id == athlete_id)
    if event_id:
        query = query.filter(Score.event_id == event_id)
    return query.order_by(Score.recorded_at.desc()).all()


@router.get("/me", response_model=List[ScoreRead])
def my_scores(
    athlete: Athlete = Depends(deps.get_current_athlete),
    db: Session = Depends(deps.get_db),
) -> List[ScoreRead]:
    """Return scores belonging to the current athlete."""

    return (
        db.query(Score)
        .filter(Score.athlete_id == athlete.id)
        .order_by(Score.recorded_at.desc())
        .all()
    )
