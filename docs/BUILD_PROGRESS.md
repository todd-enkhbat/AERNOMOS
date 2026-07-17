# Nomos Build Progress

Current phase: I (next)

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)
- Phase C: Anonymous private sessions + share-link access (`feat: add private anonymous mission sessions and share links`)
- Phase F: Real STAC catalog discovery via Microsoft Planetary Computer
- Phase H: Fresh orbital data provenance and mission-specific infrastructure
- Phase E: Guided customer-facing mission builder at `/plan`

## In progress
None — Phase E complete. Next is Phase I (planning engine).

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

## Phase E — work completed
- Five-step guided builder at `/plan` (objective → area/time → constraints → context → review)
- MapLibre + mapbox-gl-draw polygon AOI; bbox fields; strict Polygon GeoJSON upload
- Client zod + reducer state surviving step navigation; server Pydantic + `mission_geo` mirroring rules
- Nav/header/footer CTAs to `/plan`; `/missions` points to builder instead of quick-create
- Customer language: “Build a mission plan” (no “compute job” copy on this flow)
- Backend tests for invalid geo / oversized AOI / blank title / valid create / cross-session isolation

## Files changed
- API: `app/core/mission_geo.py` (new), `app/models/mission.py`, `app/core/missions.py`, `app/main.py` (clearer 422 messages)
- API tests: `tests/test_mission_builder.py`
- Web: `app/plan/page.tsx`, `components/plan/*`, `lib/mission-builder.ts`
- Web: `app/missions/page.tsx`, `components/layout/SiteHeader.tsx`, `SiteFooter.tsx`, `LiquidNavPill.tsx`, `lib/api.ts`, `globals.css`
- Deps: `zod`, `@mapbox/mapbox-gl-draw`
- Generated: `openapi.json`, `lib/generated/api-types.ts`
- `docs/BUILD_PROGRESS.md`

## Tests run
- `ruff check app tests scripts` — pass
- `mypy app` — pass
- `pytest tests -q` — 55 passed, 1 skipped
- `npm run lint` / `npm run build` — pass

## Frontend manual checklist (no vitest/playwright harness)
- [ ] Open `/plan` at desktop and mobile; demo banner remains visible
- [ ] Complete all five steps; go back — fields retained
- [ ] Draw polygon; apply bbox coordinates; upload small Polygon GeoJSON
- [ ] Reject oversized AOI / non-Polygon upload with clear error
- [ ] Submit → lands on `/missions/[id]` owned by session
- [ ] Keyboard focus order through steps and primary controls
- [ ] No “compute job” wording on `/plan` or missions CTA

## Unresolved issues / risks
- Cross-origin cookie auth in production still requires `SESSION_COOKIE_DOMAIN=.nomosorbital.com` + CORS credentials (configured) on Fly; Vercel must call `api.nomosorbital.com` with credentials or use a same-origin proxy.
- Local mission APIs rely on `/api/oc` rewrite; job demo still uses `NEXT_PUBLIC_API_BASE_URL` without cookies.
- `GET /v1/jobs` now returns curated `is_example` jobs only; non-example rows remain in DB and reachable by ID (not deleted). Ops analytics still TBD (Phase O).
- Live Planetary Computer search depends on upstream availability; SAS signing for asset download is deferred to Phase M.
- Discover defaults to last 30 days when mission has no start/end times.
- Live TLE refresh depends on CelesTrak availability; worker cron falls back to pinned snapshot with `STALE`.
- Mission infrastructure UI (truth chips) is Phase G; planning engine that consumes selection is Phase I.
- mapbox-gl-draw is Mapbox-licensed UI chrome on MapLibre; acceptable for planner MVP; terra-draw remains an option if we need a pure MapLibre draw stack later.

## Architecture decisions
- Sync catalog provider API (matches sync FastAPI routes); pystac-client for PC STAC.
- Application-level dedupe before insert + DB unique constraint for race safety.
- Optional Redis search cache (`nomos:catalog:*`) with memory fallback.
- Orbital snapshot ids are unique per successful live refresh (`celestrak-YYYY-MM-DDTHHMMSSZ`); prior contact-window rows keep their `tle_snapshot_id` for audit.
- Prefer mission-facing infra in `InfrastructureResource` while keeping legacy `ground_stations` / `satellites` for the Job demo path.
- Guided builder uses a single React reducer (no URL persistence); AOI area checked with spherical excess on both FE and BE.

## Next phase
Phase I — planning engine.

**Agent prompt to copy-paste:** [`docs/phase-prompts/08-phase-I-planning-engine.md`](phase-prompts/08-phase-I-planning-engine.md)  
**Index of all remaining prompts:** [`docs/phase-prompts/README.md`](phase-prompts/README.md)

Note: Phase G (truth-status UI) remains available in the prompt index and can run before or after I as needed; dependency-corrected order after E is **I → J → D**.
