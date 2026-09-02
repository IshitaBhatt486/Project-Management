# Project Management Foundation

A modern project-management foundation with a responsive workspace shell, typed project/task APIs, and a PostgreSQL-backed FastAPI service.

## What is included

- Responsive Workbench UI with overview, projects, project detail, tasks, activity, and settings routes
- Light and dark appearance modes with local persistence
- FastAPI backend with Pydantic request/response validation
- SQLAlchemy models and session management
- Repository and service layers for projects, tasks, and activity
- Alembic migration baseline
- OpenAPI-first TypeScript client generation
- Demo seed data for a useful first load

## Project structure

```text
backend/
├── api/routes/          # FastAPI route handlers
├── core/                # Environment-backed settings
├── db/                  # SQLAlchemy base, models, and sessions
├── repositories/        # Database access
├── schemas/             # API request and response models
├── services/            # Application/business logic
├── alembic/versions/    # Database migration history
└── scripts/             # Operational helpers, including seed data
artifacts/
├── api-server/          # Managed API service configuration
└── web/                 # Responsive frontend artifact
lib/
├── api-spec/            # OpenAPI source of truth
├── api-client-react/    # Generated React Query hooks
└── api-zod/             # Generated validation schemas
```

## Environment

Set `DATABASE_URL` to a PostgreSQL connection string. The backend also accepts:

- `APP_NAME` (optional)
- `ENVIRONMENT` (optional)
- `CORS_ORIGINS` (optional, as a JSON list when using a `.env` file)

The backend normalizes provider URLs that begin with `postgres://` or `postgresql://` to the installed `psycopg` v3 driver.
Session cookies are HttpOnly and SameSite=Lax. The Secure flag is enabled for HTTPS requests when `SESSION_COOKIE_SECURE=true`; plain HTTP development previews omit only that flag so browsers can accept the session locally.

## Authentication

Authentication is implemented with bcrypt password hashes and signed JWTs stored in the `workbench_session` HttpOnly cookie.

- `POST /api/auth/register` creates an account and starts a session
- `POST /api/auth/login` verifies credentials and starts a session
- `GET /api/auth/me` restores the current session
- `POST /api/auth/logout` clears the session cookie
- Project, task, dashboard, and activity endpoints require an authenticated session

Use a long, private `SESSION_SECRET` in every non-development environment. Passwords and JWTs are never returned to the frontend or stored in browser storage.

## Local setup

Install workspace dependencies, then apply the database migration and seed the demo data:

```bash
pnpm install
alembic upgrade head
python -m backend.scripts.seed
```

Start the services through the managed workflows:

```bash
pnpm --filter @workspace/web run dev
uvicorn backend.main:app --host 0.0.0.0 --port 8080
```

The API is mounted at `/api`. The basic connectivity check is:

```bash
curl http://localhost:80/api/healthz
```

## Development checks

```bash
pnpm run typecheck
PORT=22333 BASE_PATH=/ pnpm --filter @workspace/web run build
python -m compileall -q backend
```

When `lib/api-spec/openapi.yaml` changes, regenerate the typed client:

```bash
pnpm --filter @workspace/api-spec run codegen
```

## Frontend runtime note

The selected web artifact uses the workspace’s React/Vite runtime so it can be previewed and published through the managed artifact service. Its route structure, typed API boundary, and modular shell are intentionally organized so the same product surface can be moved into a Next.js 15 App Router host without changing the backend contract.