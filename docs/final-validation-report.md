# Nomos mission planner — final validation report

**Phase:** T  
**Date:** 2026-07-20  
**Branch validated:** `cursor/phase-prompts-detail` (mission-planner build through Phase S)  
**Deploy:** Not performed in this phase (user did not request deploy). Artifacts and steps are ready below.

## Allowed product claim

> Nomos turns a space-data objective into a source-backed infrastructure plan. It searches real public data catalogs, calculates orbital and communication constraints, compares feasible execution paths, explains assumptions, and produces a shareable technical mission brief.

## Forbidden claims (verified absent from customer-facing plan payloads and UI copy)

- AI ran onboard a satellite
- Satellite was tasked
- Ground station reserved
- Commercial pricing guaranteed
- Private provider availability is live
- Execution occurred unless a real adapter completed it

---

## Completed features

| Area | Status |
| --- | --- |
| Private anonymous sessions + mission isolation | Done |
| Guided mission builder (`/plan`) | Done |
| Real STAC catalog discovery (Microsoft Planetary Computer) | Done |
| Fresh/pinned TLE provenance + calculated contact windows | Done |
| Source-backed planning engine (feasible / conditional / rejected) | Done |
| Truth-status labels + source evidence | Done |
| Mission result brief (`/missions/[id]`) | Done |
| Homepage centered on mission planning | Done (in branch; see deploy gap) |
| PDF + JSON export + private share links | Done (PDF needs WeasyPrint system libs) |
| Curated `/examples` with disclosures | Done |
| Lightweight CPU execution (`crop_geotiff`, `thumbnail`) with OBSERVED metrics | Done |
| Provider registry (YAML, public-data / sandbox_requested / simulated) | Done |
| Privacy-safe analytics + admin summary | Done |
| Mission feedback + design-partner capture | Done |
| Product docs + Python SDK `missions` namespace | Done |
| Accelerator demos 1–3 | Done |
| Security hardening (job tokens, rate limits, SSRF allowlist, log redaction) | Done |

---

## Tests run (2026-07-20)

### Backend (`orbital-cortex/apps/api`)

| Check | Result |
| --- | --- |
| `ruff check app tests scripts` | Pass (after Phase T lint/type cleanup) |
| `mypy app` | Pass — 119 source files |
| `pytest tests -q` | **137 passed**, 2 skipped |
| Migrations from current demo DB (`alembic upgrade head`) | Pass — already at `c3d4e5f6a7b8` |
| Migrations from empty PostGIS DB | Pass — full chain `→ c3d4e5f6a7b8` |
| Focused suites (contract / authz / planner / catalog / export / execution / security / SDK / demos) | Covered by full pytest run |

Skipped tests: optional WeasyPrint host smoke + one PDF integration skip when system libs are absent.

### Frontend (`orbital-cortex/apps/web`)

| Check | Result |
| --- | --- |
| `npm run lint` | Pass |
| `npx tsc --noEmit` | Pass |
| `npm run build` | Pass — routes include `/`, `/plan`, `/missions/[id]`, `/share/[token]`, `/examples` |

### Infrastructure

| Check | Result |
| --- | --- |
| Local API `/healthz` | Pass (`status: ok`) |
| Local API `/readyz` | Pass (`database: true`, `redis: false` expected without Redis) |
| Production API `https://api.nomosorbital.com/healthz` | Pass |
| Production API `/readyz` | Pass (`database: true`, **`redis: false`** — ops attention) |
| Production web `https://nomosorbital.com` | Up, but **behind** mission-planner branch (see deploy gap) |
| Docker build / docker-compose | **Not run on this host** — Docker CLI not installed. CI workflow still builds the image on push. |
| Object storage | Local artifact backend verified via CPU execution download URL |
| Redis worker | Not required for sync CPU fallback; ARQ cron for TLE refresh is registered (`refresh_tle_snapshot` / `precompute_passes` every 6h) |
| Scheduled demo cleanup | `.github/workflows/demo-reset.yml` present (nightly when `DEMO_DATABASE_URL` is set) |

