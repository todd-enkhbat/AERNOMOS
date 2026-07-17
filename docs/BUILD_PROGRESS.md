# Nomos Build Progress

Current phase: N (next)

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)
- Phase C: Anonymous private sessions + share-link access (`feat: add private anonymous mission sessions and share links`)
- Phase F: Real STAC catalog discovery via Microsoft Planetary Computer
- Phase H: Fresh orbital data provenance and mission-specific infrastructure
- Phase E: Guided customer-facing mission builder at `/plan`
- Phase G: Source provenance and truth-status labeling (API envelope + truth UI components)
- Phase I: Source-backed mission feasibility and planning engine
- Phase J: Customer-facing mission result experience at `/missions/[id]`
- Phase D: Homepage rewrite around mission planning outcomes
- Phase K: Mission brief PDF/JSON export + private sharing UI (`/share/[token]`)
- Phase L: Isolate simulations into clearly labeled examples (`/examples`, historical job demo)
- Phase M: Lightweight real CPU execution — `crop_geotiff` + `thumbnail` on the ARQ worker with OBSERVED metrics, plus mission-brief **Run CPU demo** UI (OBSERVED thumbnail + timeline)

## In progress
None — Phase M (backend + UI polish) complete. Next is Phase N (provider registry).

## Blockers
None

