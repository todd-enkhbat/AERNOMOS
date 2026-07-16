# Current system audit — Nomos Orbital (July 2026)

This document is a point-in-time audit of the deployed AERNOMOS / Nomos Orbital system,
written **before** the mission-planner transformation. It identifies what exists, what is
real, what is simulated, where privacy risks live, and what must change. No production
behavior was modified in this phase.

Companion docs: [capability-truth.md](capability-truth.md) (customer-safe claims),
[architecture.md](architecture.md), [api-spec.md](api-spec.md), [`SOUL.md`](../../SOUL.md).

---

## 1. Backend architecture

- **Framework:** FastAPI (`apps/api/app/main.py`) with routers in `app/routes/`
  (`jobs`, `nodes`, `registry`, `routing`, `results`, `artifacts`).
- **Persistence:** Neon Postgres + PostGIS via SQLAlchemy 2.x (`app/db/orm.py`),
  Alembic migrations (`migrations/versions/`, 7 revisions), auto-run at startup
  (`app/db/migrate.py`).
- **Queue / worker:** Upstash Redis + ARQ. `POST /v1/jobs` enqueues `execute_job`;
  the worker (`app/workers/executor.py`) drives `run_pipeline`
  (`app/core/pipeline.py`) through the state machine
  `queued → routing → executing → downlinking → complete` (`app/core/state.py`).
  A 6-hourly cron precomputes contact windows (`app/workers/passes.py`).
- **Dev fallback:** `POST /v1/simulate/run/{job_id}` runs the same pipeline
  synchronously when Redis is unavailable.
- **Object storage:** Cloudflare R2 (S3 API) or local HMAC-signed artifacts
  (`app/core/object_store.py`). Pipeline uploads `results/{job_id}/detections.geojson`
  and `summary.json`.
- **Middleware:** CORS (env-driven origins), request-id logging, structured
  exception handlers, optional Sentry.
- **Rate limiting:** slowapi keyed by client IP, applied **only** to
  `POST /v1/jobs` (`app/core/ratelimit.py`, default `10/minute`).
- **Deployment:** Fly.io app `orbital-cortex-api` (region `ewr`) with `app` and
  `worker` processes (`fly.toml`); Alembic runs as the release command.

## 2. Frontend pages

Next.js app at `apps/web` deployed on Vercel (`nomosorbital.com`):

| Route | Purpose |
| --- | --- |
| `/` | Homepage: three.js `OrbitalScene` hero, `DemoLauncher`, pipeline explainer |
| `/dashboard` | Ops overview: jobs, nodes, routes, costs |
| `/jobs` | **Public all-jobs feed** + job-create form |
| `/jobs/[id]` | Job detail: routing, timeline, detection map, replay |
| `/network` | Node registry, satellites, ground stations, contact-window Gantt |
| `/calendar` | Industry calendar with ICS/CSV export |
| `/about`, `/about/final-symposium` | Company pages |
| `/docs` | API/SDK snippets (shows the shared demo key) |

API access is client-side fetch (`lib/api.ts`) against `NEXT_PUBLIC_API_BASE_URL`
with a hardcoded shared bearer token `oc_demo_public` (`lib/constants.ts`) that the
API does not actually verify.

## 3. Database models

All in `apps/api/app/db/orm.py` (string PKs like `job_x7f3...`, ISO-string timestamps):

| Model | Table | Notes |
| --- | --- | --- |
| `Job` | `jobs` | Job spec + status; AOI as JSONB |
| `ComputeNode` | `compute_nodes` | **Fictional** nodes; orbital ones reference a real `satellite_id` |
| `GroundStation` | `ground_stations` | Real public coordinates; authored ops parameters |
| `Satellite` | `satellites` | Real NORAD IDs + TLEs, `source`, `snapshot_id` |
| `ContactWindow` | `contact_windows` | SGP4-propagated pass cache |
| `RoutingDecision` | `routing_decisions` | Deterministic audit: hashes, seed, inputs, TLE snapshot |
| `RoutingCandidate` | `routing_candidates` | Per-node eligibility + scores |
| `Scene` | `scenes` | PostGIS `geometry(Polygon,4326)`; pinned NY Harbor metadata |
| `Detection` | `detections` | PostGIS points; **canned vessels** |
| `JobEvent` | `job_events` | Append-only trail with monotonic `seq` |
| `Result` | `results` | Mock inference summary + GeoJSON |

There is **no** user, session, organization, mission, share-link, provenance, or
truth-status model.

## 4. Job lifecycle

1. `POST /v1/jobs` validates a versioned spec (Pydantic), persists `queued`, emits
   `job_created`, enqueues to ARQ.
2. Worker runs `run_pipeline`: routing (real scoring math over simulated nodes),
   then **timed stage theater** for `executing` and `downlinking`
   (`WORKER_STAGE_DELAY_S`), emitting events.
