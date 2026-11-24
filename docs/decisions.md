# Decision log

This is the project's memory for _why_ things are the way they are. Read it before changing the schema, auth, ingestion, or architecture.

## How to maintain this file (rules for humans and Claude Code)

1. **Append-only.** New decisions go at the bottom of the log with the next number (`D-0NN`). Never renumber.
2. **Don't rewrite history.** Never edit the _Decision_ or _Why_ of an Accepted entry. To change a decision, add a new entry that says what changed and why, then change the old entry's **Status** to `Superseded by D-0NN`. That status line is the only edit allowed on an old entry.
3. **Corrections and new facts** (e.g. a field verified against a real API response) go in an `Update (YYYY-MM-DD):` line under the entry, not as a silent rewrite.
4. **Open questions are entries** with Status `Open`. When resolved, set the old entry to `Resolved by D-0NN` and record the outcome in a new entry.
5. **Keep the index current.** The table below lists every entry; update its Status column whenever a status changes.
6. **Keep entries short** (a few lines). Link to code or docs for detail.
7. **Statuses:** `Accepted`, `Planned` (decided, not yet built), `Open`, `Superseded by D-0NN`, `Resolved by D-0NN`.
   Entry template:

```
### D-0NN Title
- **Date:** YYYY-MM-DD
- **Status:** Accepted
- **Context:** why this came up
- **Decision:** what was chosen
- **Why / alternatives rejected:** reasoning
```

## Index

| ID    | Title                                                                     | Status   |
| ----- | ------------------------------------------------------------------------- | -------- |
| D-001 | MVP scope: ingestion and aggregation first                                | Accepted |
| D-002 | Schema changes only via Alembic migrations                                | Accepted |
| D-003 | Config via pydantic-settings and env vars                                 | Accepted |
| D-004 | Sync SQLAlchemy 2.0 with psycopg 3                                        | Accepted |
| D-005 | Backend folder layout                                                     | Accepted |
| D-006 | Game players in a child table                                             | Accepted |
| D-007 | Use `relationship` selectively                                            | Accepted |
| D-008 | Idempotent ingestion keyed on chess.com game identifier                   | Accepted |
| D-009 | Keep raw PGN and raw API payload                                          | Accepted |
| D-010 | Opening data: store ECO and name, derive family later                     | Superseded by D-017 |
| D-011 | Global chess accounts linked to users via a join table                    | Accepted |
| D-012 | Multi-user schema now, login later                                        | Accepted |
| D-013 | Engine analysis: own tables, positional "same mistake", background worker | Planned  |
| D-014 | How to derive `opening_family`                                            | Open     |
| D-015 | Hosting platform (needs a Stockfish worker)                               | Open     |
| D-016 | Frontend stack                                                            | Accepted |
| D-017 | Opening data: store only `eco` for now                                    | Accepted |

## Log

### D-001 MVP scope: ingestion and aggregation first

- **Date:** 2026-11-23
- **Status:** Accepted
- **Context:** The project aggregates a user's chess.com accounts to produce insights about their play.
- **Decision:** The MVP is data ingestion and aggregation (win/loss rates by opening, color, time control; rating over time). Engine-based analysis is the direction after the MVP and must not block it. Target insight: "You lose 54% of your games when you play the Queen's Gambit as white, often with the same mistake, as seen in this specific game." Single user for now, but the app should be shareable (see D-011, D-012).
- **Why:** Aggregates are the core value; analysis builds on stored, correctly deduplicated games.

### D-002 Schema changes only via Alembic migrations

- **Date:** 2026-11-16
- **Status:** Accepted
- **Context:** Needed a way to create tables that transfers from local to production.
- **Decision:** All schema changes go through Alembic migrations. No hand-created tables (psql/pgAdmin) and no `create_all()` outside throwaway tests. Production deploys run `alembic upgrade head`.
- **Why:** `create_all()` can't alter existing tables; hand edits can't be reproduced in production.

