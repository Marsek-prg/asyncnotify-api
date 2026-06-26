# AsyncNotify API

AsyncNotify API is a backend notification service portfolio project. It will accept events through a REST API, persist notification data, and process notification delivery in background workers in later steps.

## Current Tech Stack

- Python 3.12+
- FastAPI
- Docker
- pytest
- Ruff

PostgreSQL, Redis, Celery, and Alembic will be added in later steps.

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

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Run With Docker

Build the Docker image:

```powershell
docker compose build
```

Start the API container:

```powershell
docker compose up
```

Build and start in one command:

```powershell
docker compose up --build
```

After Docker starts, the app is available at:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Stop and remove containers:

```powershell
docker compose down
```

## Run Tests

```powershell
pytest
```

## Run Ruff

```powershell
ruff check .
```
