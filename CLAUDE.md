# Chesshire

Aggregates a user's chess.com accounts and produces insights about their play (portfolio project).

- `fe/`: React app (Vite, MUI, Emotion, TanStack Query and Router). Has its own `fe/CLAUDE.md`.
- `be/`: FastAPI + SQLAlchemy 2.0 (sync) + PostgreSQL + Alembic. Has its own `be/CLAUDE.md`.
- `docs/decisions.md`: decision log (scope, schema, auth, analysis plans)
- `docs/PLANNED.md`: details for decided-but-unscheduled features; the decision log points here

## Current scope
MVP is **data ingestion and aggregation**. Engine-based analysis (Stockfish, repeated mistakes) comes after the MVP and must not block it.

## Running locally
- Backend (from `be/`): `uv run uvicorn app.main:app --reload` (default port 8000)
- Frontend (from `fe/`): `yarn run dev` (Vite default port 5173)

## Working agreements
- **Before changing the schema, auth, ingestion, or architecture, read `docs/decisions.md`.** Don't contradict an Accepted decision without raising it first.
- **When a decision is made or changed, record it in `docs/decisions.md`**, following the maintenance rules at the top of that file (append-only; supersede, don't rewrite).
- Never commit `.env` files. Keep `.env.example` current when adding settings.
- The frontend uses **yarn**. Don't use npm, and don't create `package-lock.json`.
- Challenge plans before implementing them: point out unrealistic assumptions, weak reasoning, and likely failure points, then help with what the user decides.
- **Ask before assuming.** When a request is open-ended or has more than one reasonable reading ("flesh out", "add what's needed"), ask follow-up questions before implementing. Don't pick an interpretation and build it.
