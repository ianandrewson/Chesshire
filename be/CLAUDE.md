# Backend conventions

Stack: FastAPI, SQLAlchemy 2.0 (**sync**), PostgreSQL via psycopg 3 (`postgresql+psycopg://`), Alembic, pydantic-settings. Rationale for each choice is in `../docs/decisions.md`.

## Running

- Always run from `be/`: `uv run uvicorn app.main:app --reload`
- Python deps are managed with **uv**: use `uv add <pkg>`, never `pip install`.
- Use absolute imports (`from app.config import settings`), never relative ones.

## Layout

```
be/
  alembic.ini
  alembic/            # env.py, versions/
  app/
    main.py           # creates the FastAPI app, includes routers
    config.py         # Settings (pydantic-settings)
    database.py       # engine, SessionLocal, Base, get_db
    models/           # SQLAlchemy tables; __init__.py imports every model
    schemas/          # Pydantic request/response shapes
    routers/          # endpoints, one file per resource; keep thin
    services/         # chess.com client, aggregations, other logic
  tests/
```

Create folders when the first file needs them, not up front.

## Config

- All settings live in `app/config.py` as a `Settings(BaseSettings)` class; import the `settings` instance.
- Local values in `be/.env` (gitignored). Add every new variable to `be/.env.example` too.
- Production uses real environment variables; there is no `.env` there.

## Database and sessions

- Sync SQLAlchemy only. Endpoints get a session via `db: Session = Depends(get_db)`.
- Transactions are explicit: call `db.commit()` yourself.
- `database.py` must never import from `models/`. Models import `Base` from `app.database`.
- Every new model file must be imported in `app/models/__init__.py`, or Alembic autogenerate will silently skip it.
- Use `relationship` only where object navigation is wanted (e.g. a game with its players). Aggregations use explicit `select(...).join(...)`. Avoid lazy-load N+1 (use `selectinload` in queries that need related rows).
- Schemas (Pydantic) are separate from models. Don't return ORM objects directly from endpoints.

## Migrations (Alembic)

Schema changes happen **only** through migrations. No hand-created tables, and no `Base.metadata.create_all()` outside throwaway tests.

1. Edit the model.
2. `alembic revision --autogenerate -m "describe change"`
3. **Read the generated file.** Autogenerate shows renames as drop + add (data loss), and can miss some constraints and enum changes.
4. `alembic upgrade head`

Rules:

- Never edit a migration that has been applied anywhere; write a new one.
- Commit every migration.
- Useful: `alembic current`, `alembic history`, `alembic downgrade -1` (fine locally; be cautious in production).
- Production deploys run `alembic upgrade head`.

## Data and ingestion

- Games are unique on chess.com's game identifier; ingestion must be idempotent (re-syncing never duplicates).
- Keep the raw PGN and raw API payload on `games` so fields can be backfilled without re-fetching.
- Analysis results (engine evaluations) go in their own tables, not columns on `games`.
- Naming: `chess_uuid` and `player_uuid` are chess.com's identifiers for a game and a player; `id` and `*_id` are our own row keys. `game_players` links to games through `game_uuid` and to tracked accounts through `player_uuid` (no foreign key; see D-018).
