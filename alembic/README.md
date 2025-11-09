# Alembic Setup

1. Install dependencies: `pip install -r requirements.txt`.
2. Initialize the migration environment (once): `alembic init alembic`.
3. Update `alembic.ini` to point `sqlalchemy.url` to the same value as `SQLALCHEMY_DATABASE_URI`.
4. Edit `alembic/env.py` to import metadata from `app.db.base` (e.g. `from app.db.base import Base`).
5. Generate migrations with `alembic revision --autogenerate -m "message"` and apply them using `alembic upgrade head`.

The current file acts as a placeholder so the directory exists in version control.
