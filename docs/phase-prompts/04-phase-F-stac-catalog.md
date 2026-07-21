# Phase F — Real STAC satellite catalog discovery

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Context (already done — do not rebuild)

- Repo: AERNOMOS / product Nomos Orbital / stack in `orbital-cortex/`
- Phase A audit: `orbital-cortex/docs/current-system-audit.md`
- Phase B models: `orbital-cortex/apps/api/app/db/mission_orm.py` includes `MissionDataCandidate` with `truth_status`, footprint geometry, `source_provider`, `external_item_id`, unique constraints intended for dedupe
- Phase C: private missions via session cookie; auth deps in `app/deps/auth.py`; routes in `app/routes/missions.py`; list/create/get missions work
- Truth enum: `app/db/truth.py` (`OBSERVED`, `CALCULATED`, `PROVIDER_REPORTED`, `ESTIMATED`, `SIMULATED`, `STALE`, `UNAVAILABLE`)
- Progress tracker: `docs/BUILD_PROGRESS.md` (mark this phase in progress, then complete)
- Master plan: `docs/NOMOS_BUILD_PLAN.md`

## Product goal for this phase

Wire **real public STAC search** so a private mission can discover actual Sentinel scenes over an AOI/date range, persist them as `MissionDataCandidate` rows with provenance, and never invent catalog items.

## Concrete tech choices (do not re-litigate)

- Primary provider: **Microsoft Planetary Computer** STAC API via `pystac-client` (keyless search; SAS for assets if needed later)
- Collections to support first: **Sentinel-1 GRD** (`sentinel-1-grd` or current PC collection id — verify against live STAC), optionally **Sentinel-2 L2A**
- Second provider stub/adapter allowed: Earth Search (Element84) behind the **same** interface — implement PC fully; Earth Search can be a thin second class or placeholder registered but unused
- Cache: Redis if available (same `REDIS_URL` as ARQ); fall back to short in-process TTL cache when Redis unreachable in tests
- Never fabricate STAC items

## Required work

### 1. Provider abstraction

Create something like:

```
orbital-cortex/apps/api/app/catalog/
  __init__.py
  types.py          # CatalogSearchQuery, CatalogItem, CatalogAsset (Pydantic or dataclasses)
  base.py           # DataCatalogProvider Protocol / ABC
  planetary_computer.py
  errors.py         # CatalogUnavailableError, CatalogRateLimitedError, CatalogNotFoundError
  cache.py          # optional Redis/memory cache helpers
  service.py        # search + persist into MissionDataCandidate
```

Interface (sync or async is fine if consistent with FastAPI style in this repo — prefer **sync** if most routes are sync, or async with `httpx`/`pystac-client` patterns that fit existing code):

```python
class DataCatalogProvider:
    def search(self, query: CatalogSearchQuery) -> list[CatalogItem]: ...
    def get_item(self, collection: str, external_item_id: str) -> CatalogItem: ...
    def get_assets(self, collection: str, external_item_id: str) -> list[CatalogAsset]: ...
```

`CatalogSearchQuery` must support:

- AOI as GeoJSON polygon or bbox
- `datetime` start/end (ISO)
- collections list (default Sentinel-1 GRD)
- `limit` (cap reasonably, e.g. 20–50)

`CatalogItem` must map cleanly into `MissionDataCandidate`:

- `source_provider` = `"microsoft-planetary-computer"` (stable string)
- `collection`, `external_item_id`
- `acquisition_time`
- footprint → PostGIS geometry
- `asset_metadata` JSON (hrefs, media types, roles, sizes if present)
- `estimated_size_bytes` nullable
- `source_url` (STAC item self href or PC browser URL)
- `source_timestamp` = retrieval time (UTC now when fetched)
- `truth_status` = `PROVIDER_REPORTED` for catalog metadata from STAC; `ESTIMATED` only for size if you compute/estimate it

### 2. Persistence + dedupe

In `app/core/` (e.g. `app/core/catalog.py` or `app/catalog/service.py`):

- Given `mission_id` + search results, upsert `MissionDataCandidate`
- Unique key: `(mission_id, source_provider, external_item_id)` **or** global `(source_provider, external_item_id)` per mission — **do not insert duplicates** for the same mission+item
- Check existing UniqueConstraint / Index on `MissionDataCandidate` in `mission_orm.py`; add a migration if the unique constraint is missing
- Store footprints with GeoAlchemy2 / `ST_GeomFromGeoJSON` consistent with how Mission AOI is written today

