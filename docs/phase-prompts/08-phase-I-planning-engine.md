# Phase I — Source-backed mission feasibility and planning engine

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- Missions + candidates (F) + orbital provenance (H) available
- TruthStatus + MissionPlan / MissionPlanStep / SourceEvidence tables exist (Phase B)

## Product goal

Replace “pick one fictional compute node” as the mission outcome with a **structured planner** that generates multiple plans, rejects impossible ones with reasons, ranks feasible ones, and explains the recommendation in plain language. **No LLM as source of truth** for feasibility.

## Package layout

```
orbital-cortex/apps/api/app/planner/
  __init__.py
  types.py           # PlanPattern, ConstraintResult, etc.
  constraints.py     # hard constraints
  preferences.py     # soft scoring
  patterns.py        # candidate plan generators
  estimates.py       # duration / data movement / cost with provenance
  explain.py         # structured plain-language explanation (no LLM required)
  engine.py          # orchestrate generate → evaluate → rank → persist
  hash.py            # deterministic input/snapshot hash (mirror routing replay ideas)
```

Reuse patterns from `app/routing/constraints.py` and `app/routing/scorer.py` — do not delete the Job router; the mission planner is a **new** path.

## Plan patterns to generate (when relevant)

1. **Existing imagery → cloud**  
   Catalog scene → retrieve asset → transfer to cloud/customer storage → process → return result

2. **Existing imagery → customer edge**  
   Same but process on customer edge / preferred location

3. **Satellite → ground → cloud** (often **conditional**)  
   Acquisition → next contact window → ground station → transfer → cloud  
   Mark conditional/infeasible if no tasking/reservation API exists (`UNAVAILABLE` / feasibility `conditional`)

4. **Onboard processing**  
   Acquisition → onboard model → prioritized downlink → delivery  
   Mark **infeasible or conditional** unless a real onboard provider exists (today: unavailable)

## Hard constraints (reject with reason)

Examples — implement as explicit checks with machine-readable reason codes + human messages:

- Data exists (candidates present)
- Footprint covers AOI (PostGIS intersects / covers threshold)
- Data fresh enough vs mission freshness preference
- Deadline achievable given contact windows + transfer estimates
- Resource supports required input type
- Region / residency allowed
- Data volume within max
- Provider access exists (use access_level from H / registry stubs)
- Estimated cost ≤ max **only when cost source exists**; otherwise do not invent cost — mark cost `UNAVAILABLE` and skip cost hard-fail unless user required a cost cap with no data (then reject with `cost_unavailable`)
- Contact window exists when the pattern requires downlink

## Preferences (rank feasible plans)

- Lowest latency, lowest cost (if known), least data movement, most recent data, prefer onboard, prefer customer environment, highest confidence, simplest operational path

Weights can be fixed + versioned (`PLANNER_CONFIG_VERSION = "..."`).

## Persistence

For `POST /v1/missions/{id}/plans` (owner session):

1. Generate ≥3 candidate plans when data allows (fewer OK if constraints make others impossible — still record rejected shells with reasons)
2. Write `MissionPlan` rows (`recommended` flag on winner, `status`, `summary`, estimates, `assumptions` JSON, confidence nullable)
3. Write ordered `MissionPlanStep` rows with `truth_status`, `feasibility_status`, `rejection_reason`
4. Write `SourceEvidence` linking to catalog snapshot / TLE snapshot / methods
5. Deterministic: same mission inputs + same source snapshot → same plan hashes / ordering

## Estimates

- Duration / data movement: `ESTIMATED` or `CALCULATED` with method string
- Cost: only if a real pricing source exists; else `UNAVAILABLE` — **never fictional AWS GPU prices**
- Contact wait: `CALCULATED` from SGP4 windows + snapshot id

## Explanation

`explain.py` produces structured fields the UI can render:

- Why recommended
- What is executable now vs needs provider
- Top assumptions
- Missing integrations

Optional later: LLM rewrite of these fields only — **not in this phase** unless trivial; structured text is enough.

## API

- `POST /v1/missions/{id}/plans` → generate (idempotent strategy: new version each call, or replace non-frozen versions — document choice)
- `GET /v1/missions/{id}/plans` → list plans
- `GET /v1/missions/{id}/plans/{plan_id}` → detail with steps + evidence

Auth: owner for generate; owner/share/example for read.

## Tests (`tests/test_planner.py`)

Cover:

- Deadline miss → rejection
- Cost cap with unavailable pricing behavior
- Geography / no AOI coverage → reject
- Unavailable provider / onboard path → conditional or rejected
- Stale orbital data → labeled, may still plan with STALE
- Missing catalog → clear failure / no fake feasible imagery plan
- Determinism: two runs same snapshot → same recommendation

## Validation

Full API lint/type/tests + web build if types change. Update `BUILD_PROGRESS.md`.

## Acceptance criteria

- [ ] ≥3 candidate plans where relevant
- [ ] Impossible plans rejected with reasons
- [ ] Recommendation from structured scoring
- [ ] Every estimate has provenance / truth_status
- [ ] Deterministic for same inputs + snapshot
- [ ] No LLM required for feasibility
- [ ] Tests cover the scenarios above

## Non-goals

- Do not build the full result page layout (Phase J) — API + minimal trigger from `/missions/[id]` is enough
- Do not add PDF (Phase K)
- Do not claim tasking/reservation executed

## Commit message

```
feat: build source-backed mission feasibility and planning engine
```

## Stop

Next is Phase J (mission result experience).
