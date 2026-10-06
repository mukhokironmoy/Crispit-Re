# Crispit V1 Architecture Decisions

This document records the starting technical and product decisions for Crispit V1.

These decisions form the baseline for implementation. They can be changed later if implementation evidence justifies it, but any significant change should be recorded in the project Decision Log and Change Log.

---

## D-001 — Use a Python-First Modular Monolith

**Decision:**  
Crispit V1 will be implemented as a Python-first modular monolith.

**Reason:**  
Python is already the primary language used for the existing Crispit summarisation pipeline and provides strong libraries for APIs, background processing, database access, YouTube transcript handling, and LLM integration.

A modular monolith keeps the application in one codebase while still separating responsibilities into modules such as:

- Web/API
- Telegram bots
- Summary processing
- Source discovery
- Queue handling
- Scheduling
- Database access

This avoids the operational complexity of microservices during the MVP stage.

**Alternatives considered:**

- Microservices
- Workflow-first platforms such as n8n
- Multiple independent applications

**Status:** Active

---

## D-002 — Use FastAPI as the Backend Framework

**Decision:**  
FastAPI will be the primary backend framework.

**Reason:**  
FastAPI can support the different interfaces Crispit requires within one backend:

- REST APIs
- Telegram webhook endpoints
- Health endpoints
- Server-rendered management routes
- Internal application services

It also integrates well with Python type hints and modern validation libraries.

**Alternatives considered:**

- Flask
- Django

**Status:** Active

---

## D-003 — Use PostgreSQL and SQLAlchemy

**Decision:**  
PostgreSQL will be the primary database, with SQLAlchemy used as the Python ORM and database-access layer.

**Reason:**  
Crispit requires durable relational state for:

- Users
- Telegram identities
- Summary modes
- Tracked sources
- Videos
- Processing jobs
- Generated summaries
- Delivery preferences
- Delivery attempts

PostgreSQL provides transactions, constraints, concurrency support, and strong relational integrity.

SQLAlchemy keeps database interaction inside Python while allowing explicit schemas and transactions.

**Alternative considered:**

- SQLite-only persistence

SQLite may still be useful for isolated tests, but it will not be the primary V1 database.

**Status:** Active

---

## D-004 — Prefer Supabase for Managed PostgreSQL and Authentication

**Decision:**  
Supabase is the preferred managed infrastructure provider for the production PostgreSQL database and website authentication.

**Reason:**  
Supabase provides:

- Managed PostgreSQL
- Authentication
- Hosted infrastructure
- Administrative tooling

This avoids implementing custom account-management and authentication infrastructure during V1.

Crispit's internal application state will still be accessed through SQLAlchemy where appropriate rather than tightly coupling the entire application to Supabase-specific APIs.

**Alternative considered:**

- Self-hosted PostgreSQL with custom authentication

**Status:** Active

---

## D-005 — Use Telegram for V1 Delivery

**Decision:**  
Telegram will be the messaging and delivery platform for Crispit V1.

**Reason:**  
Telegram provides a comparatively simple Bot API and allows Crispit to prove both major product workflows without the additional approval, template, and messaging restrictions associated with WhatsApp.

The two main workflows are:

1. User-requested, on-demand summaries.
2. Automatically delivered summaries from tracked sources.

**Alternative considered:**

- WhatsApp-first delivery

WhatsApp remains a post-MVP option.

**Status:** Active

---

## D-006 — Use Two Telegram Bot Identities with One Backend

**Decision:**  
Crispit will use two Telegram bot identities while keeping one shared backend and shared business logic.

The planned identities are:

- **Crispit On-Demand Bot** — accepts user-submitted YouTube links and summary requests.
- **Crispit Main Bot** — delivers automated summaries and scheduled batches.

**Reason:**  
The two bots represent different user experiences:

- Active request-response interaction.
- Passive notification and delivery.

Separating the bot identities keeps those experiences clear without duplicating the underlying processing system.

**Alternatives considered:**

- One combined Telegram bot.
- Two completely separate backend applications.

**Status:** Active

---

## D-007 — Treat Summary Modes as Shared Core Records

**Decision:**  
Summary modes will be represented as reusable application records rather than being embedded directly into bot handlers or hard-coded workflow logic.

A mode can define configuration such as:

- Mode name
- Prompt template
- Output behaviour
- Ownership
- Whether it is enabled
- Whether it is built-in or user-created

**Reason:**  
Summary modes must eventually be usable from:

- On-demand requests
- Automatic source processing
- The management website
- User-created custom modes

