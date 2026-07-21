# Data sources

Which catalogs, orbital-data sources, and infrastructure providers Nomos
actually queries — and which are documented-only.

Truth-status and integration-status vocabulary is defined in
[`truth-statuses.md`](truth-statuses.md).

> **Source of truth.** Provider facts below are **not** restated from memory.
> The infrastructure provider list is generated from the checked-in registry
> configuration under `orbital-cortex/config/providers/*.yaml` (Phase N). If a
> provider is added, removed, or relabeled there, update the table below to
> match. The Phase Q doc-drift check
> (`app/scripts/check_data_sources_drift.py`) fails if the two diverge.

## Status

**Real today:** Live STAC catalog search (Microsoft Planetary Computer) and live
orbital elements (CelesTrak) are queried at runtime with provenance recorded.

**Simulated:** The `Nomos simulated cloud` provider is a `SIMULATED`
placeholder. Ground-station operational parameters are `SIMULATED`.

**Not yet built:** No live connection to any edge/onboard provider. Earth Search
(Element84) is a registered stub behind the catalog interface but is not used by
discovery.

---

## Satellite-data catalogs (STAC)

| Source | Provider id | State | Truth status of results |
| --- | --- | --- | --- |
| Microsoft Planetary Computer | `microsoft-planetary-computer` | **Live** — queried by mission discovery (Sentinel-1 GRD by default; Sentinel-2 L2A optional). | `PROVIDER_REPORTED` |
| Earth Search (Element84) | `earth-search-element84` | **Documented-only** — registered stub behind the same `DataCatalogProvider` interface; not used by discovery. | n/a |

Catalog results are persisted as `MissionDataCandidate` rows with the source
URL and retrieval timestamp. Nomos never fabricates catalog items; upstream
failures return typed errors (`catalog_unavailable`, `catalog_rate_limited`,
`catalog_not_found`). Deduplication key: `(mission_id, source_provider,
external_item_id)`.

## Orbital data

| Source | State | Truth status |
| --- | --- | --- |
| CelesTrak TLEs | **Live** — refreshed on a 6h cron; `PROVIDER_REPORTED` when fresh. | `PROVIDER_REPORTED` / `STALE` |
| Pinned TLE snapshot (`simulator/tle_snapshot.json`) | **Fallback** — used when CelesTrak is unreachable. Dated real TLEs, not authored fiction. | `STALE` |

Contact windows are `CALCULATED` with SGP4/Skyfield and tied to a specific
snapshot id so they are reproducible. TLEs older than 7 days are `STALE`. See
[`planning-engine.md`](planning-engine.md).

## Infrastructure provider registry (Phase N)

Generated from `orbital-cortex/config/providers/*.yaml`. `provider_name` values
below are verbatim from those files.

| Provider name | Resource type | Integration status | Registry truth status | Source |
| --- | --- | --- | --- | --- |
| KP Labs | edge | `sandbox_requested` | `PUBLIC_SOURCE` | https://www.kplabs.space/solutions/hardware/leopard |
| EDGX | edge | `public_data_only` | `PUBLIC_SOURCE` | https://www.edgx.space/product/sterna |
| Aethero | edge | `public_data_only` | `PUBLIC_SOURCE` | https://www.aethero.com/ |
| Unibap AB | edge | `public_data_only` | `PUBLIC_SOURCE` | https://unibap.com/solutions/ |
| Ubotica Technologies | edge | `public_data_only` | `PUBLIC_SOURCE` | https://ubotica.com/ubotica-cognisat-xe2/ |
| Nomos simulated cloud | cloud | `simulated` | `SIMULATED` | (none — simulated placeholder) |

None of the five design-partner providers are connected. Only
`sandbox_connected` / `partner_connected` count as live access. Fields left
`null` in the registry (geography, pricing_source, capacity_source) are **not**
guessed — no provider publicly discloses per-unit pricing or firm capacity.

To inspect the live registry rows:

```bash
cd orbital-cortex/apps/api && python -m app.scripts.show_registry
```

## Keeping this doc honest

The doc-drift check compares the `provider_name` values above against the
registry YAML files:

```bash
cd orbital-cortex/apps/api && python -m app.scripts.check_data_sources_drift
```

It exits non-zero if a provider exists in one place but not the other.