### Manual acceptance flow

Validated against **local** API (`:8000`) + local prod web build (`:3015`). Production web still serves the pre–Phase D homepage.

| # | Step | Result |
| --- | --- | --- |
| 1 | Open homepage — understand in ~5s | Pass locally (mission-planning hero + Build a mission plan). Prod still shows legacy job demo. |
| 2 | Create private anonymous mission | Pass |
| 3 | Search real satellite data | Pass — 5 Planetary Computer candidates |
| 4 | Generate multiple plans | Pass — 4 plans |
| 5 | See rejected routes + reasons | Pass |
| 6 | See truth labels + sources | Pass |
| 7 | Export PDF + JSON | JSON Pass; PDF **fails on this Mac** without `libgobject` (WeasyPrint). Docker image includes libs; `test_exports.py` PDF path mocked + HTML presentation tests pass. |
| 8 | Create private share link | Pass |
| 9 | Open share in another browser profile | Pass (fresh cookie jar + share token) |
| 10 | Confirm unrelated missions inaccessible | Pass — 401/403 without owner session |
| 11 | Execute one lightweight CPU step | Pass — `crop_geotiff` succeeded |
| 12 | See measured OBSERVED values | Pass — `observed_truth_status=OBSERVED`, non-zero `execution_seconds` |
| 13 | Submit feedback | Pass |
| 14 | Request design-partner contact | Pass |
| 15 | Confirm no false tasking/reservation/onboard claims | Pass |

### Responsive + a11y smoke

- Skip link, `main#main-content`, demo `role="status"` banner present on `/`, `/plan`, `/examples`.
- Mission builder uses labeled radios + step navigation; examples page discloses real vs simulated.
- Desktop smoke verified in browser; mobile layout previously validated in Phase M/N (no horizontal clip on mission brief).

---

## Known limitations

1. **Production frontend lag:** `main` / live Vercel still serve the pre–mission-planner homepage (`/plan` and `/examples` 404 on nomosorbital.com). Mission-planner UI lives on this branch until merged and redeployed.
2. **Production Redis:** `/readyz` reports `redis: false` — async ARQ jobs and scheduled TLE refresh will not run until `REDIS_URL` is a valid Upstash `rediss://` URL and the worker machine is up.
3. **Host PDF generation:** WeasyPrint requires pango/cairo/gobject. Local macOS without those libs fails PDF export; Docker/Fly images include them.
4. **Cost estimates:** always `UNAVAILABLE` (by design).
5. **Satellite tracks on map:** `UNAVAILABLE` (API does not expose trajectory coordinates).
6. **STAC asset download / SAS signing:** not enabled; CPU demo uses fixtures / same-mission artifacts.
7. **Org accounts / billing / GPU / live tasking:** intentionally out of scope for this release.

---

## Remaining simulations

- Nomos simulated cloud provider (`SIMULATED`)
- Ground-station operational parameters (latency / downlink / availability) labeled `SIMULATED`
- Curated example reference scenes (`SIMULATED`) so examples always render a brief
- Legacy `/jobs` historical simulation demo (SIMULATED detections + execution)
- Design-partner registry rows that are `public_data_only` or `sandbox_requested` (cited public facts, not live APIs)

---

## Unavailable integrations

- Satellite tasking APIs → plans stay `conditional` (`tasking_api_unavailable`)
- Ground-station reservation → not performed
- Onboard / partner edge compute → plans `rejected` (`onboard_provider_unavailable`) until connected
- Commercial pricing sources
- Private telemetry
- Connected sandboxes (`sandbox_connected` / `partner_connected`) — none live today

---

## Local run instructions

```bash
# API + worker + Postgres + Redis (preferred)
cd orbital-cortex && docker compose up --build

# Or API against local PostGIS (this validation host used port 5433)
cd orbital-cortex/apps/api
export DATABASE_URL=postgresql://localhost:5433/orbital_cortex
export REDIS_URL=redis://127.0.0.1:6379/0   # or unreachable URL for sync fallback
export APP_ENV=development
export ARTIFACT_SIGNING_SECRET=dev-only-artifact-signing-secret
export ANALYTICS_HASH_SALT=dev-only-analytics-hash-salt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Web
cd orbital-cortex/apps/web
npm install
npm run dev
# open http://localhost:3000 — /api/oc proxies to the API for session cookies
```

