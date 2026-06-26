# AsyncNotify API

AsyncNotify API is a backend notification service portfolio project. It will accept events through a REST API, persist notification data, and process notification delivery in background workers in later steps.

## Current Tech Stack

- Python 3.12+
- FastAPI
- pytest
- Ruff

PostgreSQL, Redis, Celery, Docker, and Alembic will be added in later steps.

## Run Locally

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The health check is available at:

```text
GET http://127.0.0.1:8000/health
```

## Run Tests

```powershell
pytest
```

## Run Ruff

```powershell
ruff check .
```