3. Completion calls `generate_mock_result` (`app/core/mock_inference.py`),
   uploads artifacts, and — for `ship_detection` — pins the canned NY Harbor
   scene + detections into PostGIS (`app/services/scenes.py`).

No real data is acquired, transferred, or processed at any stage.

## 5. Routing logic

- `app/routing/constraints.py`: hard constraints — model support, compliance tags,
  compute-preference exclusion, budget, deadline, downlink volume vs. pass capacity.
- `app/routing/scorer.py`: weighted soft scoring (model, latency, cost, availability,
  contact wait, preference, compliance) with priority-dependent weights;
  `ROUTING_CONFIG_VERSION = "2026.07.05-1"`.
- Orbital candidates use the **real** next SGP4 contact window for their satellite.
- `app/routing/replay.py` + `POST /v1/jobs/{id}/replay`: deterministic replays with
  input/decision hashes.
- The scorer selects **one** node with one fallback. It does not generate alternative
  end-to-end plans, does not express rejections in customer terms, and its cost /
  latency / availability inputs are authored fiction.

## 6. Satellite / TLE data sources

- Fleet: Sentinel-1A, Sentinel-1C, ICEYE-X2, Capella-14, Capella-15 (real NORAD IDs)
  defined in `app/services/tle_cache.py`.
- Default: **pinned snapshot** `simulator/tle_snapshot.json` (dated CelesTrak capture).
- Optional live refresh from CelesTrak GP by NORAD ID (`LIVE_TLE=true`), but there is
  **no scheduled refresh, no staleness detection, and no user-visible epoch labeling**.
- Contact windows: Skyfield `EarthSatellite` + `find_events`
  (`app/services/contact_windows.py`), precomputed off the request path, cross-checked
  against raw `sgp4` in tests. This is real physics over possibly stale elements.

## 7. Ground-station data

`simulator/ground_stations.json`, seeded by `app/seed.py`. Names and coordinates are
real public sites (KSAT Svalbard/Tromsø, AWS Ground Station regions, Leaf Space);
elevation masks are plausible defaults; `latency_minutes`, `downlink_mbps`, and
`availability` are **authored demo parameters** with no provider connection and no
source metadata or access-level labeling.

## 8. Simulated node data

`simulator/sample_nodes.json` — e.g. `sim_leo_01`, `aws_us_east_gpu` — with fictional
GPU classes, storage, power state, availability percentages, base costs, and latency.
The OpenAPI tag for `/v1/nodes` says "Simulated compute-node registry," and the
dashboard labels them simulated, but the values are indistinguishable in structure from
real ones and drive the routing decision shown to users.

## 9. Simulated inference and output generation

`app/core/mock_inference.py`:

- `ship_detection`: 17 hardcoded NY Harbor vessels with authored confidences
  (0.78–0.94), fabricated length/heading estimates, and "review/monitor" priorities.
- `crop_health`: one hardcoded stress polygon, confidence 0.84.
- `disaster_response`: one hardcoded flood point, confidence 0.88.

`app/services/scenes.py` + `simulator/ny_harbor_scene/` pin a canned SAR scene
(with a real-format STAC item id) and detections. Result summaries read like real
mission output ("Detected 17 likely vessels…"). This is the **primary customer-facing
output** of the product today.

## 10. Authentication behavior

**None.** No API keys are verified, no users, no tenants, no sessions. The frontend
sends `Authorization: Bearer oc_demo_public` on job creation only; the API ignores it.
The only abuse control is the per-IP rate limit on job creation.

## 11. Public job exposure

- `GET /v1/jobs` lists **every job from every visitor**, unauthenticated,
  cursor-paginated.
- `GET /v1/jobs/{id}` (+ `/events`, `/routing`, `/result`, `/scene`, `/detections`)
  are readable by anyone who has or guesses an id.
- The `/jobs` page renders the global feed in public navigation; `/dashboard`,
  `/network`, and the homepage `SdkResultPreview` also read the global list.
- Any AOI, budget, deadline, or job parameters a visitor submits are therefore
  **publicly visible to all other visitors**. This is the highest-priority privacy
  risk in the system.

## 12. Deployment setup

| Surface | Mechanism |
| --- | --- |
| API + worker | Fly.io `orbital-cortex-api` (`fly.toml`), Docker, Alembic release command |
| Frontend | Vercel, root `apps/web`, `NEXT_PUBLIC_API_BASE_URL` |
| DNS | Cloudflare — `nomosorbital.com`, `api.nomosorbital.com` |
| DB / Redis / artifacts | Neon, Upstash, Cloudflare R2 |
| CI | `.github/workflows/deploy.yml` (ruff/mypy/pytest, SDK tests, web lint+build, Docker build, Fly deploy on `main`) |
| SDK codegen | `.github/workflows/sdk.yml` regenerates `orbitalcortex_api` from `openapi.json` |
| Demo reset | `.github/workflows/demo-reset.yml` — nightly `app.seed --reset --force` |