## Decisions
- Focus on mission planning before GPU execution.
- All user-facing values require truth-status labels.
- User missions must not be publicly enumerable.
- Follow the dependency-corrected execution order in `docs/NOMOS_BUILD_PLAN.md` (not alphabetical A→T).
- Prefer updating `orbital-cortex/docs/current-system-audit.md` as the Phase A audit location (not a duplicate under `docs/`).
- Phase B: mission tables are additive UUID + PostGIS models; legacy Job/Scene/Detection string-ID tables are unchanged so the demo path stays intact.
- Phase B: `organization_id` / `converted_user_id` are UUID columns without FKs until org/auth tables exist.
- Phase B: missions require at least one owner (`anonymous_session_id` OR `organization_id`) via CHECK constraint.
- Phase C: session + share tokens use `secrets.token_urlsafe(32)` with SHA-256 hashes only; raw tokens never stored.
- Phase C: production cookies are HttpOnly + Secure + SameSite=Lax with optional `Domain=.nomosorbital.com`; local dev uses host-only cookies via Next.js `/api/oc/*` rewrite proxy.
- Phase C: curated public examples use `missions.is_example=true` and a stable examples org UUID; private lists exclude them.
- Phase C: legacy `/jobs` remains reachable by direct URL for the demo but is removed from primary nav.
- Follow-up: public `GET /v1/jobs` lists curated `is_example` jobs only; visitor submissions are hidden from the list (still openable by ID). Seed promotes up to 3 complete jobs as examples when none exist.
- Phase F: primary STAC provider is Microsoft Planetary Computer (`sentinel-1-grd`; optional `sentinel-2-l2a`). Provider id string: `microsoft-planetary-computer`.
- Phase F: Earth Search (Element84) is a registered stub behind the same `DataCatalogProvider` interface but unused by discover.
- Phase F: catalog metadata persisted as `truth_status=PROVIDER_REPORTED`; never fabricate items on upstream failure (503 `catalog_unavailable` / 502 `catalog_not_found`).
- Phase F: dedupe unique key `(mission_id, source_provider, external_item_id)`; `estimated_size_bytes` is BIGINT for multi-GB Sentinel scenes.
- Phase F: Redis cache with short TTL when reachable; in-process TTL fallback for tests / Redis down.
- Phase H: TLE epoch age > **7 days** → `STALE` (`STALE_EPOCH_DAYS` in `tle_cache.py`).
- Phase H: live CelesTrak failure → pinned `simulator/tle_snapshot.json` with `source=pinned-snapshot` and truth `STALE` (dated real TLEs, not authored fiction).
- Phase H: fresh live CelesTrak → `PROVIDER_REPORTED`; contact windows remain `CALCULATED` via `SGP4/Skyfield.find_events` and store `tle_snapshot_id`.
- Phase H: ground-station coordinates → `PROVIDER_REPORTED`; authored latency/downlink/availability → `SIMULATED` in `source_metadata` (never claimed as live capacity).
- Phase H: mission satellite selection is collection/preference-driven over the small Nomos fleet only (no full catalog dump).
- Phase H: ARQ cron `refresh_tle_snapshot` every 6h (prefer live + pinned fallback); `precompute_passes` five minutes later.
- Phase E: customer `objective_type` enum: `analyze_imagery`, `plan_data_delivery`, `compare_processing`, `remote_sensing_workflow`, `other` (legacy demo values still accepted).
- Phase E: AOI max area **500,000 km²**; GeoJSON max **200k** chars; Polygon/bbox only (WGS84).
- Phase E: builder extras (`organization_name`, `use_case`, `max_age_days`, `onboard_processing`, `data_residency`) pack into `customer_systems` JSON (`kind` tags) — no new columns.
- Phase E: mission create `status` limited to `draft` | `exploratory` | `active` (not `example`).
- Phase G: `ProvenancedValue` envelope on catalog candidates, contact windows, and mission infrastructure Out models; internal routing keeps flat `_window_to_dict`.
- Phase G: SIMULATED/ESTIMATED use hatched gold truth badges; STALE/UNAVAILABLE use vermilion; OBSERVED/CALCULATED/PROVIDER use cobalt.
- Phase G: contact-window API method display string is **SGP4 via Skyfield**; source **CelesTrak TLE snapshot {id}**.
- Phase I: planner is a **new path** under `app/planner/`; Job routing (`app/routing/`) is unchanged.
- Phase I: `PLANNER_CONFIG_VERSION = "2026.07.17-1"`; soft weights versioned with that constant.
- Phase I: generation strategy is **append_versions** — each `POST /plans` appends a new MissionPlan version batch and clears prior `recommended` flags (plans retained for audit).
- Phase I: cost estimates are always `UNAVAILABLE` until a real pricing source exists; a mission `max_cost_usd` with no pricing → reject with `cost_unavailable` (never invent AWS/GPU prices).
- Phase I: satellite→ground→cloud is typically `conditional` (`tasking_api_unavailable`); onboard is `rejected` (`onboard_provider_unavailable`).
- Phase I: AOI coverage threshold is **5%** footprint∩AOI / AOI area via PostGIS.
- Phase J: the recommendation is the dominant result-page element; legacy simulated detections remain isolated to the legacy Job demo and are not rendered on mission briefs.
- Phase J: mission geography uses MapLibre with only the mission AOI, the recommended plan's selected scene, and ground stations referenced by generated plan steps. Satellite tracks remain explicitly `UNAVAILABLE` because the mission API does not expose trajectory coordinates.
- Phase J: list responses are hydrated through each plan-detail endpoint so ordered steps and source evidence are available after refresh; communication windows are filtered client-side to IDs referenced by mission plans.
- Phase K: PDF generation is **sync on POST** for MVP (same `generate_pdf_export` used by ARQ worker `generate_mission_pdf_export`); JSON schema_version is **1**.
- Phase K: private share URLs use `/share/{token}` (raw token in path; only hash stored). Legacy `?share_token=` on `/missions/[id]` still works via existing auth deps.
- Phase K: `GET /v1/share/{token}` returns only `mission_id` + link metadata — never unrelated mission payloads.
- Phase K: PDF deps are WeasyPrint + Jinja2; Dockerfile installs pango/cairo/gdk-pixbuf/fonts.
- Phase L: four curated example missions use stable uuid5 IDs under `EXAMPLES_ORGANIZATION_ID`; disclosure metadata lives in `customer_systems` with `kind=example_disclosure`.
- Phase L: `demo-reset` deletes visitor jobs only (`is_example=false`); curated example jobs and all example missions are preserved; seed upserts the four example missions.
- Phase L: `/jobs` + DemoLauncher are labeled **Historical simulation demo**; mock_inference remains for that path only.
- Phase M: execution data contracts live in exactly one module, `app/execution/types.py`; provider id is `local-cpu`.
- Phase M: two tasks only — `crop_geotiff` (rasterio) and `thumbnail` (Pillow, PNG). Checksum was **not** added (kept scope to two fully solid tasks per the phase prompt).
- Phase M: idempotency is a DB unique constraint on `execution_jobs.idempotency_key`; replayed submits return the stored job unchanged (no re-enqueue, no re-run). Clients may omit the key — a deterministic sha256 of (plan, step, task_type, input_ref, params) is derived.
- Phase M: `input_ref` allowlist is `fixture:<name>` (files inside `EXECUTION_FIXTURE_DIR`, no paths) and `artifact:missions/{mission_id}/...` (same-mission object-store keys, enabling crop → thumbnail chaining). Everything else → 422 `execution_invalid`.
- Phase M: resource guards — `EXECUTION_MAX_INPUT_BYTES` (default 100 MB, checked before processing) and `EXECUTION_MAX_SECONDS` timeout (default 120 s, thread-pool future timeout → job failed with a clear error, no hang).
- Phase M: executable step types are `cloud_process` / `edge_process` only, and only steps with `feasibility_status=feasible`.
- Phase M: when Redis is unreachable (local dev/tests) submit falls back to running the real task synchronously in-process — same runner the ARQ worker calls; production enqueues `run_execution_job` on ARQ.
- Phase M: plan steps flip `planned → running → executed/failed` via a new `mission_plan_steps.execution_status` column (+ `executed_at`); measured metrics land in `source_metadata.execution.observed` with `truth_status=OBSERVED`. Estimates on the step are untouched — observed values are additive, never overwrite planning provenance.
- Phase M: outputs upload to the object store only after the task succeeds, so failed jobs cannot leave partial artifacts.

## Phase L — work completed
- Upgraded Phase L agent prompt with concrete file targets, seed/reset rules, and tests
- Seeded four curated public example missions with real/calculated/estimated/simulated/unavailable disclosures
- Replaced `/examples` placeholder with a disclosure-first examples library
- Relabeled legacy job demo UI (list, detail, DemoLauncher, DetectionPanel, SdkResultPreview, DemoBoundary)
- Made `reset_demo_data` preserve curated example jobs; demo-reset workflow documents safety rules
- Updated `SOUL.md` and `capability-truth.md` for the examples / historical-demo boundary

## Phase L — files changed
- `docs/phase-prompts/12-phase-L-isolate-simulations.md`
- `orbital-cortex/apps/api/app/core/missions.py`
- `orbital-cortex/apps/api/app/seed.py`
- `orbital-cortex/apps/api/tests/test_examples_phase_l.py`
- `orbital-cortex/apps/api/tests/test_mission_sessions.py`
- `.github/workflows/demo-reset.yml`
- `orbital-cortex/apps/web/app/examples/page.tsx`
- `orbital-cortex/apps/web/components/examples/ExamplesLibrary.tsx`
- `orbital-cortex/apps/web/app/page.tsx`, `layout.tsx`, `jobs/page.tsx`, `jobs/[id]/page.tsx`
- `orbital-cortex/apps/web/components/jobs/DemoLauncher.tsx`
- `orbital-cortex/apps/web/components/DetectionPanel.tsx`
- `orbital-cortex/apps/web/components/archive/ArchivePrimitives.tsx`
- `orbital-cortex/apps/web/components/platform/SdkResultPreview.tsx`
- `orbital-cortex/apps/web/components/layout/SiteFooter.tsx`
- `SOUL.md`, `orbital-cortex/docs/capability-truth.md`, `docs/BUILD_PROGRESS.md`

## Phase L — tests run
- `pytest tests/test_examples_phase_l.py -q` — 4 passed
- `pytest tests -q` — 82 passed, 1 skipped
- `ruff check` on changed API files — pass
- `npm run lint` — pass
- `npm run build` — pass (`/examples` route present)

## Phase L — investor-readiness refinement (July 2026)
Goal: make the isolated examples read as a product proof (not a static disclosure
catalog) and harden motion for a customer/investor walkthrough.

Work completed:
- Each curated example now seeds one authored reference scene labeled `SIMULATED`
  (`ensure_example_plans` in `seed.py`) so the planner persists a real recommended
  brief. Truth mix is honest: `SIMULATED` scene, `CALCULATED` orbital math,
  `ESTIMATED` transfers, `UNAVAILABLE` cost/tasking. Idempotent — candidate keyed by
  stable uuid5; plans generated only when a mission has none, so reboots/resets never
  duplicate or overwrite curated plans.
- `/examples` rebuilt around a **featured specimen** that fetches the recommended
  plan live (summary, feasibility, estimate chips with truth badges, ordered step
  timeline) plus a truth-label legend and a calm disclosure grid.
- Example mission-detail back-link now returns to `/examples` (was `/missions`).
- Motion hardening: `LiquidCard` gained an `interactive` opt-out (reading grids drop
  pointer-tracking + hover lift); examples reveal uses restrained `FadeIn`/`Stagger`;
  `ScoreBar` and `JobStepper` swapped layout `width` animations for GPU `scaleX`
  (`origin-left`) with `prefers-reduced-motion` handling; `OrbitalScene` now pauses
  its RAF loop when offscreen (IntersectionObserver) or the tab is hidden, and
  reacts to live reduced-motion changes.

Files changed (refinement):
- `orbital-cortex/apps/api/app/core/missions.py` (per-example `collection`, `example_candidate_id`)
- `orbital-cortex/apps/api/app/seed.py` (`ensure_example_plans`)
- `orbital-cortex/apps/api/tests/test_examples_phase_l.py` (recommended-plan + reseed idempotency tests)
- `orbital-cortex/apps/web/components/examples/ExamplesLibrary.tsx` (featured specimen + legend)
- `orbital-cortex/apps/web/components/liquid/LiquidCard.tsx` (`interactive` prop)
- `orbital-cortex/apps/web/app/missions/[id]/page.tsx` (example back-link)
- `orbital-cortex/apps/web/components/ScoreBar.tsx`, `components/jobs/JobStepper.tsx` (GPU transforms + reduced motion)
- `orbital-cortex/apps/web/components/orbital/OrbitalScene.tsx` (visibility/reduced-motion gating)

Tests run (refinement):
- Temporary PostGIS 3.6 cluster (postgresql@17) on port 5433 for local DB validation
- `pytest tests/test_examples_phase_l.py -q` — 6 passed
- `pytest tests/test_planner.py tests/test_mission_sessions.py tests/test_mission_builder.py tests/test_mission_model.py tests/test_api.py -q` — 32 passed
- `npm run lint` — pass; `npm run build` — pass (`/examples` 7.11 kB)

## Phase M — work completed
- `app/execution/` module: `types.py` (single source of data contracts:
  ProviderCapabilities, ExecutionTask, ExecutionEstimate, ExternalJob,
  ExternalJobStatus, ExecutionResult, ObservedMetrics), `refs.py` (input_ref
  allowlist), `tasks.py` (crop_geotiff + thumbnail), `provider.py`
  (`ExecutionProvider` interface + `LocalCpuExecutionProvider`), `runner.py`
  (staged transfer → guarded execution → upload, all phases measured).
- `execution_jobs` table + `mission_plan_steps.execution_status`/`executed_at`
  (alembic `f8a9b0c1d2e3`, upgrade + downgrade).
- ARQ worker function `run_execution_job` registered; `enqueue_execution_job`
  helper in `core/queue.py` with sync fallback when Redis is down.
- API: `POST /v1/missions/{id}/plans/{plan_id}/execute` (owner-only) and
  `GET .../execute/{external_job_id}` (status/result + signed download URL).
- Plan step/detail responses now include `execution_status` + `executed_at`.
- OpenAPI spec + web `api-types.ts` regenerated; web lint/build pass.
- Deps: rasterio + pillow added to `requirements.txt`. Dockerfile unchanged —
  both ship manylinux wheels (rasterio bundles GDAL), verified by running the
  full test suite in the dev venv; no system libraries were needed.

## Phase M UI polish — work completed
- **`ExecutionDemoPanel`** on mission brief section 03: owner-only **Run CPU demo**
  chains `crop_geotiff` → `thumbnail` on `fixture:sample.tif`, polls status,
  shows OBSERVED metrics + signed PNG thumbnail; read-only shares see results
  but not the run button.
- **`MissionTimeline`** pills: Planned / Running / Executed / Failed; executed
  steps show additive **Observed: Xs · Y out** under planner ESTIMATED duration.
- **API client** (`lib/api.ts`): `executePlanStep`, `getExecutionStatus`, step
  fields `execution_status` / `executed_at`; AOI crop bounds helper
  (`lib/missionAoi.ts`).
- **Production fixture**: `ensure_execution_fixtures()` writes
  `{EXECUTION_FIXTURE_DIR}/sample.tif` (~9.5 KB synthetic GeoTIFF) at seed/
  startup — no binary committed; Fly/Docker use default `var/execution_fixtures/`.
