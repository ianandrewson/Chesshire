# Frontend conventions

Stack: React, Vite, MUI, Emotion (styled components), TanStack Router, TanStack Query. Package manager: **yarn** (never npm). Rationale in `../docs/decisions.md` (D-016).

## Running

- From `fe/`: `yarn run dev` (Vite default port 5173).
- The backend runs separately (see `../be/CLAUDE.md`, default port 8000).
- The API base URL comes from a `VITE_`-prefixed env variable. Anything `VITE_`-prefixed is bundled into public JavaScript: **never put secrets in frontend env files.** Keep `fe/.env.example` current; never commit `.env` files.

## Conventions

- **Server state lives in TanStack Query.** Don't copy query data into `useState` or other global state. Mutations should invalidate or update the relevant queries.
- **Routing uses TanStack Router.** Don't introduce another router.
- **Styling uses MUI components plus Emotion `styled`.** Use theme values (spacing, palette, typography) instead of hardcoded colors and pixel values. Don't add another styling library.
- The backend returns Pydantic-shaped JSON; keep frontend types for API data in one place per resource instead of redefining them per component.
