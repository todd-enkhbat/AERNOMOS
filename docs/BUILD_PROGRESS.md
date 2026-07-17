# Nomos Build Progress

Current phase: H (next)

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)
- Phase C: Anonymous private sessions + share-link access (`feat: add private anonymous mission sessions and share links`)
- Phase F: Real STAC catalog discovery via Microsoft Planetary Computer

## In progress
None — Phase F complete. Next is Phase H (orbital provenance / infrastructure resources).

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

## Phase F — work completed
- `DataCatalogProvider` abstraction + Planetary Computer implementation via `pystac-client`
- Earth Search stub adapter (not enabled)
- `POST /v1/missions/{id}/discover` (owner) and `GET /v1/missions/{id}/candidates` (owner/share/example read)
- Persist `MissionDataCandidate` with footprint, assets, source URL, retrieval timestamp, truth status
- Mission detail UI: “Discover catalog data” control + candidate list with truth labels
- Mocked unit/API tests + env-gated live STAC integration test (`RUN_LIVE_STAC=1`)
- Migration: unique dedupe constraint + BIGINT sizes
- OpenAPI + TS types regenerated

## Files changed
- API catalog: `app/catalog/{__init__,types,base,errors,cache,planetary_computer,earth_search,service}.py`
- API routes/models: `app/routes/missions.py`, `app/models/mission.py`, `app/db/mission_orm.py`
- Migration: `c5d6e7f8a9b0_mission_candidate_unique.py`
- Deps: `requirements.txt` (`pystac-client`)
- Tests: `tests/test_catalog.py`, `tests/test_catalog_integration.py`, `tests/fixtures/stac_ny_harbor_sentinel1.json`, `tests/conftest.py`
- Web: `app/missions/[id]/page.tsx`, `lib/api.ts`
- Generated: `openapi.json`, `lib/generated/api-types.ts`
- `docs/BUILD_PROGRESS.md`

## Tests run
- `ruff check app tests scripts` — pass
- `mypy app` — pass
- `pytest tests -q` — 39 passed, 1 skipped (live STAC)
- `npm run lint` / `npm run build` — pass

## Unresolved issues / risks
- Cross-origin cookie auth in production still requires `SESSION_COOKIE_DOMAIN=.nomosorbital.com` + CORS credentials (configured) on Fly; Vercel must call `api.nomosorbital.com` with credentials or use a same-origin proxy.
- Local mission APIs rely on `/api/oc` rewrite; job demo still uses `NEXT_PUBLIC_API_BASE_URL` without cookies.
- Guided mission builder UI is still minimal (title + default AOI); Phase E expands the form.
- `GET /v1/jobs` now returns curated `is_example` jobs only; non-example rows remain in DB and reachable by ID (not deleted). Ops analytics still TBD (Phase O).
- Live Planetary Computer search depends on upstream availability; SAS signing for asset download is deferred to Phase M.
- Discover defaults to last 30 days when mission has no start/end times.

## Architecture decisions
- Sync catalog provider API (matches sync FastAPI routes); pystac-client for PC STAC.
- Application-level dedupe before insert + DB unique constraint for race safety.
- Optional Redis search cache (`nomos:catalog:*`) with memory fallback.

## Next phase
Phase H — orbital / infrastructure provenance (populate `InfrastructureResource` with labeled sources).

**Agent prompt to copy-paste:** [`docs/phase-prompts/05-phase-H-orbital-provenance.md`](phase-prompts/05-phase-H-orbital-provenance.md)  
**Index of all remaining prompts:** [`docs/phase-prompts/README.md`](phase-prompts/README.md)
