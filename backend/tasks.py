from pathlib import Path
from typing import Any, Dict
from uuid import UUID
import json
import os

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from redis import Redis
from rq import Queue
from rq.job import get_current_job
import openai

from .config import get_settings
from .database import SessionLocal
from .models import Document, JobResult


# Load environment variables from backend/.env when imported (for OPENAI_API_KEY, etc.)
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)

settings = get_settings()
openai.api_key = os.getenv("OPENAI_API_KEY", "")


def parse_pdf(path: str, document_id: str, email: str) -> Dict[str, Any]:
  """
  RQ job that reads a PDF from disk, stores its raw text, and enqueues a
  follow-up job to extract key information.

  Returns:
    {
      "linked_job": "<id of extract_key_info job>",
      "content": { "raw_text": "..." }
    }
  """
  pdf_path = Path(path)
  if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found at: {pdf_path}")

  reader = PdfReader(str(pdf_path))
  text_parts: list[str] = []

  for page in reader.pages:
    page_text = page.extract_text() or ""
    text_parts.append(page_text)

  full_text = "\n".join(text_parts)

  # Enqueue key-information extraction job
  redis_conn = Redis.from_url(settings.redis_url)
  queue = Queue(settings.rq_queue_name, connection=redis_conn)
  linked_job = queue.enqueue(extract_key_info, full_text, document_id, email)

  job = get_current_job()
  job_id = job.id if job is not None else None

  content_json: Dict[str, Any] = {"raw_text": full_text}

  # Persist this job's result in the database
  db = SessionLocal()
  try:
    doc_uuid = UUID(document_id)
    document = db.get(Document, doc_uuid)
    if document is None:
      raise ValueError(f"Document {document_id} not found when saving parse_pdf result.")

    job_result = JobResult(
      job_id=job_id or "",
      document_id=document.id,
      email=email,
      job_type="parse_pdf",
      content=content_json,
      linked_job_id=linked_job.id,
    )
    db.add(job_result)
    db.commit()
  finally:
    db.close()

  # Clean up: remove the PDF file from disk after processing
  try:
    if pdf_path.exists():
      pdf_path.unlink()
  except Exception as e:
    # Log but don't fail the job if file deletion fails
    print(f"Warning: Failed to delete PDF file {pdf_path}: {e}")

  return {"linked_job": linked_job.id, "content": content_json}


def extract_key_info(full_text: str, document_id: str, email: str) -> Dict[str, Any]:
  """
  Extract key information from the plain-text PDF content.

  Uses the OpenAI API to robustly parse electricity bills of varying formats.
  """
  model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

  system_prompt = (
    "You are an expert assistant that extracts key fields from electricity bill text. "
    "Given the raw OCR or text of an electricity bill, identify and normalize the "
    "following fields where possible:\n"
    "- billed_name: the customer or entity being billed\n"
    "- provider_name: the retailer or energy provider (e.g. 'Amber Electric Pty Ltd')\n"
    "- account_number: the customer's account number on the bill\n"
    "- invoice_number: the specific invoice/bill number\n"
    "- address: the supply or billing address line(s)\n"
    "- total_owed: the total amount due for this bill, numeric as a string (e.g. '189.31')\n"
    "- due_date: the payment due date as it appears on the bill\n"
    "- billing_period: the billing period covered by the bill\n"
    "- usage_kwh: total energy usage in kWh for the period, as string (e.g. '623.64')\n"
    "- charges_total: total charges before credits, as string\n"
    "- nmi: the National Metering Identifier or similar identifier if present\n\n"
    "Return ONLY a JSON object with exactly these keys. Use null when a field cannot be found."
  )

  response = openai.ChatCompletion.create(
    model=model_name,
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": full_text},
    ],
  )

  content = response.choices[0].message["content"]
  key_info: Dict[str, Any] = json.loads(content)

  job = get_current_job()
  job_id = job.id if job is not None else None

  # Persist this job's result in the database
  db = SessionLocal()
  try:
    doc_uuid = UUID(document_id)
    document = db.get(Document, doc_uuid)
    if document is None:
      raise ValueError(f"Document {document_id} not found when saving extract_key_info result.")

    job_result = JobResult(
      job_id=job_id or "",
      document_id=document.id,
      email=email,
      job_type="extract_key_info",
      content=key_info,
      linked_job_id=None,
    )
    db.add(job_result)
    db.commit()
  finally:
    db.close()

  return {"linked_job": None, "content": key_info}


