# Project Management Foundation

A typography-first project management workspace for organizing projects, tasks, priorities, and team activity.

## Run & Operate

- `pnpm --filter @workspace/web run dev` — run the responsive web application
- `pnpm --filter @workspace/api-server run dev` — run the FastAPI server through the managed API workflow
- `alembic upgrade head` — apply PostgreSQL migrations
- `python -m backend.scripts.seed` — add a small local demo dataset when the database is empty
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: FastAPI with Pydantic schemas
- DB: PostgreSQL + SQLAlchemy
- Migrations: Alembic
- Frontend: React + Vite + TypeScript + Tailwind CSS (App Router-ready route structure)
- Validation: Pydantic at the backend boundary, generated Zod client schemas
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/web` — responsive frontend shell and theme system
- `backend` — FastAPI app, SQLAlchemy models, repositories, services, and routes
- `backend/alembic/versions` — migration history
- `lib/api-spec/openapi.yaml` — source of truth for generated TypeScript API hooks
- `lib/api-client-react` — generated React Query client

## Architecture decisions

- HTTP uses camelCase while Python modules and database columns use snake_case; Pydantic aliases keep that boundary explicit.
- FastAPI is served through the existing `/api` service path so the frontend uses relative, environment-safe URLs.
- Persistence is split into repositories and services so HTTP handlers remain thin and can evolve independently from the database layer.
- The first schema is intentionally small: projects, tasks, and activity establish the core product language without prematurely locking in collaboration features.

## Product

The workspace overview surfaces project progress, open work, and recent activity. Projects and tasks have typed list, create, update, and delete contracts, with light/dark appearance preferences available from the shell.

## User preferences

The interface should stay restrained and human: typography-led, whitespace-forward, subtle borders, no glassmorphism, oversized cards, neon colors, or large gradients.

## Gotchas

- Run `pnpm --filter @workspace/api-spec run codegen` after changing the OpenAPI contract.
- Run `alembic upgrade head` before calling data endpoints against a fresh database.
- The API workflow runs from the repository root so `backend.main:app` is importable.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
