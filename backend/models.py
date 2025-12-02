from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import TIMESTAMP, Column, String, LargeBinary, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# Run from backend directory; use absolute imports for sibling modules.
from database import Base


class Document(Base):
  __tablename__ = "documents"

  id = Column(UUID(as_uuid=True), primary_key=True)
  email = Column(String, nullable=False)
  filename = Column(String, nullable=False)
  content = Column(LargeBinary, nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
  job_id = Column(String, nullable=True)


class JobResult(Base):
  __tablename__ = "job_results"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
  job_id = Column(String, unique=True, nullable=False)
  document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
  email = Column(String, nullable=False)
  job_type = Column(String, nullable=False)
  content = Column(JSON, nullable=True)
  linked_job_id = Column(String, nullable=True)
  created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
  updated_at = Column(
    TIMESTAMP(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )


