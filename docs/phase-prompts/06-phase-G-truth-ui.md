# Phase G — Source provenance and truth-status labeling (API + UI)

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- A–C, F, H complete (TruthStatus enum exists; catalog + orbital provenance produce labels)

## Product goal

Every important mission-facing number can show **status + source + timestamp + method + explanation**. Simulated/estimated values must look visually distinct from observed/calculated.

## Backend

### Provenance envelope

Define a reusable schema (Pydantic), e.g. in `app/models/provenance.py`:

```python
class ProvenancedValue(BaseModel):
    value: Any
    truth_status: TruthStatus
    source: str | None = None
    retrieved_at: str | None = None  # ISO UTC
    effective_at: str | None = None
    method: str | None = None
    explanation: str | None = None
    freshness: str | None = None  # e.g. "fresh" | "stale" | "unknown"
```

Apply it to mission-facing numeric/date fields that already exist or are returned by:

- catalog candidates (sizes, acquisition times)
- contact windows (AOS/LOS, duration, est downlink)
- any early plan estimate stubs if present

Do **not** require wrapping every string title. Focus on numbers, times, costs, confidence, sizes, durations.

Include provenance in OpenAPI; regenerate:

```bash
cd orbital-cortex/apps/api && python -m scripts.export_openapi ../../openapi.json
cd ../web && npm run generate:api-types
```

## Frontend components

Create under `orbital-cortex/apps/web/components/truth/` (or similar):

| Component | Role |
| --- | --- |
| `TruthBadge` | Compact status chip: OBSERVED / CALCULATED / … |
| `SourcePopover` | On click/hover: source, retrieved_at, method, explanation |
| `FreshnessIndicator` | Fresh vs stale visual |
| `AssumptionPanel` | List of assumptions / UNAVAILABLE integrations |

Style guidance:

- Match existing Nomos Record / archive primitives (`components/archive/ArchivePrimitives.tsx` `DemoBoundary` patterns)
- SIMULATED and ESTIMATED must be **visually distinct** from OBSERVED / CALCULATED / PROVIDER_REPORTED
- STALE and UNAVAILABLE must be obvious warnings, not decorative
- Avoid purple glow / generic AI dashboard aesthetics

### Example copy for popovers

**CALCULATED contact window**

- Source: CelesTrak TLE snapshot `{snapshot_id}`
- Retrieved: …
- Method: SGP4 via Skyfield
- Elevation mask: …
- TLE epoch: …

**SIMULATED**

> This value is generated for demonstration and is not connected to a provider.

**UNAVAILABLE**

> Nomos has not connected to a provider capable of performing this action.

Wire badges into:

- `/missions/[id]` candidate list (from Phase F)
- Any contact-window / infrastructure panel from Phase H
- Keep Job demo pages honest too where easy (label simulated detections if shown) — full isolation is Phase L

## Tests

- Backend: provenance schema serialization / OpenAPI includes fields
- Frontend: smoke render tests if the repo has a pattern; otherwise Story-free manual checklist in BUILD_PROGRESS
- Ensure no core mission number API field ships without `truth_status`

## Acceptance criteria

- [ ] Provenance envelope in API for important mission values
- [ ] TruthBadge + SourcePopover + FreshnessIndicator + AssumptionPanel exist
- [ ] Simulated/estimated visually distinct
- [ ] OpenAPI + TS types regenerated
- [ ] `BUILD_PROGRESS.md` updated

## Non-goals

- Do not rewrite homepage (Phase D)
- Do not build full plan timeline UI (Phase J) beyond wiring badges where data exists
- Do not start Phase E

## Commit message

```
feat: add source provenance and truth-status labeling
```

## Stop

Next phase is E (guided mission builder).
