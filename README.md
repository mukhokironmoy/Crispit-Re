# Crispit

Crispit converts YouTube content into structured summaries and delivers them through on-demand and automated workflows.

## V1 Architecture

Crispit V1 is being developed as a Python-first modular monolith using:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Supabase
- Telegram
- A database-backed job queue
- A standalone Python worker and scheduler

See `docs/architecture-decisions.md` for the architectural baseline.

## Project Structure

Application code uses a `src` layout and is organised by responsibility:

- `api` — FastAPI routes, webhooks, and external request handling.
- `core` — Configuration, logging, exceptions, and shared infrastructure.
- `db` — SQLAlchemy engine, sessions, declarative base, and database dependencies.
- `integrations` — Telegram, YouTube, LLM, and other external services.
- `models` — SQLAlchemy database models.
- `repositories` — Database-access operations.
- `services` — Application workflows and business logic.
- `scheduling` — Source-discovery and delivery scheduling.
- `workers` — Background job processing.
- `tests` — Automated tests for the application.
- `tests/integration` — Tests that require external infrastructure such as PostgreSQL.

## Local Development

Crispit requires:

- Python 3.12 or newer.
- Docker Desktop with Docker Compose.

### Create the virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents the activation script from running, temporarily allow locally created scripts for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Install the project

Upgrade Pip and install Crispit with its development dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The editable installation allows changes inside `src\crispit` to take effect without reinstalling the project after every edit.

### Configure the environment

Create a local environment file from the safe template:

```powershell
Copy-Item .env.example .env
```

The current configuration variables are:

```dotenv
CRISPIT_APP_NAME=Crispit
CRISPIT_APP_ENVIRONMENT=development
CRISPIT_LOG_LEVEL=INFO

CRISPIT_DATABASE_URL=postgresql+psycopg://crispit:crispit_dev_password@localhost:5432/crispit_dev
CRISPIT_TEST_DATABASE_URL=postgresql+psycopg://crispit:crispit_test_password@localhost:5433/crispit_test
```

`CRISPIT_DATABASE_URL` is used by the local Crispit application.

`CRISPIT_TEST_DATABASE_URL` is used only by integration tests and points to an isolated PostgreSQL test instance.

The `.env` file is ignored by Git and must not be committed. The safe `.env.example` template remains version-controlled.

## Local PostgreSQL

Crispit uses Docker Compose to provide reproducible PostgreSQL instances for local development and integration testing.

The Compose configuration defines two isolated services:

- `postgres` — development PostgreSQL instance exposed on `localhost:5432`.
- `postgres-test` — integration-test PostgreSQL instance exposed on `localhost:5433`.

The development database is:

```text
Database: crispit_dev
Port:     5432
```

The integration-test database is:

```text
Database: crispit_test
Port:     5433
```

### Start PostgreSQL

Start both database services:

```powershell
docker compose up -d
```

Check their status:

```powershell
docker compose ps
```

Both services should eventually report a `healthy` status.

### Stop PostgreSQL

Stop the containers without deleting their data:

```powershell
docker compose stop
```

Start them again with:

```powershell
docker compose start
```

To remove the containers while preserving their Docker volumes:

```powershell
docker compose down
```

Avoid using `docker compose down -v` unless the local database data is intentionally being discarded, because `-v` also removes the associated volumes.

## Running the Application

Make sure the development PostgreSQL service is running:

```powershell
docker compose up -d postgres
```

Then start the FastAPI development server:

```powershell
python -m uvicorn crispit.main:app --host 127.0.0.1 --port 8765 --reload
```

The `--reload` option restarts the server when Python source files change. It is intended for local development only.

The following endpoints are available:

- Liveness check: `http://127.0.0.1:8765/health/live`
- Readiness check: `http://127.0.0.1:8765/health/ready`
- Interactive API documentation: `http://127.0.0.1:8765/docs`
- OpenAPI schema: `http://127.0.0.1:8765/openapi.json`

### Liveness

`GET /health/live` returns:

```json
{
  "status": "ok"
}
```

The liveness endpoint confirms that the Crispit application process itself is running.

It does not depend on PostgreSQL.

### Readiness

`GET /health/ready` performs a real database connectivity check using SQLAlchemy.

When PostgreSQL is available, it returns:

```json
{
  "status": "ready"
}
```

When PostgreSQL is unavailable, it returns HTTP `503 Service Unavailable` with:

```json
{
  "detail": "Database unavailable"
}
```

This allows Crispit to distinguish between:

- the application process being alive, and
- the application being ready to serve requests that depend on PostgreSQL.

## Database Layer

Crispit uses SQLAlchemy with the Psycopg PostgreSQL driver.

The connection flow is:

```text
Crispit application
        ↓
SQLAlchemy
        ↓
Psycopg
        ↓
PostgreSQL
```

`src/crispit/db/session.py` provides:

- the shared SQLAlchemy engine.
- the `SessionLocal` session factory.

`src/crispit/db/base.py` provides the declarative SQLAlchemy `Base` class that future ORM models will inherit from.

`src/crispit/db/dependencies.py` provides the FastAPI database-session dependency and ensures sessions are closed after use.

## Automated Checks

### Fast tests

Run tests that do not require external infrastructure:

```powershell
python -m pytest -m "not integration" -W error
```

These tests can run without PostgreSQL.

### Integration tests

Make sure the isolated test PostgreSQL service is healthy:

```powershell
docker compose up -d postgres-test
docker compose ps
```

Then run:

```powershell
python -m pytest -m integration -W error
```

Integration tests use `CRISPIT_TEST_DATABASE_URL` and connect to the isolated `crispit_test` PostgreSQL instance on port `5433`.

### Entire test suite

With both PostgreSQL services running:

```powershell
python -m pytest -W error
```

### Code-quality checks

Run Ruff:

```powershell
python -m ruff check .
```

Run static type checking:

```powershell
python -m mypy src tests
```

Check installed dependency compatibility:

```powershell
python -m pip check
```

Check for whitespace errors in the Git diff:

```powershell
git diff --check
```

The complete local verification sequence is:

```powershell
docker compose up -d
python -m pytest -W error
python -m ruff check .
python -m mypy src tests
python -m pip check
git diff --check
```

## Development Status

Completed milestone: S0.M4 — Local PostgreSQL and SQLAlchemy Connection

Next milestone: S0.M5 — Supabase Project and Initial Schema