## FastAPI + RQ + Redis backend

This backend provides a minimal API to:

- **Upload a PDF energy bill**, store it in Postgres, and enqueue an **RQ job** to analyze it.
- **Check the status** of the analysis job.

### Tech stack

- **FastAPI** – HTTP API.
- **Postgres + SQLAlchemy** – stores uploaded PDFs.
- **Redis + RQ** – background job queue.
- **PyPDF2** – simple PDF text extraction (for now we just print the content).

---

### 1. Install dependencies

```bash
cd /Users/edwin/Development/Personal/energy-bill-reader/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

---

### 2. Run Postgres and Redis

You can use Docker or local services. Example with Docker:

```bash
docker run --name energy-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=energy_bills -p 5432:5432 -d postgres:16
docker run --name energy-redis -p 6379:6379 -d redis:7
```

---

### 3. Configure environment (optional)

Create a `.env` file in `backend/` to override defaults:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/energy_bills
REDIS_URL=redis://localhost:6379/0
RQ_QUEUE_NAME=pdf-analysis
UPLOAD_DIR=uploads
```

Default values (used if `.env` is missing) are the same as above.

---

### 4. Run the API server

From the **project root** (so that `backend` is treated as a package):

```bash
cd /Users/edwin/Development/Personal/energy-bill-reader
backend/.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open the interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### 5. Run the RQ worker

In another terminal (same virtualenv), from the **project root**:

```bash
cd /Users/edwin/Development/Personal/energy-bill-reader
backend/.venv/bin/python -m backend.worker
```

This starts an RQ worker listening to the `pdf-analysis` queue.

---

### 6. API endpoints

#### `POST /upload`

Upload a PDF, store it in Postgres, and enqueue a job:

- **Form field**: `file` – the PDF file (`multipart/form-data`).
- **Response**:

```json
{
  "job_id": "rq:job:...",
  "document_id": "uuid...",
  "filename": "your-bill.pdf"
}
```

#### `GET /status/{job_id}`

Check the status of a job:

- **Response** example:

```json
{
  "job_id": "rq:job:...",
  "status": "finished",
  "result": "Full PDF text here...",
  "enqueued_at": "...",
  "started_at": "...",
  "ended_at": "...",
  "exc_info": null
}
```

> For now, the job simply reads the PDF from disk, prints its contents to the worker logs, and returns the extracted text.
