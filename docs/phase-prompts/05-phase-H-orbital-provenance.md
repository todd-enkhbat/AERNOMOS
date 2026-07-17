# Phase H — Fresh orbital data provenance and mission-specific infrastructure

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- Phases A–C complete
- Phase F complete (STAC candidates exist) — if F is incomplete, stop and tell the user

## Context — inspect first

Read and reuse (do not rewrite from scratch):

- `orbital-cortex/apps/api/app/services/tle_cache.py` — fleet NORAD IDs, pinned snapshot vs live CelesTrak
- `orbital-cortex/apps/api/app/services/contact_windows.py` — Skyfield/SGP4
- `orbital-cortex/apps/api/app/workers/passes.py` — precompute cron
- `orbital-cortex/simulator/tle_snapshot.json` — pinned fallback
- `orbital-cortex/simulator/ground_stations.json` — public GS coords + authored ops params
- `Satellite.snapshot_id`, `RoutingDecision.tle_snapshot_id` already exist on legacy job path
- Mission models: `InfrastructureResource`, `SourceEvidence` in `app/db/mission_orm.py`
- Truth statuses in `app/db/truth.py`

## Product goal

Make orbital and ground-station inputs **auditable**: every contact-window / TLE-derived value used by missions must record which snapshot produced it, detect staleness, fall back to the pinned snapshot with `STALE` or `SIMULATED` labels, and only surface satellites relevant to the mission (not the whole catalog).

## Required work

### 1. TLE refresh + snapshot versioning

Extend `tle_cache.py` (and seed/worker as needed):

1. Scheduled refresh via ARQ cron (extend existing passes worker or add `refresh_tle_snapshot` cron — e.g. every 6–12h)
2. Persist per-satellite (or snapshot-level):
   - `source` (e.g. `celestrak-gp` vs `pinned-snapshot`)
   - `tle_epoch`
   - `snapshot_id` (new id each successful live refresh; keep previous)
   - `retrieved_at` / `data_freshness_at` if columns needed — **add Alembic migration** if schema gaps exist
3. Staleness rule (document the threshold, e.g. epoch age > 7 days → `STALE`):
   - When live fetch fails → use pinned `simulator/tle_snapshot.json`
   - Mark truth status `STALE` if using aged live data, `SIMULATED` or `STALE` for pinned fallback (prefer `STALE` for pinned dated snapshot; use `SIMULATED` only if data is demo-authored fiction)
4. Expose an internal helper: `get_orbital_snapshot_metadata() -> {snapshot_id, source, epochs, truth_status, retrieved_at}`

### 2. Contact windows tied to snapshot

- When precomputing windows, store which `snapshot_id` / TLE epoch set produced them (migration on `contact_windows` if needed — e.g. `tle_snapshot_id` column)
- API responses for windows used by missions must include snapshot provenance
- Calculations remain Skyfield/SGP4 — truth_status `CALCULATED` with method `SGP4` / Skyfield `find_events`

### 3. Ground stations access-level + source metadata

For seeded ground stations (and/or `InfrastructureResource` rows of type `ground_station`):

- Add fields if missing (migration): `source_metadata` JSON, `access_level` enum/string:
  - `public_information`
  - `sandbox_available`
  - `partner_required`
  - `private`
  - `simulated`
- Coordinates from public registries → `OBSERVED` / `PROVIDER_REPORTED`
- Authored latency/downlink/availability → `SIMULATED` or `ESTIMATED` with explanation in metadata — **do not pretend they are live provider capacity**

Prefer writing mission-facing infra into `InfrastructureResource` while keeping legacy `ground_stations` table working for the Job demo.

### 4. Mission-specific satellite selection

Do **not** render or load all ~30k tracked objects (we only have a small fleet today — keep it that way).

Add helper used by later planner/UI:

- Given a mission + its `MissionDataCandidate` collections, select relevant satellites (e.g. Sentinel-1A/C for S1 candidates; Capella/ICEYE only if mission asks or collections match)
- Endpoint optional: `GET /v1/missions/{id}/infrastructure` returning relevant sats + GS + snapshot metadata with truth statuses

### 5. SourceEvidence records

When refreshing TLEs or computing windows for a mission context, write `SourceEvidence` rows (or ensure helpers exist to write them) so Phase I/J can attach evidence without inventing sources.

### 6. Tests

- Stale detection unit tests (freeze time / fake epoch)
- Fallback to pinned snapshot on live failure; status labeled correctly
- Contact window reproducibility for same snapshot + inputs
- Mission-specific selection excludes unrelated sats
- Existing `tests/test_contact_windows.py` still pass

### 7. Progress + codegen

Update `docs/BUILD_PROGRESS.md`. Regenerate OpenAPI/types if APIs changed.

## Validation

```bash
cd orbital-cortex/apps/api && ruff check app tests scripts && mypy app && pytest tests -q
cd ../web && npm run lint && npm run build
```

## Acceptance criteria

- [ ] Mission plans / APIs can record which orbital-data snapshot was used
- [ ] Contact-window calculations remain reproducible for a snapshot
- [ ] Stale / fallback data clearly labeled with truth status
- [ ] Ground stations have access_level + source metadata
- [ ] Satellite selection is mission-specific (no global dump)
- [ ] Tests cover staleness + fallback
- [ ] Legacy Job contact-window path still works

## Non-goals

- Do not build truth UI components (Phase G)
- Do not build the planning engine (Phase I)
- Do not change homepage copy

## Commit message

```
feat: add fresh orbital data provenance and mission-specific infrastructure
```

## Stop

Stop after this phase. Next is Phase G.
