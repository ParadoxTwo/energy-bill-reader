import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Settings:
  """Application configuration loaded from environment variables (simple dataclass)."""

  database_url: str
  redis_url: str
  rq_queue_name: str
  upload_dir: str
  cors_origins: list[str]


@lru_cache
def get_settings() -> Settings:
  """Return cached settings, reading from environment variables if present."""
  # Parse CORS origins from environment variable (comma-separated) or use defaults
  cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
  )
  cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

  return Settings(
    database_url=os.getenv(
      "DATABASE_URL",
      "postgresql+psycopg2://postgres:postgres@localhost:5432/energy_bills",
    ),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    rq_queue_name=os.getenv("RQ_QUEUE_NAME", "pdf-analysis"),
    upload_dir=os.getenv("UPLOAD_DIR", "uploads"),
    cors_origins=cors_origins,
  )