### 3. API endpoints

Add under missions router (or `app/routes/catalog.py` included from `main.py`), **session-owned**:

1. `POST /v1/missions/{mission_id}/discover`
   - Body: optional overrides for date range, collections, limit (default to mission’s AOI + start/end if set)
   - Auth: owner session required (use `get_owned_mission` / `require_anonymous_session`)
   - Behavior: call provider → persist candidates → return list of candidates with truth_status
   - On upstream failure: `502` or `503` with typed error code like `catalog_unavailable` — **do not** invent empty “successful” fake items

2. Optional helper for the builder later: `POST /v1/catalog/search` (session required) that searches without persisting — only if cheap; otherwise discover alone is enough for this phase

3. `GET /v1/missions/{mission_id}/candidates` — list persisted candidates for a mission (owner or valid share/example read access via existing `get_mission_for_read`)

Response fields for each candidate (customer-facing):

- collection / satellite family
- acquisition date
- footprint GeoJSON
- available assets (media types / roles)
- estimated size if known
- source provider + URL
- source_timestamp / freshness
- truth_status

### 4. Dependencies

- Add `pystac-client` (and any thin helpers) to `orbital-cortex/apps/api/requirements.txt`
- Rebuild Docker image path must still work; keep versions compatible with Python 3.12

### 5. Frontend (minimal but real)

Do **not** build the full `/plan` wizard (that is Phase E). For this phase:

- On `/missions/[id]` (or a small section there), add a **“Discover catalog data”** control that:
  - Calls discover
  - Lists returned candidates with truth badge text (plain label is fine; fancy UI is Phase G)
  - Shows clear error if provider is down

If `/missions/[id]` is too thin today, a simple panel is fine — keep styling consistent with Nomos Record UI (dark glass), no purple-gradient AI look.

### 6. Tests

Create `tests/test_catalog.py` (and/or `tests/test_catalog_integration.py`):

**Unit / mocked (required):**

- Mock Planetary Computer responses (fixture JSON STAC FeatureCollection)
- Search maps to `CatalogItem` correctly
- Persist + second discover does not duplicate rows
- Upstream timeout/HTTP error → API returns typed error, no fake rows
- Unauthorized session cannot discover another session’s mission

**Live integration (optional, env-gated):**

- Skip unless `RUN_LIVE_STAC=1`
- Search New York Harbor bbox roughly `[-74.3, 40.3, -73.5, 41.0]` over a recent date window for Sentinel-1
- Assert ≥1 real item id returned

### 7. Codegen + docs

After OpenAPI changes:

```bash
cd orbital-cortex/apps/api && python -m scripts.export_openapi ../../openapi.json
cd ../web && npm run generate:api-types
```

Update `docs/BUILD_PROGRESS.md` with files changed, tests run, decisions, next phase = H.

Briefly note the provider in a short comment or stub in `orbital-cortex/docs/` only if needed — full `data-sources.md` is Phase Q.

## Validation checklist (must all pass)

```bash
cd orbital-cortex/apps/api
ruff check app tests scripts
mypy app
pytest tests -q
# optional: RUN_LIVE_STAC=1 pytest tests/test_catalog_integration.py -q

cd ../web
npm run lint
npm run build
```

## Acceptance criteria

- [ ] Real STAC provider abstraction + Planetary Computer implementation
- [ ] Discover over NY Harbor (live or recorded fixture based on real shape) returns real item IDs / acquisitions / footprints
- [ ] Results persisted as `MissionDataCandidate` with source URL + retrieval timestamp + truth_status
- [ ] Duplicates not re-inserted
- [ ] Upstream outages produce clear errors (no fabricated items)
- [ ] Mocked tests pass; optional live test exists and is skipped by default
- [ ] Mission ownership enforced
- [ ] OpenAPI + TS types regenerated
- [ ] `BUILD_PROGRESS.md` updated; next phase listed as H

## Explicit non-goals (do not do in this phase)

- Do not build the planning engine, PDF export, homepage rewrite, or full `/plan` wizard
- Do not task satellites or download full rasters to R2 yet (Phase M)
- Do not remove or rewrite the Job/demo pipeline
- Do not start Phase H

## Commit message

```
feat: integrate real STAC satellite data discovery
```

Commit only if the user asked you to commit this phase; otherwise leave changes ready and report.

## Stop condition

When acceptance criteria pass and progress is updated, **stop**. Do not begin Phase H.