Seed curated examples / accelerator demos:

```bash
cd orbital-cortex/apps/api
python -m app.seed
python -m app.seed --demo=1 --reset
python -m app.seed --demo=3 --reset --execute
```

---

## Deploy instructions

Do **not** block on GPU, tasking, billing, or full org auth.

### 1. Merge mission-planner branch to `main`

The validated code is ahead of `origin/main`. Merge (or open a PR) so Vercel and Fly CI pick up Phases D–T.

### 2. API (Fly.io)

```bash
# From repo with FLY_API_TOKEN, or rely on .github/workflows/deploy.yml on main
cd orbital-cortex
fly deploy -a orbital-cortex-api
```

Confirm secrets (see `orbital-cortex/docs/production-runbook.md`):

- `DATABASE_URL`, `REDIS_URL` (`rediss://…`), `S3_*`, `CORS_ORIGINS`, `PUBLIC_BASE_URL`
- Non-default `ARTIFACT_SIGNING_SECRET` and `ANALYTICS_HASH_SALT` in production
- Worker process group running (`fly machines list`)

Verify:

```bash
curl https://api.nomosorbital.com/healthz
curl https://api.nomosorbital.com/readyz   # expect redis: true after fix
```

### 3. Web (Vercel)

- Root: `orbital-cortex/apps/web`
- `NEXT_PUBLIC_API_BASE_URL=https://api.nomosorbital.com`
- Redeploy after env changes (build-time bake)
- Confirm `/plan` and `/examples` return 200 and homepage CTA is **Build a mission plan**

### 4. Post-deploy smoke

1. Homepage → Build a mission plan  
2. Discover → Generate plan → truth badges  
3. Export JSON (+ PDF)  
4. Share link in a second browser  
5. Owner-only Run CPU demo → OBSERVED  

---

## Accelerator demo instructions

Full spoken script: [`orbital-cortex/docs/accelerator-demo-script.md`](../orbital-cortex/docs/accelerator-demo-script.md)  
Limitations: [`orbital-cortex/docs/demo-limitations.md`](../orbital-cortex/docs/demo-limitations.md)

```bash
cd orbital-cortex/apps/api
python -m app.seed --demo=1 --reset            # NY Harbor / Sentinel-1
python -m app.seed --demo=2 --reset            # Disaster / Gulf
python -m app.seed --demo=3 --reset --execute  # Edge vs cloud + OBSERVED CPU

# Optional live STAC proof
python -m app.seed --demo=1 --reset --live
```

Open the printed mission URL with the demo session cookie (or run from a browser session you own). Say clearly: fixtures are pinned **real** Planetary Computer items; cloud steps remain `SIMULATED`; Demo 3 CPU metrics are `OBSERVED`.

---

## Highest-priority next provider integration

**KP Labs Smart Mission Lab** (`sandbox_requested` in the registry).

Why first:

- Already cited in the provider registry with a public sandbox product path
- Unlocks a real `sandbox_connected` edge/onboard alternative to the simulated cloud placeholder
- Directly reduces “rejected onboard” plans without inventing tasking or pricing

Follow-ons after KP Labs: EDGX compute-as-a-service, then Unibap/Ubotica documented APIs if sandbox credentials become available.

---

## Soul / docs alignment

Updated to carry the allowed claim:

- [`SOUL.md`](../SOUL.md)
- [`AGENTS.md`](../AGENTS.md)
- [`orbital-cortex/docs/capability-truth.md`](../orbital-cortex/docs/capability-truth.md)

---

## Phase T verdict

**Mission planner validation is complete for release documentation.**  
Automated suites pass. Manual private-mission flow works end-to-end on the local stack. Production API is healthy but Redis is down; production web must be redeployed from this branch before customers see the mission planner UI.