- **Truth docs**: `capability-truth.md` “Real CPU demo execution (Phase M)”;
  mission brief section 08 disclosure; `SOUL.md` demo-truth bullet;
  `/examples` read-only note for owners.
- **Mission page wiring**: `canExecute`, `onRefreshPlan`, plan detail reload
  after execution; `InlineNotice` for errors/success.

## Phase M UI polish — files changed
- `orbital-cortex/apps/web/components/missions/ExecutionDemoPanel.tsx` (new)
- `orbital-cortex/apps/web/lib/missionAoi.ts` (new)
- `orbital-cortex/apps/web/lib/api.ts`
- `orbital-cortex/apps/web/components/missions/MissionBrief.tsx`
- `orbital-cortex/apps/web/app/missions/[id]/page.tsx`
- `orbital-cortex/apps/web/components/examples/ExamplesLibrary.tsx`
- `orbital-cortex/apps/api/app/execution/fixtures.py` (new)
- `orbital-cortex/apps/api/app/seed.py`
- `orbital-cortex/apps/api/tests/test_execution_phase_m.py` (fixture seed test)
- `SOUL.md`, `orbital-cortex/docs/capability-truth.md`, `docs/BUILD_PROGRESS.md`

## Phase M UI polish — tests run
- `pytest tests -q` — **93 passed**, 1 skipped
- `npm run lint` — pass; `npm run build` — pass
- **Browser QA** (localhost:3015 prod build → API :8000):
  - Desktop: `/plan` → mission → catalog candidate + generate plan → **Run CPU demo**
    → thumbnail visible, OBSERVED **0.045s · 245 B out**, timeline **Executed** pill
  - Mobile (~390px): timeline + execution panel render without horizontal clip
  - Share link: no run button; owner-only message; **Executed** + **Observed** visible
  - Failure/retry: API `test_failure_corrupt_input_no_partial_artifact` verifies
    human-readable errors; UI shows vermilion error box + **Run CPU demo** retry
    (`ExecutionDemoPanel` failed state)
- **Note:** CPU demo panel requires a **feasible** `cloud_process` / `edge_process`
  step — run catalog discovery (or seed candidates) before generating plans.

## Phase M — skipped / deferred
- `checksum` task (prompt allowed it only after the first two were solid;
  scope kept to the two fully tested tasks).
- Planetary Computer SAS input_refs (allowlist currently fixture + same-
  mission artifacts; SAS signing remains deferred as noted since Phase F).
- Pre-existing lint/type debt not touched: 3 ruff E501 in
  `app/exports/presentation.py` / `tests/test_pdf_presentation.py` and mypy
  errors in `services/contact_windows.py`, `planner/engine.py:382`,
  `routes/missions.py` trailing `_ =` lines — all present before Phase M.

## Phase M — files changed
- `orbital-cortex/apps/api/app/execution/{__init__,types,refs,tasks,provider,runner}.py` (new)
- `orbital-cortex/apps/api/migrations/versions/f8a9b0c1d2e3_execution_jobs.py` (new)
- `orbital-cortex/apps/api/tests/test_execution_phase_m.py` (new, 8 tests)
- `orbital-cortex/apps/api/app/db/mission_orm.py` (ExecutionJob, step columns)
- `orbital-cortex/apps/api/app/core/{config,queue}.py`
- `orbital-cortex/apps/api/app/workers/executor.py`
- `orbital-cortex/apps/api/app/routes/missions.py` (execute endpoints)
- `orbital-cortex/apps/api/app/models/mission.py`, `app/planner/engine.py` (step Out fields)
- `orbital-cortex/apps/api/requirements.txt`
- `orbital-cortex/openapi.json`, `orbital-cortex/apps/web/lib/generated/api-types.ts` (regenerated)

## Phase M — tests run
- `pytest tests/test_execution_phase_m.py -q` — 8 passed (end-to-end crop with
  OBSERVED metrics + on-disk artifact, idempotent submit enqueues exactly one
  ARQ job, corrupt-input failure with no orphaned artifact, oversized-input
  guard, chained crop → thumbnail with valid openable PNG, input_ref
  allowlist rejections, non-executable step rejection, owner-only auth)
