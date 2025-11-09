from pydantic import BaseModel


class RankingItem(BaseModel):
    """Single row of an event ranking."""

    rank: int
    athlete_id: int
    name: str
    group: str
    best_performance: float
