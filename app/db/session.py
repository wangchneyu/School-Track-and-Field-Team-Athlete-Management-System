from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()
database_url = settings.database_uri
engine_options = {"pool_pre_ping": True, "future": True}

if database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    engine_options["pool_size"] = settings.DB_POOL_SIZE
    engine_options["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_options["pool_recycle"] = settings.DB_POOL_RECYCLE

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
