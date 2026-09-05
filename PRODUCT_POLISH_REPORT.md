# Product polish report

## 1. Problems found

### Performance

- Project lists issued one task-count query per project (an N+1 query pattern).
- Dashboard task metrics required four separate task queries.
- Common project, task, membership, and activity ordering/filtering paths lacked composite indexes.
- Authentication and not-found screens were bundled eagerly.
- The global keyboard listener was detached and attached again after every shell render.

### UI and accessibility

- The global search trigger was not connected to the command palette.
- Project search only considered the currently loaded default page and omitted descriptions.
- The mobile navigation trigger did not have an accessible name.
- Command-palette focus was not restored to its trigger when the dialog closed.
- Keyboard shortcuts needed safeguards to avoid firing while a user typed in a form.

### Security and correctness

- Dashboard counts were workspace-global, exposing aggregate information from projects the current user could not access.
- Legacy dashboard activity was keyed only by project name, so it could not be reliably permission-scoped.
- Authentication endpoints had no request throttling.
- Browser mutation requests had no explicit cross-site request protection.
- Task status and priority accepted arbitrary strings; blank-only task titles were accepted.
- Several request models silently ignored unknown fields.
- Project keys and color values lacked format constraints.
- Member removal attempted to log an undefined variable and failed at runtime.

### Code quality and testing

- Activity ordering did not consistently use an ID tie-breaker.
- There was no automated permission/data-isolation coverage.
- There was no authentication throttling or input-validation coverage.
- The repository does not currently contain a browser end-to-end test harness.

## 2. Fixes applied

### Performance

- Replaced per-project task counts with one grouped bulk query.
- Consolidated dashboard task metrics into one aggregate query.
- Added migrations for composite indexes supporting project, task, membership, and activity queries.
- Added lazy loading for authentication and not-found routes.
- Stabilized the new-project callback and keyboard-listener effect.
- Kept command-palette and project-search filtering local and bounded to avoid requests per keystroke.

### UI and accessibility

- Added the searchable command palette and connected the top-bar search control.
- Added Ctrl/Cmd+K, N, Arrow Up/Down, Enter, and Escape behavior.
- Expanded project search to name, key, and description across up to 50 loaded projects.
- Added dialog, combobox, listbox, option, live-region, accessible-name, and focus-restoration behavior.
- Preserved the existing spacing/type system and extended it consistently for responsive palette layouts.
- Retained the existing responsive breakpoints and dark-theme token system.

### Security and correctness

- Scoped dashboard project/task aggregates to the authenticated user's memberships.
- Added relational project IDs to legacy activity rows and scope activity through memberships.
- Added cross-site mutation rejection using Fetch Metadata and validated Origin headers.
- Added a bounded sliding-window authentication rate limiter with Retry-After responses.
- Restricted task statuses and priorities to supported values and enforced field lengths/blank checks.
- Rejected unknown auth, project, and membership payload fields.
- Added project-key and color format validation.
- Fixed member-removal activity logging.

### Tests and verification

- Added activity creation, editing, invitation, ordering, pagination, and removal tests.
- Added dashboard tenant-isolation, viewer permission, input validation, and rate-limit tests.
- All 11 backend tests pass.
- Python compilation and TypeScript project/frontend checks pass.
- Alembic reports a single migration head: `0007_scope_legacy_activity`.
- Diff whitespace validation passes.

## 3. Remaining technical debt

- There is no committed Playwright/Cypress suite, so a complete browser E2E run, automated accessibility audit, visual mobile verification, and dark-mode visual regression could not be performed. No browser was available in this environment.
- The local production build is blocked by a missing platform-specific optional Rollup binary in the installed dependency tree; TypeScript compilation succeeds.
- Authentication throttling is process-local. Multi-instance production deployments should use a shared Redis-backed limiter and trusted-proxy-aware client identification.
- CSRF protection uses modern browser Fetch Metadata plus Origin validation. A double-submit or synchronizer token would provide defense for older/nonstandard clients.
- Project search uses `%term%` matching. At larger scale, PostgreSQL trigram or full-text indexes should replace it.
- Mutation repositories commit independently, so multi-step project/member changes and their activity logs are not yet one atomic transaction.
- Legacy workspace activity and project activity logs remain separate concepts and should eventually be unified.
- The single large `App.tsx` limits route-level code splitting and makes focused component tests harder.
- The development session secret must be replaced and managed through a secret store in production.

## 4. Recommended next features

1. Add Playwright journeys for registration/login, project/task CRUD, membership roles, activity pagination, command-palette navigation, mobile viewports, and dark mode.
2. Add axe accessibility assertions and screenshot-based visual regression in CI.
3. Move authentication rate limits and session revocation state to Redis.
4. Unify all project/task/member events in one workspace activity stream.
5. Add PostgreSQL full-text/trigram global search with cursor pagination.
6. Split `App.tsx` into lazy route modules and reusable feature components.
7. Add audit-log retention/export controls and administrator security alerts.