### D-003 Config via pydantic-settings and env vars

- **Date:** 2026-11-16
- **Status:** Accepted
- **Decision:** A `Settings(BaseSettings)` class in `app/config.py`. Local values in a gitignored `.env` (with a committed `.env.example`); production uses real environment variables. Required fields fail fast at startup.
- **Why:** Typed, validated, single place for config; the same code works locally and in production.

### D-004 Sync SQLAlchemy 2.0 with psycopg 3

- **Date:** 2026-11-20
- **Status:** Accepted
- **Decision:** Sync SQLAlchemy 2.0, PostgreSQL via psycopg 3 (`postgresql+psycopg://`). chess.com HTTP calls may still be async via httpx, independent of the DB layer.
- **Why:** Async SQLAlchemy adds real complexity (no implicit lazy loading, session lifecycle gotchas); FastAPI runs plain `def` endpoints in a threadpool, which is enough at this scale.

### D-005 Backend folder layout

- **Date:** 2026-11-20
- **Status:** Accepted
- **Decision:** `be/app/{config.py, database.py, main.py, models/, schemas/, routers/, services/}`, with Alembic at the `be/` root. `database.py` holds the engine, session factory, `Base` and `get_db`. Models import `Base`; `database.py` never imports models; `models/__init__.py` imports every model. Folders are created when needed, not up front. No repository layer; services call the session directly.

### D-006 Game players in a child table

- **Date:** 2026-11-23
- **Status:** Accepted
- **Context:** Each game has a white and a black player with the same shape.
- **Decision:** Table `game_players`, one row per color per game, unique on `(game_id, color)`, with username, rating, result, and a nullable `account_id` (set only when the player is a tracked chess.com account). The API may still expose nested `white` / `black` objects.
- **Why:** Aggregates dominate, and nearly every insight is from one account's side of the game. With one row per side, "my rating/result" is a column and the opponent is the other row, instead of a `CASE WHEN white_username = ...` in every query. Flat columns and JSONB were rejected for that reason.

### D-007 Use `relationship` selectively

- **Date:** 2026-11-23
- **Status:** Accepted
- **Decision:** Foreign keys everywhere they apply; ORM `relationship` only where object navigation helps (e.g. `Game.players`, possibly `User.chess_accounts`). Aggregations use explicit joins.
- **Why:** Lazy loading causes N+1 queries; each relationship is more code to reason about.

### D-008 Idempotent ingestion keyed on chess.com game identifier

- **Date:** 2026-11-23
- **Status:** Accepted
- **Decision:** Unique constraint on chess.com's game identifier (verify the exact field, likely a `uuid`, against a real API response). Re-syncing never creates duplicates. A game can appear in two accounts' archives (two tracked accounts played each other), so dedupe on that identifier.

### D-009 Keep raw PGN and raw API payload

- **Date:** 2026-11-23
- **Status:** Accepted
- **Decision:** `games` stores the full PGN (text) and the raw API payload (JSONB).
- **Why:** New fields can be backfilled later without re-fetching from chess.com. JSONB is for raw storage only, not for querying aggregates.

### D-010 Opening data: store ECO and name, derive family later

- **Date:** 2026-11-23
- **Status:** Superseded by D-017
- **Decision:** Extract `eco` and the opening name from PGN headers at ingestion (verify header fields against real data) and store them on `games`. `opening_family` is a nullable derived column, recomputable from stored PGN/raw data. See D-014 for how to derive it.
- **Why:** Chess.com's opening names are very specific; grouping by raw name creates many tiny buckets, so a coarser family is needed for meaningful stats. Because source data is stored (D-009), the rule can change without re-ingesting.

### D-011 Global chess accounts linked to users via a join table

