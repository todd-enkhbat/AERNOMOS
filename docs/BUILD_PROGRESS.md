# Nomos Build Progress

Current phase: C

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)

## In progress
Phase C: Anonymous private sessions + share-link access

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

## Phase B — work completed
- Shared `TruthStatus` enum: OBSERVED, CALCULATED, PROVIDER_REPORTED, ESTIMATED, SIMULATED, STALE, UNAVAILABLE
- ORM entities: AnonymousSession, Mission, MissionDataCandidate, InfrastructureResource, MissionPlan, MissionPlanStep, SourceEvidence, ShareLink
- Alembic revision `f2a3b4c5d6e7` (revises `e1f2a3b4c5d6`): additive tables + indexes (ownership, created_at, GiST geometries, catalog IDs, token hashes, provider+type)
- Tests: migration up/down, session/org ownership isolation, share-link uniqueness/expiry/revoke, legacy jobs still writable

## Files changed
- `orbital-cortex/apps/api/app/db/truth.py` (new)
- `orbital-cortex/apps/api/app/db/mission_orm.py` (new)
- `orbital-cortex/apps/api/app/db/orm.py` (registers mission models)
- `orbital-cortex/apps/api/migrations/versions/f2a3b4c5d6e7_mission_planning_data_model.py` (new)
- `orbital-cortex/apps/api/tests/test_mission_model.py` (new)
- `docs/BUILD_PROGRESS.md`

## Tests run
- `ruff check app tests scripts` — pass
- `mypy app` — pass
- `pytest tests -q` — 26 passed (includes migration + ownership + share-link + full legacy suite)

## Unresolved issues / risks
- No API yet for sessions/missions (Phase C); model isolation is DB-level only.
- Share tokens and session tokens are hash columns only; minting/cookie middleware is Phase C.
- `organization_id` has no organizations table yet.
- Local validation used Homebrew PostgreSQL 17 + PostGIS on port 5433 (CI uses `postgis/postgis:16-3.4`).

## Architecture decisions
- UUID primary keys for all mission-planning tables (non-enumerable).
- PostGIS `geometry(Geometry, 4326)` for mission AOI, candidate footprints, and optional resource locations; named GiST indexes with `spatial_index=False` on columns to avoid duplicate auto-indexes.
- Truth status stored as non-native VARCHAR enum (easier to extend than PG ENUM).
- Do not modify Job tables; demo compatibility verified by write/delete on `jobs` after migration.

## Next phase
Phase C — anonymous private sessions, cookie + hash storage, mission ownership middleware, share-token validation.
