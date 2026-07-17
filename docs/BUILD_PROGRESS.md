# Nomos Build Progress

Current phase: G (next)

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)
- Phase C: Anonymous private sessions + share-link access (`feat: add private anonymous mission sessions and share links`)
- Phase F: Real STAC catalog discovery via Microsoft Planetary Computer
- Phase H: Fresh orbital data provenance and mission-specific infrastructure

## In progress
None — Phase H complete. Next is Phase G (truth-status UI system).

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

## Phase H — work completed
- Extended `tle_cache` with snapshot versioning, staleness classification, pinned fallback, and `get_orbital_snapshot_metadata()`
- Contact windows persist `tle_snapshot_id`; API responses include snapshot provenance + `CALCULATED` method label
- Seed writes `InfrastructureResource` for fleet sats + GS; legacy `ground_stations` gain `access_level` + `source_metadata`
- `GET /v1/missions/{id}/infrastructure` returns mission-relevant sats, public GS, and orbital snapshot metadata
- SourceEvidence helpers for orbital snapshots and contact windows (for Phase I/J)
- ARQ `refresh_tle_snapshot` cron + migration for provenance columns
- Unit/API tests for staleness, fallback, reproducibility, and mission-specific selection

## Files changed
- API: `app/services/tle_cache.py`, `contact_windows.py`, `mission_infrastructure.py` (new)
- API: `app/workers/passes.py`, `app/workers/executor.py`, `app/seed.py`
- API: `app/db/orm.py`, `app/db/truth.py` (`AccessLevel`)
- API: `app/models/node.py`, `app/models/mission.py`, `app/routes/missions.py`, `app/core/node_registry.py`
- Migration: `d6e7f8a9b0c1_orbital_provenance.py`
- Tests: `tests/test_orbital_provenance.py`
- Generated: `openapi.json`, `lib/generated/api-types.ts`
- `docs/BUILD_PROGRESS.md`

## Tests run
- `ruff check app tests scripts` — pass
- `mypy app` — pass
- `pytest tests -q` — 48 passed, 1 skipped (live STAC)
- `npm run lint` / `npm run build` — pass

## Unresolved issues / risks
- Cross-origin cookie auth in production still requires `SESSION_COOKIE_DOMAIN=.nomosorbital.com` + CORS credentials (configured) on Fly; Vercel must call `api.nomosorbital.com` with credentials or use a same-origin proxy.
- Local mission APIs rely on `/api/oc` rewrite; job demo still uses `NEXT_PUBLIC_API_BASE_URL` without cookies.
- Guided mission builder UI is still minimal (title + default AOI); Phase E expands the form.
- `GET /v1/jobs` now returns curated `is_example` jobs only; non-example rows remain in DB and reachable by ID (not deleted). Ops analytics still TBD (Phase O).
- Live Planetary Computer search depends on upstream availability; SAS signing for asset download is deferred to Phase M.
- Discover defaults to last 30 days when mission has no start/end times.
- Live TLE refresh depends on CelesTrak availability; worker cron falls back to pinned snapshot with `STALE`.
- Mission infrastructure UI (truth chips) is Phase G; planning engine that consumes selection is Phase I.

## Architecture decisions
- Sync catalog provider API (matches sync FastAPI routes); pystac-client for PC STAC.
- Application-level dedupe before insert + DB unique constraint for race safety.
- Optional Redis search cache (`nomos:catalog:*`) with memory fallback.
- Orbital snapshot ids are unique per successful live refresh (`celestrak-YYYY-MM-DDTHHMMSSZ`); prior contact-window rows keep their `tle_snapshot_id` for audit.
- Prefer mission-facing infra in `InfrastructureResource` while keeping legacy `ground_stations` / `satellites` for the Job demo path.

## Next phase
Phase G — truth-status UI system.

**Agent prompt to copy-paste:** [`docs/phase-prompts/06-phase-G-truth-ui.md`](phase-prompts/06-phase-G-truth-ui.md)  
**Index of all remaining prompts:** [`docs/phase-prompts/README.md`](phase-prompts/README.md)
