# Phase N — Extensible infrastructure provider registry

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

The mission planner reads **registry-backed** `InfrastructureResource` records instead of hardcoded fictional nodes from `sample_nodes.json` (Job demo may still use sample nodes until fully isolated).

## Registry contents

Each provider/resource should support:

- provider name, resource type, external id
- API availability, sandbox availability, auth required
- supported task types / data formats
- geography, pricing source, capacity source
- current status, data freshness, contact info
- **integration_status:**  
  `public_data_only` | `documented_api` | `sandbox_requested` | `sandbox_connected` | `partner_connected` | `simulated` | `unavailable`

## Ingestion

- Checked-in versioned YAML or JSON under e.g. `orbital-cortex/config/providers/`
- CLI or `python -m app.scripts.ingest_providers` (or seed hook) upserts into `InfrastructureResource`
- Adding a provider = edit config + ingest — **no planner core changes**
- Secrets never exposed to the browser

## Planner change

- Phase I engine queries registry for cloud/edge/GS/orbital_compute resources
- Simulated entries must carry `truth_status=SIMULATED` and `integration_status=simulated`
- Public-info-only clearly distinguished from live connected availability

## Optional admin

Minimal internal endpoint or documented seed path is enough — full admin UI not required.

## Acceptance criteria

- [ ] Planner uses registry for mission path
- [ ] Versioned config + ingest path exists
- [ ] Public vs connected vs simulated distinct
- [ ] New provider addable without changing engine code
- [ ] Tests for ingest + planner reading registry
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
feat: add extensible infrastructure provider registry
```

## Stop

Next is Phase O.
