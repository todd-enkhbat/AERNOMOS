# Mission planner overview

## Status

**Real today:** The end-to-end private mission workflow — describe an objective,
draw an area of interest, search real public catalogs, calculate real orbital
and communication constraints, generate ranked source-backed plans, inspect
truth-labeled values, export a brief, and share it privately. One real CPU
execution path proves the system can run a step.

**Simulated:** Cloud processing options, the ground-station operational
parameters, and curated example scenes are `SIMULATED` and labeled as such.

**Not yet built:** Satellite tasking, ground-station reservation, onboard
execution, commercial pricing, and accounts/organizations. See
[`demo-limitations.md`](demo-limitations.md).

## What the product does

> Nomos Orbital turns a space-data objective into a source-backed infrastructure
> plan.

A user describes a mission — an objective, an area of interest, a date range,
and constraints (deadline, data residency, preferred compute location). Nomos:

1. Searches **real public satellite-data catalogs** for scenes covering the area
   and time ([`data-sources.md`](data-sources.md)).
2. Calculates **real orbital and communication constraints** (satellite passes,
   ground-station contact windows) from current public orbital elements.
3. Generates **multiple structured plans** — feasible, conditional, and rejected
   — using a deterministic engine ([`planning-engine.md`](planning-engine.md)).
4. Labels **every headline value** with a truth status
   ([`truth-statuses.md`](truth-statuses.md)) so a reader always knows what is
   observed, calculated, estimated, simulated, stale, or unavailable.
5. Produces a **shareable technical mission brief** (PDF + versioned JSON) behind
   a private link.

## Who it is for

- **Remote-sensing / GEOINT teams** who need to plan how a space-data workload
  should move across satellite, ground, edge, and cloud infrastructure before
  committing budget or vendor contracts.
- **Mission and infrastructure engineers** who want a traceable, source-backed
  comparison of execution paths with explicit assumptions.
- **Design partners** evaluating whether a vendor-neutral planning layer is
  worth integrating their infrastructure into.

It is explicitly **not** an AI-model company, a GPU-inference product, or a
satellite-tasking broker. The value is planning, truthfulness, and traceability.

## Surfaces

**Public marketing surface** — `/`, `/how-it-works`, `/examples`, `/docs`.
Explains the product and shows curated example missions.

**Private mission workspace** — `/plan`, `/missions`, `/missions/[id]`,
`/share/[token]`. Contains the private mission-planning workflow, entered with an
anonymous session (no login). See [`privacy-model.md`](privacy-model.md).

## How to use it (customer path)

1. Open the site and click **Build a mission plan**.
2. Describe the objective, draw an AOI, set the date range and constraints.
3. Run catalog discovery to see real candidate scenes.
4. Generate plans and read the recommendation and alternatives.
5. Inspect truth badges and sources on any value.
6. Export the brief and/or create a private share link.
7. Optionally run the one real CPU execution demo on a feasible step.

## Programmatic access

The Python SDK mirrors the customer path with customer terminology (mission,
plan, candidate, share link) and never exposes database models:

```python
from orbitalcortex import Client

client = Client(base_url="https://api.nomosorbital.com")
mission = client.missions.create(
    title="Harbor monitoring",
    objective_type="analyze_imagery",
    area_of_interest={"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
)
plan = client.missions.generate_plan(mission["id"])
report = client.missions.export_pdf(mission["id"])
```

Typed errors and their API mappings are documented in
[`provider-integrations.md`](provider-integrations.md#sdk-error-mapping).

## Related docs

- [`data-sources.md`](data-sources.md) — which catalogs and providers are queried.
- [`planning-engine.md`](planning-engine.md) — how a request resolves to a plan.
- [`privacy-model.md`](privacy-model.md) — the privacy and isolation model.
- [`truth-statuses.md`](truth-statuses.md) — the provenance vocabulary.
- [`provider-integrations.md`](provider-integrations.md) — adding a provider + SDK errors.
- [`demo-limitations.md`](demo-limitations.md) — what a live demo does and does not show.
- [`accelerator-demo-script.md`](accelerator-demo-script.md) — the demo arc.
