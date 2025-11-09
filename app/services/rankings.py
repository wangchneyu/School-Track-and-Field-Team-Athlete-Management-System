from typing import Dict, Iterable, List, Tuple

from app.models.athlete import Athlete
from app.models.event import Event
from app.models.score import Score


def build_rankings(event: Event, rows: Iterable[Tuple[Score, Athlete]]) -> List[Dict]:
    """Return a sorted ranking list for the provided event."""

    best: Dict[int, Tuple[float, Athlete]] = {}
    for score, athlete in rows:
        current = best.get(athlete.id)
        if current is None:
            best[athlete.id] = (score.performance, athlete)
            continue
        previous_performance = current[0]
        if event.type == "time":
            if score.performance < previous_performance:
                best[athlete.id] = (score.performance, athlete)
        else:
            if score.performance > previous_performance:
                best[athlete.id] = (score.performance, athlete)

    reverse = event.type == "distance"
    sorted_rows = sorted(best.values(), key=lambda item: item[0], reverse=reverse)
    payload: List[Dict] = []
    for idx, (performance, athlete) in enumerate(sorted_rows, start=1):
        payload.append(
            {
                "rank": idx,
                "athlete_id": athlete.id,
                "name": athlete.name,
                "group": athlete.group,
                "best_performance": performance,
            }
        )
    return payload
