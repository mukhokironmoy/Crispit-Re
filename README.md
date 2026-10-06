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

## Development Status

Current milestone: S0.M1 — Repository, Prerequisites, and Decision Baseline