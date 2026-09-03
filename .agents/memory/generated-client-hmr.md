---
name: Generated client HMR
description: A transient Vite development-server behavior during Orval client regeneration.
---

When OpenAPI codegen cleans and recreates the generated React client files, the running Vite server can briefly emit missing-module and failed-HMR warnings while those files are between states.

**Why:** Orval replaces the generated output directory rather than updating every generated file atomically from Vite's perspective.

**How to apply:** Treat the warning as transient if the generated client typechecks and the next full page refresh loads successfully; restart the frontend only when the stale module state persists.