from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.event import Event
from app.models.score import Score
from app.models.user import User
from app.schemas.score import ScoreCreate, ScoreRead, ScoreUpdate

router = APIRouter(prefix="/scores", tags=["scores"])


def _enrich_scores(scores: list, db: Session) -> List[dict]:
    """Add athlete_name and event_name to score records."""
    athlete_ids = {s.athlete_id for s in scores}
    event_ids = {s.event_id for s in scores}
    athletes = {a.id: a.name for a in db.query(Athlete).filter(Athlete.id.in_(athlete_ids)).all()} if athlete_ids else {}
    events = {e.id: e.name for e in db.query(Event).filter(Event.id.in_(event_ids)).all()} if event_ids else {}
    result = []
    for s in scores:
        d = ScoreRead.model_validate(s).model_dump()
        d["athlete_name"] = athletes.get(s.athlete_id, "")
        d["event_name"] = events.get(s.event_id, "")
        result.append(d)
    return result


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


@router.get("")
def list_scores(
    athlete_id: Optional[int] = None,
    event_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[dict]:
    """List scores with optional filters."""

    query = db.query(Score)
    if athlete_id:
        query = query.filter(Score.athlete_id == athlete_id)
    if event_id:
        query = query.filter(Score.event_id == event_id)
    scores = query.order_by(Score.recorded_at.desc()).all()
    return _enrich_scores(scores, db)


@router.get("/me")
def my_scores(
    athlete: Athlete = Depends(deps.get_current_athlete),
    db: Session = Depends(deps.get_db),
) -> List[dict]:
    """Return scores belonging to the current athlete."""

    scores = (
        db.query(Score)
        .filter(Score.athlete_id == athlete.id)
        .order_by(Score.recorded_at.desc())
        .all()
    )
    return _enrich_scores(scores, db)


@router.put("/{score_id}", response_model=ScoreRead)
def update_score(
    score_id: int,
    data: ScoreUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> ScoreRead:
    """Update an existing performance result."""

    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(score, field, value)
    db.commit()
    db.refresh(score)
    return score


@router.delete("/{score_id}", status_code=204)
def delete_score(
    score_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete a score record."""

    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    db.delete(score)
    db.commit()
    return None
