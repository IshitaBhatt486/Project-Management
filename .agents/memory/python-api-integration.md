---
name: Python API integration
description: Durable integration constraints for the Python API and generated client.
---

The managed database may expose a `postgresql://` or `postgres://` URL without a driver name, while the Python dependency set uses psycopg v3. Normalize those URLs to `postgresql+psycopg://` anywhere SQLAlchemy or Alembic creates an engine.

**Why:** SQLAlchemy otherwise falls back to the psycopg2 dialect and the FastAPI service fails before startup, even when psycopg v3 is installed.

**How to apply:** Keep the URL normalization shared by the runtime session and Alembic environment; do not expose database credentials in source or chat.

OpenAPI `integer` schemas can cause Orval to emit `z.int()`, which is incompatible with the installed Zod 3 runtime in this workspace.

**Why:** Codegen completes but the library typecheck fails on the generated validator API.

**How to apply:** Use the workspace-supported numeric schema type in the OpenAPI contract unless the validator dependency is intentionally upgraded alongside generated output.