- `pytest tests -q` — 92 passed, 1 skipped (optional WeasyPrint smoke)
- `ruff check` on all Phase M files — pass; `mypy app/execution` — pass
- DB audit queries: `execution_jobs.observed_metrics` nonzero and matching
  `ls -la` byte sizes; `mission_plan_steps.execution_status = 'executed'`
  with `source_metadata.execution.truth_status = 'OBSERVED'`; failed jobs
  carry human-readable errors with `output_key IS NULL` and zero files on disk
- `npm run lint` + `npm run build` (web) — pass after typegen

## Unresolved issues / risks
- Cross-origin cookie auth in production still requires `SESSION_COOKIE_DOMAIN=.nomosorbital.com` + CORS credentials (configured) on Fly; Vercel must call `api.nomosorbital.com` with credentials or use a same-origin proxy.
- Local mission APIs rely on `/api/oc` rewrite; job demo still uses `NEXT_PUBLIC_API_BASE_URL` without cookies.
- `GET /v1/jobs` now returns curated `is_example` jobs only; non-example rows remain in DB and reachable by ID (not deleted). Ops analytics still TBD (Phase O).
- Live Planetary Computer search depends on upstream availability; SAS signing for asset download is deferred to Phase M.
- Discover defaults to last 30 days when mission has no start/end times.
- Live TLE refresh depends on CelesTrak availability; worker cron falls back to pinned snapshot with `STALE`.
- mapbox-gl-draw is Mapbox-licensed UI chrome on MapLibre; acceptable for planner MVP; terra-draw remains an option if we need a pure MapLibre draw stack later.
- Phase I does not execute tasking/reservation; satellite paths remain conditional.
- Mission satellite tracks cannot be drawn until an API exposes trajectory coordinates; the result page labels this `UNAVAILABLE`.
- Contact-window retrieval still uses the existing public pass-cache endpoint and filters the response to plan-referenced IDs in the browser; a mission-scoped endpoint would be cleaner in a later API phase.
- Host CI images without WeasyPrint system libs skip the optional PDF integration test; Docker image must include those libs (updated).
- Revoke UI on the mission page tracks the latest share link created in the current browser session (raw token is only returned once).
- Curated example missions are seeded with disclosure metadata but without pre-generated planner plans; opening an example mission may show the generate-plan empty state until a visitor generates plans. Cards on `/examples` carry the full truth disclosures.
- A pre-Phase-L thin example mission row (random UUID) may still exist in long-lived DBs alongside the four stable uuid5 examples; seed does not delete it.

## Architecture decisions
- Sync catalog provider API (matches sync FastAPI routes); pystac-client for PC STAC.
- Application-level dedupe before insert + DB unique constraint for race safety.
- Optional Redis search cache (`nomos:catalog:*`) with memory fallback.
- Orbital snapshot ids are unique per successful live refresh (`celestrak-YYYY-MM-DDTHHMMSSZ`); prior contact-window rows keep their `tle_snapshot_id` for audit.
- Prefer mission-facing infra in `InfrastructureResource` while keeping legacy `ground_stations` / `satellites` for the Job demo path.
- Guided builder uses a single React reducer (no URL persistence); AOI area checked with spherical excess on both FE and BE.
- Provenance envelope is API/UI-only for Out models; DB rows and internal routing helpers remain flat scalars.
- Planner meta (pattern, hashes, scores, estimates, explanation) stored inside `MissionPlan.assumptions` JSON under `kind=planner_meta` so Phase B schema stays unchanged.
- No LLM in the feasibility path; `explain.py` emits structured fields only.
- The Phase J page renders a complete eight-section brief for feasible, conditional, and fully rejected plan sets. Missions without plans get an honest `Generate plan` empty state.
- Heavy MapLibre code is dynamically loaded only when the geographic section renders.
- PDF MVP renders synchronously on the request path; ARQ worker registers the same generator for larger/async use.
- Share pages resolve token → mission_id first, then load the mission with the share header — never enumerate other missions.
- Phase L example disclosures reuse `customer_systems` JSON (`kind=example_disclosure`) instead of a new column.
- Phase L keeps `mock_inference.py` for `/jobs` only; customer mission briefs remain free of fabricated detections.

## Next phase
Phase N — execution provider registry.

**Agent prompt to copy-paste:** [`docs/phase-prompts/14-phase-N-provider-registry.md`](phase-prompts/14-phase-N-provider-registry.md)
**Index of all remaining prompts:** [`docs/phase-prompts/README.md`](phase-prompts/README.md)