## 13. Test coverage

~20 test functions in 4 files under `apps/api/tests/`:

- `test_api.py` — end-to-end simulate run, worker pipeline, registry, validation,
  state machine (5).
- `test_platform.py` — health, pagination, artifacts, rate limit, seed reset (7).
- `test_routing_audit.py` — replay determinism, budget constraints, PostGIS
  detections (3).
- `test_contact_windows.py` — SGP4 vs. Skyfield cross-check, elevation masks,
  snapshot handling, downlink estimates (5).

No tests exist for authorization (nothing to authorize), privacy, catalog data,
or exports. Frontend has lint + build in CI but no component/e2e tests.

## 14. Technical debt

- ISO-string timestamps instead of `timestamptz` columns.
- Client-only data fetching in the web app; dashboard N+1 request patterns.
- `Job.area_of_interest_json` still JSONB while `Scene.aoi` is PostGIS.
- Shared fake bearer token implies auth that does not exist.
- Simulated node parameters are structurally identical to real values (no
  truth-status field anywhere in the schema).
- No scheduled TLE refresh; live mode is opt-in and unmonitored.
- Rate limiting only on job creation; all read endpoints are unmetered.
- No provenance model: sources, retrieval timestamps, and methods are not recorded
  per value.

## 15. Component truth table

| Component | Current implementation | Truth status | Customer value | Required change |
| --- | --- | --- | --- | --- |
| FastAPI + ARQ + Postgres/PostGIS + Redis + R2 | Production on Fly/Neon/Upstash/R2 | OBSERVED (real infra) | High — foundation | Keep; extend with mission models |
| Job lifecycle + events | Real persistence, real state machine | OBSERVED | Medium | Keep for legacy demo; supersede with Mission flow |
| Routing scorer + replay | Real deterministic math over fictional inputs | CALCULATED over SIMULATED inputs | Medium | Reuse patterns in new planner over registry-backed resources |
| Contact windows | Skyfield/SGP4 over pinned TLEs | CALCULATED (STALE risk) | High | Scheduled refresh, snapshot provenance, staleness labels |
| Satellites / TLEs | Real NORAD IDs, pinned CelesTrak snapshot | OBSERVED but STALE | High | Live refresh + epoch labeling |
| Ground stations | Real coordinates, authored ops params | Mixed: OBSERVED coords, SIMULATED params | Medium | Source metadata + access-level labels |
| Compute nodes | Fictional JSON registry | SIMULATED | Low (misleading) | Replace with `InfrastructureResource` registry, truth-labeled |
| Inference results / detections | Hardcoded mock output | SIMULATED (unlabeled at value level) | Negative if mistaken for real | Demote to curated labeled examples |
| NY Harbor scene | Canned metadata + STAC-format id | SIMULATED | Low | Replace with real STAC discovery |
| Costs / latency estimates | Authored numbers | SIMULATED | Negative if mistaken for real | Only show estimates with provenance |
| Auth / privacy | None; global public job feed | UNAVAILABLE | Critical gap | Anonymous private sessions + share links |
| Data catalog search | None | UNAVAILABLE | Critical gap | Real STAC provider (Planetary Computer) |
| Mission planning / alternatives | None (single-node choice) | UNAVAILABLE | Critical gap | Feasibility + multi-plan engine |
| Exports / sharing | None | UNAVAILABLE | High | PDF/JSON export + private share links |
| Real execution | None (stage theater) | UNAVAILABLE | High | Lightweight CPU execution provider |
| SDK | Real client for current API | OBSERVED | Medium | Add `missions` resource + typed errors |
| Analytics | None (Sentry optional) | UNAVAILABLE | Medium | Privacy-safe product/ops metrics |

## Summary of simulation points

1. `app/core/mock_inference.py` — all job results.
2. `simulator/sample_nodes.json` — all compute nodes, costs, availability.
3. `simulator/ny_harbor_scene/` + `app/services/scenes.py` — canned scene/detections.
4. `app/core/pipeline.py` — timed `executing`/`downlinking` stages (no work performed).
5. `simulator/ground_stations.json` — authored latency/downlink/availability params.
6. `simulator/tle_snapshot.json` — pinned (aging) orbital elements used by default.
7. `oc_demo_public` — decorative bearer token; no verification.

## Summary of privacy risks

1. Global unauthenticated job feed (`GET /v1/jobs`, `/jobs` page).
2. All job sub-resources readable by id with no ownership check.
3. No session or ownership model; ids are the only (non-)control.
4. User-submitted AOIs/budgets/deadlines visible to all visitors.
5. No warning against submitting proprietary or export-controlled information.
6. Read endpoints unmetered (enumeration by pagination is trivial and by design).