- **Date:** 2026-11-23
- **Status:** Accepted
- **Context:** Users may have several chess.com accounts, and ownership can't be verified through the public API, so two app users can add the same username.
- **Decision:** `chess_accounts` is global: one row per chess.com username (unique), holding per-account data such as last-synced time. `user_chess_accounts (user_id, chess_account_id)` links users to accounts (composite primary key, foreign keys on both columns). Games are ingested once per username.
- **Why / alternatives rejected:** `user_id` on `chess_accounts` collides with the unique game identifier (D-008) and with `game_players.account_id` when two users add the same username. A list/array of accounts on `users` can't be referenced by foreign keys and has nowhere to hold per-account data.

### D-012 Multi-user schema now, login later

- **Date:** 2026-11-23
- **Status:** Accepted
- **Decision:**
  - Now: a `users` table and the join table from D-011; a `get_current_user` FastAPI dependency that returns one seeded user; every endpoint touching accounts or games depends on it and filters by it. Real auth later is a change to that one function.
  - Later, after ingestion and aggregation work end to end: own login. FastAPI's docs recommend `pwdlib` (Argon2) for password hashing, with PyJWT for tokens. Choose token placement then: bearer token (simpler; XSS exposure if kept in JS-accessible storage) vs `httpOnly` cookie (safer; needs CORS-with-credentials and CSRF handling; dev origins differ: `localhost:5173` vs `localhost:8000`).
  - Avoid `fastapi-users` (in maintenance mode).
  - Chess.com account ownership is unverified: the public API can't prove a user owns a username, so adding an account is only a claim. Don't present accounts as verified. "Sign in with Chess.com" OAuth exists but requires applying via a form (not self-service), so the MVP must not depend on it.

### D-013 Engine analysis: own tables, positional "same mistake", background worker

- **Date:** 2026-11-23
- **Status:** Planned
- **Decision:** Analysis results get their own tables (e.g. per-move evaluations: game, ply, normalized position, move played, eval before/after, best move), not columns on `games`. "Same mistake" is positional: same normalized position + side to move + same bad move, with an eval-drop threshold. Analysis is CPU-heavy and runs outside the request cycle in a background worker, with Stockfish installed where the worker runs (likely Docker). Opening classification does not need an engine; ECO comes from the game data.

### D-014 How to derive `opening_family`

- **Date:** 2026-11-23
- **Status:** Open
- **Context:** Options: ECO code ranges, parsing the opening name, or an open openings dataset (e.g. lichess's `chess-openings`; confirm current format and license first). Decide after looking at real ingested data and how many games land in each bucket.
- **Update (2026-11-24):** Deferred; D-017 drops `opening_family` from the schema for now. This stays Open until a family is actually needed.

### D-015 Hosting platform

- **Date:** 2026-11-23
- **Status:** Open
- **Context:** The analysis phase needs a CPU-capable worker with Stockfish installed (D-013), which rules out some free tiers and points to Docker. Decide before choosing a platform.

### D-016 Frontend stack

- **Date:** 2026-11-24
- **Status:** Accepted
- **Decision:** React with Vite; MUI for components, with Emotion for styled components; TanStack Router for routing and TanStack Query for server state; yarn as the package manager. Lives in `fe/`.
- **Why:** Owner's choice. Frontend env variables (anything `VITE_`-prefixed) are bundled into the public JavaScript, so they must never hold secrets; the backend URL is fine.

### D-017 Opening data: store only `eco` for now

- **Date:** 2026-11-24
- **Status:** Accepted
- **Context:** D-010 planned to store `eco`, the opening name, and a derived `opening_family` on `games`. The name and family aren't needed yet.
- **Decision:** `games` stores only `eco`. No opening name or `opening_family` columns for now; opening aggregates group by `eco`. The raw PGN and API payload (D-009) are kept, so the name can be extracted later and `opening_family` added with a migration and backfill. D-014 (how to derive the family) stays Open.
- **Why:** ECO is enough for the MVP aggregates, and dropping the two columns avoids deciding the family rule (D-014) before there is real data to look at.
