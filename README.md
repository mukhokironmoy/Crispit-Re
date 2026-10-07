# Crispit

Crispit is a system for converting YouTube content into structured summaries and delivering them through on-demand and automated workflows.

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

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install Crispit and its development dependencies:
```python
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the automated checks:
```python
python -m pytest
python -m ruff check .
python -m mypy src
```

The FastAPI application entry point and health endpoint will be introduced in S0.M3.

## Development Status
Completed milestone: S0.M2 — Python Package and Bare-Bones File Tree
Next milestone: S0.M3 — Typed Configuration, Logging, and Health Endpoint