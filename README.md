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
- `db` — Database engine, sessions, and migration infrastructure.
- `integrations` — Telegram, YouTube, LLM, and other external services.
- `models` — SQLAlchemy database models.
- `repositories` — Database-access operations.
- `services` — Application workflows and business logic.
- `scheduling` — Source-discovery and delivery scheduling.
- `workers` — Background job processing.
- `tests` — Automated tests for the application.

## Local Development

Crispit requires Python 3.12 or newer.

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

The initial configuration variables are:

```dotenv
CRISPIT_APP_NAME=Crispit
CRISPIT_APP_ENVIRONMENT=development
CRISPIT_LOG_LEVEL=INFO
```

The `.env` file is ignored by Git and must not be committed. The safe `.env.example` template remains version-controlled.

## Running the Application

Start the development server:

```powershell
python -m uvicorn crispit.main:app --host 127.0.0.1 --port 8765 --reload
```

The `--reload` option restarts the server when Python source files change. It is intended for local development only.

The following endpoints are then available:

- Liveness check: `http://127.0.0.1:8765/health/live`
- Interactive API documentation: `http://127.0.0.1:8765/docs`
- OpenAPI schema: `http://127.0.0.1:8765/openapi.json`

The liveness endpoint returns:

```json
{
  "status": "ok"
}
```

It confirms that the Crispit application process is running. Checks for PostgreSQL and other external dependencies will be added separately when those services are introduced.

## Automated Checks

Run the test suite:

```powershell
python -m pytest -W error
```

Run the Ruff code-quality checks:

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

The complete local verification sequence is:

```powershell
python -m pytest -W error
python -m ruff check .
python -m mypy src tests
python -m pip check
git diff --check
```

## Development Status

Completed milestone: S0.M3 — Typed Configuration, Logging, and Health Endpoint

Next milestone: S0.M4 — Local PostgreSQL and SQLAlchemy Connection