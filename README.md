# AsyncNotify API

AsyncNotify API is a backend notification service portfolio project. It will accept events through a REST API, persist notification data, and process notification delivery in background workers in later steps.

## Current Tech Stack

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Docker
- pytest
- Ruff

Redis, Celery, and notification workers will be added in later steps.

## Persistence

The project now includes the first domain persistence models:

- incoming events
- notifications
- delivery attempts

Alembic includes the initial domain migration that creates the `events`,
`notifications`, and `delivery_attempts` tables.

## Environment Variables

Copy `.env.example` to `.env` for local overrides if needed. Do not commit real secrets.

```env
APP_NAME=AsyncNotify API
APP_ENV=local
APP_DEBUG=true
APP_VERSION=0.1.0
POSTGRES_DB=asyncnotify
POSTGRES_USER=asyncnotify
POSTGRES_PASSWORD=asyncnotify
DATABASE_URL=postgresql+psycopg://asyncnotify:asyncnotify@postgres:5432/asyncnotify
```

`DATABASE_URL` is used by the application and Alembic. In Docker Compose, the API connects to PostgreSQL through the `postgres` service name.

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
GET http://127.0.0.1:8000/health/db
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Run With Docker

Docker Compose starts the API and PostgreSQL services. Build and start them with:

```powershell
docker compose up --build
```

After Docker starts, check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/db
http://127.0.0.1:8000/docs
```

Stop and remove containers:

```powershell
docker compose down
```

PostgreSQL data is stored in the named Docker volume `postgres_data`.

## Database

The project has the database foundation configured:

- SQLAlchemy 2.x declarative base in `app/db/base.py`
- synchronous SQLAlchemy engine and session dependency in `app/db/session.py`
- Alembic configuration in `alembic.ini` and `alembic/`
- `Base.metadata` wired as Alembic `target_metadata`
- Event, Notification, and DeliveryAttempt domain models
- initial migration `20260627_0001_create_notification_tables.py`

When Docker PostgreSQL is running, manage migrations from the API container:

```powershell
docker compose exec api alembic upgrade head
docker compose exec api alembic current
docker compose exec api alembic downgrade -1
```

For local Alembic commands, `DATABASE_URL` must point to an accessible PostgreSQL
instance before running:

```powershell
alembic upgrade head
```

## Run Tests

```powershell
pytest
```

## Run Ruff

```powershell
ruff check .
```
