from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# See note in main.py: in production we run from the backend directory,
# so we import sibling modules with absolute imports.
from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


def get_db() -> Session:
  """
  FastAPI dependency that yields a database session and ensures it is closed.
  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


