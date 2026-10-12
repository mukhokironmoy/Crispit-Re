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

The editable installation allows changes inside `src/crispit` to take effect without reinstalling the project after every edit.

### Configure the environment

Create a local environment file from the safe template:

```powershell
Copy-Item .env.example .env
```

The current local-development configuration variables are:

```dotenv
CRISPIT_APP_NAME=Crispit
CRISPIT_APP_ENVIRONMENT=development
CRISPIT_LOG_LEVEL=INFO

CRISPIT_DATABASE_URL=postgresql+psycopg://crispit:crispit_dev_password@localhost:5432/crispit_dev
CRISPIT_TEST_DATABASE_URL=postgresql+psycopg://crispit:crispit_test_password@localhost:5433/crispit_test
```

`CRISPIT_DATABASE_URL` selects the database used by the running application. By default, this is the local development PostgreSQL instance.

`CRISPIT_TEST_DATABASE_URL` is used by the integration-test setup and points to an isolated local PostgreSQL test instance.

An optional `CRISPIT_SUPABASE_DATABASE_URL` can also be supplied for a managed PostgreSQL connection; see [Supabase Managed PostgreSQL](#supabase-managed-postgresql-optional).

The `.env` file is ignored by Git and must not be committed. The safe `.env.example` template remains version-controlled. The sample local credentials above are for the Docker development setup, not for a deployed database.

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

## Supabase Managed PostgreSQL (Optional)

Crispit can connect to a Supabase-hosted PostgreSQL database using the same SQLAlchemy and Psycopg 3 database layer used for local PostgreSQL. Supabase is optional for local development; the Docker databases remain available for development and integration testing.

### Create a Supabase project and obtain its connection URI

1. Create a project in the [Supabase dashboard](https://supabase.com/dashboard).
2. In the project, open **Connect** and select **Session pooler**.
3. Copy the PostgreSQL connection URI. The session pooler supports IPv4 connections and uses port `5432`.
4. Use the database password associated with the project. If the password contains URI-reserved characters (such as `@`, `/`, `:` or `#`), percent-encode the password portion before using it in a URI.

A Session pooler connection URI resembles:

```text
postgresql://postgres.PROJECT_REF:YOUR_PASSWORD@POOLER_HOST:5432/postgres
```

Keep the project-specific username, pooler host, and database name from the Supabase dashboard. Do not use the plain `postgres` username in place of the project-specific pooler username.

### Configure the optional Supabase URL

Add the following entry to the local `.env` file, replacing the placeholders with the actual connection details:

```dotenv
CRISPIT_SUPABASE_DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:YOUR_PASSWORD@POOLER_HOST:5432/postgres
```

The `postgresql+psycopg://` prefix explicitly selects Psycopg 3 for SQLAlchemy.

The `CRISPIT_` prefix is required by the current Pydantic Settings configuration. The `supabase_database_url` field is optional, so Crispit can run without Supabase credentials.

**Do not change** `CRISPIT_DATABASE_URL` or `CRISPIT_TEST_DATABASE_URL` just to store the Supabase connection information. Adding `CRISPIT_SUPABASE_DATABASE_URL` alone does not switch the application to Supabase.

Document this variable in `.env.example` using a commented placeholder only, never real credentials:

```dotenv
# Optional Supabase managed PostgreSQL (Session pooler)
# CRISPIT_SUPABASE_DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:YOUR_PASSWORD@POOLER_HOST:5432/postgres
```

### Choose which database the application uses

| Environment variable | Role |
| --- | --- |
| `CRISPIT_DATABASE_URL` | Active application database; local PostgreSQL by default. |
| `CRISPIT_TEST_DATABASE_URL` | Isolated local database used by integration tests. |
| `CRISPIT_SUPABASE_DATABASE_URL` | Optional stored connection URI for managed PostgreSQL. |

For a temporary Supabase readiness check in **Windows PowerShell**, set the active database URL for the current shell and run a fresh Python process:

```powershell
$env:CRISPIT_DATABASE_URL = (python -c "from crispit.core.config import get_settings; print(get_settings().supabase_database_url or '')")
```

This command copies the configured Supabase URL into a shell environment variable. Only use it after verifying that `CRISPIT_SUPABASE_DATABASE_URL` is configured. **Do not print the environment variable or include the URL in logs or screenshots.**

With the override active, use a fresh process to check database readiness:

```powershell
@'
from fastapi.testclient import TestClient
from crispit.main import app

response = TestClient(app).get("/health/ready")
print("Status code:", response.status_code)
print("Response:", response.json())
'@ | python -
```

A successful connection returns HTTP `200` with `{"status": "ready"}`.

After the check, remove the override:

```powershell
Remove-Item Env:\CRISPIT_DATABASE_URL
```

New Python processes will then use the local `CRISPIT_DATABASE_URL` value in `.env`, provided there is no other environment override. Do not run the integration test suite while intentionally overriding the application's database URL to the managed database.

### Security and testing boundaries

- Keep real passwords and connection URIs in `.env` or a secure deployment secret manager, never in source control or `.env.example`.
- Verify that Git ignores `.env` with `git check-ignore .env`.
- Keep routine integration tests pointed at the isolated local `crispit_test` database; avoid coupling them to Supabase availability.
- Do not run destructive tests, schema experiments, or seed operations against a production database.
- The `/health/ready` check verifies connectivity; it does not confirm that future application tables or migrations have been deployed.

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

- Liveness check: <http://127.0.0.1:8765/health/live>
- Readiness check: <http://127.0.0.1:8765/health/ready>
- Interactive API documentation: <http://127.0.0.1:8765/docs>
- OpenAPI schema: <http://127.0.0.1:8765/openapi.json>

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

`GET /health/ready` performs a real database connectivity check using SQLAlchemy against the active application database.

When the database is available, it returns:

```json
{
  "status": "ready"
}
```

When the database is unavailable, it returns HTTP `503 Service Unavailable` with:

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
Psycopg 3
        ↓
PostgreSQL (local Docker or Supabase)
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

- **S0.M4 — Local PostgreSQL and SQLAlchemy Connection:** Completed.
- **S0.M5 — Supabase Project and Managed-Database Connection:** Connectivity and readiness verification completed; documentation, final automated checks, and commit pending.

The Supabase database connection has been verified, but this milestone does not claim that application tables or schema migrations have been deployed to Supabase.
