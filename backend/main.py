from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from rq import Queue
from rq.job import Job
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, engine, get_db
from .models import Document, JobResult
from .tasks import parse_pdf

settings = get_settings()

# Ensure database tables exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
  title="Energy Bill Analyzer API",
  description="Upload business energy bills, queue analysis jobs, and check their status.",
  version="0.1.0",
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=False,
  allow_methods=["*"],
  allow_headers=["*"],
)


def get_redis() -> Redis:
  return Redis.from_url(settings.redis_url)


def get_queue(redis_conn: Redis | None = None) -> Queue:
  if redis_conn is None:
    redis_conn = get_redis()
  return Queue(settings.rq_queue_name, connection=redis_conn)


@app.post("/upload")
async def upload_pdf(
  email: str = Form(...),
  file: UploadFile = File(...),
  db: Session = Depends(get_db),
):
  """
  Upload a PDF, store it in Postgres, and enqueue an RQ job to parse it.
  """
  if file.content_type != "application/pdf":
    raise HTTPException(status_code=400, detail="Only PDF files are supported.")

  # Read file bytes
  contents = await file.read()
  if not contents:
    raise HTTPException(status_code=400, detail="Uploaded file is empty.")

  # Ensure upload directory exists and write file to disk
  upload_dir = Path(settings.upload_dir)
  upload_dir.mkdir(parents=True, exist_ok=True)

  file_id = uuid4()
  filename = f"{file_id}.pdf"
  disk_path = upload_dir / filename
  disk_path.write_bytes(contents)

  # Store in Postgres
  document = Document(
    id=file_id,
    email=email,
    filename=file.filename or filename,
    content=contents,
  )
  db.add(document)
  db.commit()

  # Enqueue RQ job that operates on the file path on disk
  redis_conn = get_redis()
  queue = get_queue(redis_conn)
  job: Job = queue.enqueue(parse_pdf, str(disk_path), str(document.id), email)

  # Persist job id on the document for easy correlation
  document.job_id = job.id
  db.add(document)
  db.commit()
  db.refresh(document)

  return {
    "job_id": job.id,
    "document_id": str(document.id),
    "filename": document.filename,
  }


@app.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
  """
  Return the current status (and result if finished) of a queued job.
  """
  # Prefer the database, which stores structured results and linked jobs.
  job_record = db.query(JobResult).filter(JobResult.job_id == job_id).one_or_none()
  if job_record is not None:
    return {
      "job_id": job_record.job_id,
      "status": "finished",
      "content": job_record.content,
      "linked_job_id": job_record.linked_job_id,
      "enqueued_at": None,
      "started_at": None,
      "ended_at": None,
      "exc_info": None,
    }

  # Fallback to querying the RQ job directly if we don't have a DB record yet.
  redis_conn = get_redis()
  try:
    job = Job.fetch(job_id, connection=redis_conn)
  except Exception:
    raise HTTPException(status_code=404, detail="Job not found.")

  return {
    "job_id": job.id,
    "status": job.get_status(),
    "content": job.result,
    "linked_job_id": None,
    "enqueued_at": job.enqueued_at,
    "started_at": job.started_at,
    "ended_at": job.ended_at,
    "exc_info": job.exc_info,
  }



