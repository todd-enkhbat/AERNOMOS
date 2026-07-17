# Nomos Build Progress

Current phase: J (next)

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)
- Phase C: Anonymous private sessions + share-link access (`feat: add private anonymous mission sessions and share links`)
- Phase F: Real STAC catalog discovery via Microsoft Planetary Computer
- Phase H: Fresh orbital data provenance and mission-specific infrastructure
- Phase E: Guided customer-facing mission builder at `/plan`
- Phase G: Source provenance and truth-status labeling (API envelope + truth UI components)
- Phase I: Source-backed mission feasibility and planning engine

## In progress
None — Phase I complete. Next is Phase J (mission result experience).

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

## Phase I — work completed
- Planner package: generate → estimate → hard-constrain → soft-rank → explain → persist
- Patterns: existing imagery→cloud, imagery→edge, satellite→ground→cloud, onboard
- APIs: `POST/GET /v1/missions/{id}/plans`, `GET .../plans/{plan_id}` (owner generate; owner/share/example read)
- Persists `MissionPlan`, ordered `MissionPlanStep`, and `SourceEvidence` (catalog + TLE + estimate methods)
- Deterministic plan/input hashes for same mission inputs + source snapshot + config version
- Minimal `/missions/[id]` Generate plans trigger + recommendation summary

## Files changed
- API: `app/planner/` (`__init__.py`, `types.py`, `hash.py`, `constraints.py`, `preferences.py`, `patterns.py`, `estimates.py`, `explain.py`, `engine.py`)
- API: `app/routes/missions.py`, `app/models/mission.py`
- API tests: `tests/test_planner.py` (new)
- Web: `app/missions/[id]/page.tsx`, `lib/api.ts`
- Generated: `orbital-cortex/openapi.json`, `lib/generated/api-types.ts`
- `docs/BUILD_PROGRESS.md`

## Tests run
- `pytest tests/test_planner.py -q` — 8 passed
- `pytest tests -q` — 69 passed, 1 skipped
- `ruff check app/planner app/routes/missions.py …` — pass
- `npm run generate:api-types` — pass
- `npm run lint` — pass
- `npm run build` — pass

## Unresolved issues / risks
- Cross-origin cookie auth in production still requires `SESSION_COOKIE_DOMAIN=.nomosorbital.com` + CORS credentials (configured) on Fly; Vercel must call `api.nomosorbital.com` with credentials or use a same-origin proxy.
- Local mission APIs rely on `/api/oc` rewrite; job demo still uses `NEXT_PUBLIC_API_BASE_URL` without cookies.
- `GET /v1/jobs` now returns curated `is_example` jobs only; non-example rows remain in DB and reachable by ID (not deleted). Ops analytics still TBD (Phase O).
- Live Planetary Computer search depends on upstream availability; SAS signing for asset download is deferred to Phase M.
- Discover defaults to last 30 days when mission has no start/end times.
- Live TLE refresh depends on CelesTrak availability; worker cron falls back to pinned snapshot with `STALE`.
- mapbox-gl-draw is Mapbox-licensed UI chrome on MapLibre; acceptable for planner MVP; terra-draw remains an option if we need a pure MapLibre draw stack later.
- Phase I does not execute tasking/reservation; satellite paths remain conditional.
- Full mission result UX (executive recommendation layout, comparison tables) is Phase J.

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

## Next phase
Phase J — mission result experience.

**Agent prompt to copy-paste:** [`docs/phase-prompts/09-phase-J-mission-result.md`](phase-prompts/09-phase-J-mission-result.md)  
**Index of all remaining prompts:** [`docs/phase-prompts/README.md`](phase-prompts/README.md)
