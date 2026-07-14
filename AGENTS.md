# Agent onboarding — AERNOMOS / Nomos Orbital

Read this file first in any new chat session before making changes.

## What this repo is

| Layer | Path | Purpose |
| --- | --- | --- |
| **Repo name** | `AERNOMOS` | GitHub repo; keep this name |
| **Product (user-facing)** | **Nomos Orbital** | Company / website / API titles |
| **Deployable stack** | `orbital-cortex/` | FastAPI + Next.js + Python SDK — **this is production** |
| **MVS skeleton** | `src/nomos/` | In-process Python demo (submit → route → log); not deployed |

Do **not** rename `orbital-cortex/` directory, Fly app `orbital-cortex-api`, or Python package `orbitalcortex` without explicit request — infra depends on them.

## Live production (as of July 2026)

| Surface | URL |
| --- | --- |
| Website | https://nomosorbital.com |
| API | https://api.nomosorbital.com |
| API (Fly default) | https://orbital-cortex-api.fly.dev |
| Fly app | `orbital-cortex-api` (region `ewr`) |

## Stack map

| Concern | Provider | Env vars (Fly unless noted) |
| --- | --- | --- |
| API + worker | Fly.io | `fly.toml`, two processes: `app`, `worker` |
| Postgres + PostGIS | Neon | `DATABASE_URL` |
| Job queue | Upstash Redis | `REDIS_URL` — must be `rediss://...` URL, **not** `redis-cli` command |
| Artifacts | Cloudflare R2 | `S3_BUCKET`, `S3_ENDPOINT_URL`, `S3_*` |
| DNS | Cloudflare | `nomosorbital.com`, `api` A/AAAA → Fly IPs |
| Frontend | Vercel | root `orbital-cortex/apps/web`, `NEXT_PUBLIC_API_BASE_URL` |

**Cloudflare R2 is file storage, not Redis.** Redis (Upstash) is required for async job processing.

## Key docs

| Doc | Use when |
| --- | --- |
| [orbital-cortex/docs/production-runbook.md](orbital-cortex/docs/production-runbook.md) | Ops, debugging prod, secrets checklist |
| [orbital-cortex/docs/deployment.md](orbital-cortex/docs/deployment.md) | First-time deploy |
| [orbital-cortex/docs/frontend-roadmap.md](orbital-cortex/docs/frontend-roadmap.md) | Phase B UI work |
| [orbital-cortex/docs/architecture.md](orbital-cortex/docs/architecture.md) | System design |
| [orbital-cortex/docs/api-spec.md](orbital-cortex/docs/api-spec.md) | REST contract |
| [README.md](README.md) | Product vision |

## Common production issues

1. **Jobs stuck `queued`** — worker machine stopped on Fly. See runbook: `fly machines list`, start worker.
2. **"Failed to fetch" on Vercel** — wrong `NEXT_PUBLIC_API_BASE_URL` (must redeploy after change) or missing CORS origin on Fly `CORS_ORIGINS`.
3. **`redis: false` on `/readyz`** — bad `REDIS_URL` (often pasted Upstash CLI instead of `rediss://` URL).

## Local dev

```bash
cd orbital-cortex && docker compose up --build   # API + worker + Postgres + Redis
cd orbital-cortex/apps/web && npm install && npm run dev
```

## Codegen

```bash
# After API schema changes:
cd orbital-cortex/apps/api && python -m scripts.export_openapi ../../openapi.json
cd ../web && npm run generate:api-types
```

## Phase status

- **Phase A (done):** Branding, docs, OpenAPI TS types, frontend CI, production deploy
- **Phase B (next):** Marketing site + UX polish — see `frontend-roadmap.md`
- **Phase C:** Auth, real node adapters, constraint routing

## Commit / deploy

- CI: `.github/workflows/deploy.yml` — API tests + web build + Fly deploy on `main` (needs `FLY_API_TOKEN` secret)
- Do not commit secrets, `.env`, or `.cursor/`

## Cursor Cloud specific instructions

The cloud VM runs the stack **natively (no Docker)**. Postgres 16 + PostGIS and Redis are installed as system packages; the startup update script only refreshes code deps (Python venvs + `npm ci`). Services and infra are **not** auto-started — start them yourself each session:

```bash
# Infra (once per VM boot; data persists in the snapshot)
sudo pg_ctlcluster 16 main start        # Postgres+PostGIS on :5432 (db orbital_cortex, user/pass postgres/postgres)
sudo redis-server --daemonize yes        # Redis on :6379

# App services (dev mode, hot reload) — run each in its own tmux session
cd orbital-cortex/apps/api && . .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd orbital-cortex/apps/api && . .venv/bin/activate && arq app.workers.executor.WorkerSettings   # async job worker
cd orbital-cortex/apps/web && npm run dev            # UI on :3000
```

- Python deps live in two gitignored venvs: **API/worker/SDK** at `orbital-cortex/apps/api/.venv`, **MVS skeleton** at repo-root `.venv`.
- API config is read from `orbital-cortex/apps/api/.env` (gitignored) — already points `DATABASE_URL`/`REDIS_URL` at the local services. The API auto-runs Alembic migrations and seeds simulator data on startup, so a fresh DB self-populates.
- **Test gotcha:** run tests with the module form — `python -m pytest tests` (from `apps/api` or `sdk/python`). Bare `pytest tests` fails with `ModuleNotFoundError: No module named 'app'` (the repo has no src-layout/pythonpath config; this also fails in the current CI).
- **Lint scope:** API lint is `ruff check app tests scripts` (CI scope). `ruff check .` reports pre-existing failures in `migrations/`, which are intentionally out of scope.
- **Web lint gotcha:** there is no committed ESLint config, so `npm run lint` (`next lint`) prompts interactively on a PTY. To lint non-interactively, first create `orbital-cortex/apps/web/.eslintrc.json` = `{ "extends": "next/core-web-vitals" }` (CI auto-generates this in its non-TTY shell); do not commit it.
- Web typegen needs `orbital-cortex/openapi.json` (gitignored): regenerate with `python -m scripts.export_openapi ../../openapi.json` from `apps/api`, then `npm run generate:api-types`. Committed `lib/generated/api-types.ts` already matches the current schema.
- Handy API facts: completed job status string is `complete`; result manifest is at `GET /v1/jobs/{id}/result` (not `/v1/results/{id}`); local artifacts are served via signed URLs under `/v1/artifacts/...`.
