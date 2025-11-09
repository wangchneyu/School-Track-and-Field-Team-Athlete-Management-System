"""Seed the database with an initial admin user and sample athletics data."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy.orm import Session

# Ensure the project root is on sys.path when running as standalone script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import models  # noqa: F401  # Import for metadata registration
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.athlete import Athlete
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.featured_event import FeaturedEvent
from app.models.rating import Rating
from app.models.score import Score
from app.models.training_session import TrainingSession
from app.models.user import User


def get_or_create_user(db: Session, username: str, role: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(username=username, role=role, password_hash=get_password_hash(password))
    db.add(user)
    db.flush()
    return user


def get_or_create_event(db: Session, name: str, type_: str) -> Event:
    event = db.query(Event).filter(Event.name == name).first()
    if event:
        return event
    event = Event(name=name, type=type_)
    db.add(event)
    db.flush()
    return event


def create_sample_data() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_user = get_or_create_user(db, "admin", "admin", "Admin123!")

        # Create two athletes with linked user accounts.
        athletes_info = [
            {
                "student_id": "2023001",
                "name": "李雷",
                "gender": "男",
                "group": "短跑组",
                "main_event": "100m",
                "phone": "13911110001",
            },
            {
                "student_id": "2023002",
                "name": "韩梅梅",
                "gender": "女",
                "group": "中长跑组",
                "main_event": "800m",
                "phone": "13911110002",
            },
        ]

        athlete_objs: list[Athlete] = []
        for info in athletes_info:
            user = get_or_create_user(db, info["student_id"], "athlete", "123456")
            athlete = (
                db.query(Athlete)
                .filter(Athlete.student_id == info["student_id"])
                .first()
            )
            if not athlete:
                athlete = Athlete(user_id=user.id, **info)
                db.add(athlete)
                db.flush()
            athlete_objs.append(athlete)

        # Events
        event_100m = get_or_create_event(db, "100m", "time")
        event_800m = get_or_create_event(db, "800m", "time")
        event_long_jump = get_or_create_event(db, "跳远", "distance")

        # Training sessions
        today = date.today()
        sessions: list[TrainingSession] = []
        for idx in range(3):
            session = (
                db.query(TrainingSession)
                .filter(TrainingSession.date == today - timedelta(days=idx))
                .first()
            )
            if not session:
                session = TrainingSession(
                    date=today - timedelta(days=idx),
                    start_time="16:30",
                    end_time="18:00",
                    location="田径场",
                    description=f"常规训练 第{idx + 1}天",
                    created_by=admin_user.id,
                )
                db.add(session)
                db.flush()
            sessions.append(session)

        # Attendance entries (latest session)
        db.query(Attendance).delete(synchronize_session=False)  # demo reset
        for session in sessions:
            for athlete in athlete_objs:
                status = "present"
                if session.date == today - timedelta(days=1) and athlete.student_id == "2023002":
                    status = "late"
                db.add(
                    Attendance(
                        session_id=session.id,
                        athlete_id=athlete.id,
                        status=status,
                        remark="自动示例数据",
                        recorded_by=admin_user.id,
                    )
                )

        # Scores
        db.query(Score).delete(synchronize_session=False)
        score_samples = [
            (athlete_objs[0], event_100m, 11.2),
            (athlete_objs[1], event_800m, 145.0),
            (athlete_objs[0], event_long_jump, 6.2),
        ]
        for athlete, event, perf in score_samples:
            db.add(
                Score(
                    athlete_id=athlete.id,
                    event_id=event.id,
                    performance=perf,
                    is_official=True,
                    remark="示例成绩",
                )
            )

        # Ratings
        db.query(Rating).delete(synchronize_session=False)
        for athlete in athlete_objs:
            db.add(
                Rating(
                    athlete_id=athlete.id,
                    coach_id=admin_user.id,
                    date=today - timedelta(days=1),
                    attitude=90,
                    attendance=95,
                    performance=92,
                    comment="保持状态，继续努力！",
                )
            )

        # Featured event for countdown
        featured = db.query(FeaturedEvent).first()
        start_time = datetime.now() + timedelta(days=7, hours=2)
        if featured:
            featured.name = "校运会田径选拔赛"
            featured.start_time = start_time
            featured.location = "田径中心体育场"
            featured.description = "请全体主力队员参加，提前30分钟到场热身。"
            featured.updated_by = admin_user.id
        else:
            db.add(
                FeaturedEvent(
                    name="校运会田径选拔赛",
                    start_time=start_time,
                    location="田径中心体育场",
                    description="请全体主力队员参加，提前30分钟到场热身。",
                    updated_by=admin_user.id,
                )
            )

        db.commit()
        print("✅ Seed data inserted. Admin account -> username: admin / password: Admin123!")
        print("✅ Athlete sample accounts -> 学号 2023001 / 2023002, 初始密码 123456")
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
