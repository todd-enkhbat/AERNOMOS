# Agent onboarding — AERNOMOS / Nomos Orbital

Read this file first in any new chat session before making changes.

## Canonical product soul

Before writing site copy, changing product language, or touching visual design, read
[`SOUL.md`](SOUL.md). It is the canonical source for positioning, product truth,
terminology, voice, visual direction, and the simulation boundary. When a lasting
decision is not covered there, make it in that spirit and add it back.

For UI or motion work, also follow
[`orbital-cortex/docs/design-engineering-workflow.md`](orbital-cortex/docs/design-engineering-workflow.md).
Review the whole page in-browser at desktop and mobile widths; do not approve isolated
components while section rhythm, imagery, or fallbacks remain unverified.

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
| [docs/NOMOS_BUILD_PLAN.md](docs/NOMOS_BUILD_PLAN.md) | **Mission-planner master plan (phases A–T)** — persistent build context |
| [docs/phase-prompts/](docs/phase-prompts/README.md) | **Copy-paste agent prompts per phase (F–T)** — detailed implementation instructions |
| [docs/BUILD_PROGRESS.md](docs/BUILD_PROGRESS.md) | **Current build phase / blockers / decisions** — update after every phase |
| [orbital-cortex/docs/production-runbook.md](orbital-cortex/docs/production-runbook.md) | Ops, debugging prod, secrets checklist |
| [orbital-cortex/docs/deployment.md](orbital-cortex/docs/deployment.md) | First-time deploy |
| [orbital-cortex/docs/frontend-roadmap.md](orbital-cortex/docs/frontend-roadmap.md) | Legacy frontend roadmap (Nomos Record UI) |
| [orbital-cortex/docs/architecture.md](orbital-cortex/docs/architecture.md) | System design |
| [orbital-cortex/docs/api-spec.md](orbital-cortex/docs/api-spec.md) | REST contract |
| [orbital-cortex/docs/capability-truth.md](orbital-cortex/docs/capability-truth.md) | Customer-safe claims and demo boundaries |
| [orbital-cortex/docs/mission-planner-overview.md](orbital-cortex/docs/mission-planner-overview.md) | **Mission planner: what it does, who it's for** (Phase Q) |
| [orbital-cortex/docs/data-sources.md](orbital-cortex/docs/data-sources.md) | STAC/orbital sources + provider registry (source of truth, Phase Q) |
| [orbital-cortex/docs/truth-statuses.md](orbital-cortex/docs/truth-statuses.md) | **Canonical truth_status / integration_status vocabulary** (Phase Q) |
| [orbital-cortex/docs/planning-engine.md](orbital-cortex/docs/planning-engine.md) | How a request resolves to a plan (Phase Q) |
| [orbital-cortex/docs/privacy-model.md](orbital-cortex/docs/privacy-model.md) | Privacy/isolation model for a legal/security reader (Phase Q) |
| [orbital-cortex/docs/provider-integrations.md](orbital-cortex/docs/provider-integrations.md) | Adding a provider + SDK error mapping (Phase Q) |
| [orbital-cortex/docs/demo-limitations.md](orbital-cortex/docs/demo-limitations.md) | **Unhedged what-works / what-doesn't for a live call** (Phase Q) |
| [orbital-cortex/docs/accelerator-demo-script.md](orbital-cortex/docs/accelerator-demo-script.md) | Demo arc skeleton (Phase R finishes it) |
| [orbital-cortex/docs/current-system-audit.md](orbital-cortex/docs/current-system-audit.md) | Pre-mission-planner system audit: simulation points, privacy risks |
| [orbital-cortex/docs/design-engineering-workflow.md](orbital-cortex/docs/design-engineering-workflow.md) | UI, imagery, motion, and visual QA gates |
| [SOUL.md](SOUL.md) | Canonical product, copy, and design direction |
| [README.md](README.md) | Product vision |

## Nomos build workflow (mission planner)

Master plan: [`docs/NOMOS_BUILD_PLAN.md`](docs/NOMOS_BUILD_PLAN.md).  
Progress: [`docs/BUILD_PROGRESS.md`](docs/BUILD_PROGRESS.md).  
Always-applied Cursor rule: [`.cursor/rules/nomos-build-loop.mdc`](.cursor/rules/nomos-build-loop.mdc).

**Do not** execute phases A–T as one giant one-shot task. Use a **goal-based loop per phase**: continue until the current phase’s acceptance criteria pass (turn/time limits are safety caps only).

### Default entry

When the user says “continue the build”, “next phase”, “work on Nomos”, or “continue Nomos”:

1. Read both plan and progress files.
2. Execute **only** the phase listed as current / in progress (canonical order in the master plan — not alphabetical letter order).
3. Follow the build-loop rule until acceptance criteria pass.
4. Update `docs/BUILD_PROGRESS.md` and stop (do not start the next phase unless asked).
5. Commit only when the user explicitly asks, unless the phase prompt already requests the phase commit.

### For every implementation task

1. Read both plan and progress files before making changes.
2. Identify the current phase; inspect existing implementation; write a short execution plan.
3. Implement only that phase; do not rewrite unrelated systems.
4. Add or update tests; run validation; fix failures before declaring done.
5. Review the diff for security, regressions, fabricated data, and misleading claims.
6. Update `docs/BUILD_PROGRESS.md` (completed work, files, tests, issues, decisions, next phase).
7. Stop after the phase is fully validated and report the result.

A phase is complete only when acceptance criteria, tests, builds, applicable migrations, and docs are done — and no high-severity known issue remains. Never mark complete merely because code was written.

Never fabricate provider data, execution results, pricing, availability, confidence, or satellite activity. When real data is unavailable, use: OBSERVED, CALCULATED, PROVIDER_REPORTED, ESTIMATED, SIMULATED, STALE, UNAVAILABLE.

Stop and ask the user on: required external credential, irreversible production change, unclear product decision, or three distinct failed repair attempts on the same tests.

**Naming note:** Older “Phase A/B/C” bullets below refer to the pre-mission-planner product track (branding / Nomos Record UI / auth). For the mission-planner build, trust `docs/NOMOS_BUILD_PLAN.md` and `docs/BUILD_PROGRESS.md` (Phase A = audit, Phase B = data model, etc.).

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
- **Phase B (done, July 2026):** "Nomos Record" redesign — dark glass UI, Golden Record logo (`components/brand/NomosMark.tsx`), three.js orbital hero (`components/orbital/OrbitalScene.tsx`), contact-window Gantt, Fraunces/Inter/Plex Mono via next/font. No API key field in UI; demo uses shared `oc_demo_public` (API has no auth yet; POST /v1/jobs is rate-limited per IP). `CORS_ORIGINS` on Fly includes localhost:3000 for local dev against prod API.
- **Mission-planner Phase D (homepage):** Primary CTA is **Build a mission plan** → `/plan`. Job `DemoLauncher` is demoted off the homepage hero. See `SOUL.md` and `docs/BUILD_PROGRESS.md`.
- **Phase C (legacy product track):** Auth, real node adapters, constraint routing

## Commit / deploy

- CI: `.github/workflows/deploy.yml` — API tests + web build + Fly deploy on `main` (needs `FLY_API_TOKEN` secret)
- Do not commit secrets or `.env`. Commit `.cursor/rules/*.mdc` project rules; do not commit other local `.cursor/` state
