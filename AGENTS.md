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
- **Phase B (done, July 2026):** "Nomos Record" redesign — dark glass UI, Golden Record logo (`components/brand/NomosMark.tsx`), three.js orbital hero (`components/orbital/OrbitalScene.tsx`), demo-first homepage (`DemoLauncher`), contact-window Gantt, Fraunces/Inter/Plex Mono via next/font. No API key field in UI; demo uses shared `oc_demo_public` (API has no auth yet; POST /v1/jobs is rate-limited per IP). `CORS_ORIGINS` on Fly includes localhost:3000 for local dev against prod API.
- **Phase C:** Auth, real node adapters, constraint routing

## Commit / deploy

- CI: `.github/workflows/deploy.yml` — API tests + web build + Fly deploy on `main` (needs `FLY_API_TOKEN` secret)
- Do not commit secrets, `.env`, or `.cursor/`