Keeping them as shared records prevents duplicate configuration across interfaces.

**Alternative considered:**

- Hard-coded prompts inside Telegram handlers

**Status:** Active

---

## D-008 — Use One Shared Processing Queue

**Decision:**  
All summary-generation work will enter one shared processing queue.

**Reason:**  
On-demand summaries and automatically discovered videos ultimately perform the same core processing:

1. Obtain transcript.
2. Build prompt.
3. Call LLM.
4. Validate output.
5. Store summary.

The timing of delivery is a user preference and should not require separate processing queues.

**Alternative considered:**

- Separate queues for immediate summaries and scheduled digests

**Status:** Active

---

## D-009 — Start with a Database-Backed Queue and Plain Python Worker

**Decision:**  
The initial job queue will use PostgreSQL-backed job records processed by a standalone Python worker.

**Reason:**  
This provides the durability needed for V1 without immediately introducing infrastructure such as:

- Redis
- Celery
- RabbitMQ

The database-backed approach also allows the project to directly model:

- Pending jobs
- Claimed jobs
- Running jobs
- Retries
- Failures
- Completed jobs

If future load demonstrates that PostgreSQL is insufficient as a queue, dedicated queue infrastructure can be introduced later.

**Alternative considered:**

- Redis + Celery from Sprint 0

**Status:** Active

---

## D-010 — Keep Discovery and Delivery Scheduling Separate

**Decision:**  
Source discovery timing and user delivery timing will be handled independently.

**Reason:**  
A source may need to be checked frequently for new videos even when the user only wants one digest each day.

For example:

```text
Check YouTube source every 30 minutes
                ↓
Discover new video
                ↓
Generate and store summary
                ↓
Wait until user's configured delivery time
                ↓
Deliver daily batch
```

Combining discovery and delivery into one schedule would unnecessarily delay processing and make scheduling logic harder to manage.

**Alternative considered:**

- One combined scheduler for discovery and delivery

**Status:** Active

---

## D-011 — Use Ordinary Python Services for the Summary Pipeline

**Decision:**  
The V1 summary workflow will be implemented using normal Python service modules rather than an agent framework.

**Reason:**  
The primary summary workflow is deterministic:

```text
Video
  ↓
Transcript
  ↓
Prompt
  ↓
LLM
  ↓
Validation
  ↓
Persistence
  ↓
Delivery
```

There is currently no need for an agent to dynamically decide which actions or tools should execute.

Normal Python services are simpler to:

- Understand
- Test
- Debug
- Maintain

**Alternative considered:**

- LangGraph-based orchestration

**Status:** Active

---

## D-012 — Defer WhatsApp, n8n, and LangGraph

**Decision:**  
WhatsApp integration, n8n workflows, and LangGraph orchestration are explicitly outside the Crispit V1 scope.

**Reason:**  
None of these technologies are necessary to prove the core product workflows.

Adding them during V1 would increase:

- Development time
- Infrastructure complexity
- Testing requirements
- Failure points

They can be reconsidered once the initial product is functional and deployed.

**Status:** Active

---

## D-013 — Define Crispit V1 as Sprints 0–4

**Decision:**  
The first deployable Crispit release consists of Sprints 0 through 4.

The broad roadmap is:

```text
Sprint 0
Foundation and infrastructure

Sprint 1
On-demand summarisation

Sprint 2
Automated discovery and delivery

Sprint 3
Management website and authentication

Sprint 4
Deployment, reliability, and production release
```

**Reason:**  
Additional scaling, provider integrations, advanced automation, and monetisation should not delay the first complete product.

A successful V1 should demonstrate the complete user workflow before post-MVP functionality is added.

**Status:** Active

---

# Architecture Baseline

Based on the decisions above, the initial Crispit V1 architecture is:

```text
Users
  │
  ├───────────────┐
  │               │
Website       Telegram
  │            Bots
  │               │
  └───────┬───────┘
          │
       FastAPI
          │
 ┌────────┴────────┐
 │                 │
Application     Database
Services       PostgreSQL
 │                 │
 │          SQLAlchemy Models
 │
 ├── Transcript Service
 ├── Mode Service
 ├── Prompt Builder
 ├── LLM Provider
 ├── Queue Service
 ├── Discovery Service
 └── Delivery Service
          │
          ▼
   Database Job Queue
          │
      Python Worker
          │
   Summary Processing

Separate Scheduler
      │
      ├── Source discovery
      └── Scheduled delivery
```

The architecture should remain simple during V1. New infrastructure should only be introduced when an existing design demonstrably cannot satisfy a requirement.