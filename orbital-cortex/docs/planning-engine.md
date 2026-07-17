# Planning engine

How Nomos resolves a mission request into a set of ranked, source-backed plans.
Implemented in `app/planner/` (Phase I). Truth-status vocabulary is defined in
[`truth-statuses.md`](truth-statuses.md).

## Status

**Real today:** A deterministic, structured feasibility engine (no LLM in the
feasibility path) that evaluates hard constraints against real catalog and
orbital data, generates feasible/conditional/rejected plans with explicit
reason codes, ranks feasible plans, and selects a recommendation. Same inputs +
same source snapshot → identical plan hashes.

**Simulated:** Cloud steps use the `SIMULATED` demo cloud provider. Cost/latency
figures for simulated providers are not real.

**Not yet built:** No tasking/reservation is executed, so satellite→ground→cloud
plans are `conditional` and onboard plans are `rejected`.

## Request → plan, step by step

1. **Inputs.** A `Mission` (objective, area of interest, date range, deadline,
   constraints) plus persisted `MissionDataCandidate` rows from catalog
   discovery and the current orbital snapshot.
2. **Build context.** The engine assembles candidates, mission-relevant
   satellites/ground stations, contact windows, and the infrastructure provider
   registry (Phase N) into a planning context.
3. **Generate candidate plans** for the supported patterns (below).
4. **Evaluate hard constraints** per plan; reject impossible plans with a reason
   code; mark tasking/onboard-dependent plans `conditional`/`rejected`.
5. **Estimate** duration and data movement (`ESTIMATED`); cost stays
   `UNAVAILABLE` unless a real pricing source exists.
6. **Rank** feasible plans by versioned soft weights and **select** one
   recommendation.
7. **Explain** the recommendation with structured fields (an LLM may only
   rephrase this output; it is never the source of feasibility).
8. **Persist** each generation as a new version batch (`append_versions`):
   prior `recommended` flags are cleared; all plans are retained for audit.

Planner metadata (pattern, hashes, scores, estimates, explanation) is stored
inside `MissionPlan.assumptions` under `kind=planner_meta`, so the Phase B schema
is unchanged. `PLANNER_CONFIG_VERSION` is stored on every plan for
reproducibility.

## Hard constraints vs preferences

**Hard constraints** decide feasibility. Each failure carries a reason code:

| Reason code | Meaning |
| --- | --- |
| `data_missing` | No catalog scene exists for the AOI/time. |
| `aoi_uncovered` | Scene footprint covers < 5% of the AOI. |
| `data_stale` | Available data is older than the mission's freshness limit. |
| `data_volume_exceeded` | Estimated data movement exceeds the mission limit. |
| `region_not_allowed` | A step's region is outside the allowed regions. |
| `provider_access_denied` | Required provider access does not exist. |
| `cost_unavailable` | A `max_cost_usd` was set but no real pricing source exists. |
| `cost_exceeded` | Estimated cost exceeds the maximum (when a price exists). |
| `deadline_infeasible` | The deadline cannot be met. |
| `no_contact_window` | No eligible ground-station contact window exists. |
| `tasking_api_unavailable` | Satellite tasking is required but not connected → `conditional`. |
| `onboard_provider_unavailable` | Onboard execution is required but not connected → `rejected`. |
| `simulated_edge_provider` | The only edge option is a simulated provider. |
| `edge_provider_access_required` | A real edge provider is needed but not connected. |
| `customer_edge_unspecified` | Customer edge processing requested without a node. |

**Preferences** only rank feasible plans (lowest latency, least data movement,
most recent data, simplest path, highest confidence, etc.). They never make an
infeasible plan feasible.

## Supported plan patterns

- **Existing imagery → cloud** — catalog scene → retrieve → transfer to cloud →
  process → return. Cloud step is the `SIMULATED` demo provider today.
- **Existing imagery → customer edge** — as above, but process on a customer
  edge node. `conditional`/`rejected` unless a real edge provider is connected.
- **Satellite → ground → cloud** — acquisition → contact window → ground station
  → transfer → cloud. **Always `conditional`** (`tasking_api_unavailable`); no
  tasking or reservation is executed.
- **Onboard processing** — acquisition → onboard model → prioritized downlink →
  delivery. **`rejected`** (`onboard_provider_unavailable`) until a real onboard
  provider exists.

## Determinism

For the same mission inputs and the same source snapshot, the planner produces
the same candidate plans, the same ordering, and the same `plan_hash` /
`input_hash`. This is what makes a mission brief auditable and reproducible.

## What the engine deliberately does not do

- It does not invent prices — cost is `UNAVAILABLE`, not a guess.
- It does not task satellites or reserve ground stations.
- It does not use an LLM to decide feasibility.
- It does not fabricate catalog scenes or contact windows to fill gaps.
