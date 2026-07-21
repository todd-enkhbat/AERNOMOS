# Provider integrations

How a new infrastructure provider is added to Nomos, and how the SDK surfaces
API errors. This is the "here's how easy integration is" artifact for a call
with an edge/onboard-compute partner (EDGX, Aethero, KP Labs, etc.).

Truth-status and integration-status vocabulary is defined in
[`truth-statuses.md`](truth-statuses.md).

## Status

**Real today:** Providers are added by checking in a versioned YAML file and
running an idempotent ingest. The planner reads the registry at plan time; no
planner core code changes to add a provider. The SDK maps real API error
responses to typed exceptions.

**Simulated:** The bundled `Nomos simulated cloud` provider is a `SIMULATED`
placeholder used so a plan can show a cloud step during the demo.

**Not yet built:** No live `sandbox_connected` / `partner_connected` provider
exists yet. Adding real credentials/heartbeats is future work.

## Adding a provider (config + ingest)

A provider is one YAML file under `orbital-cortex/config/providers/`:

```yaml
provider_name: KP Labs            # customer-facing name (verbatim in docs)
resource_type: edge               # satellite | orbital_compute | ground_station
                                  # | cloud | edge | storage | network
external_id: null
api_available: false
sandbox_available: true
auth_required: false
supported_task_types:
  - edge_process
supported_data_formats: []
geography: null                   # leave null rather than guess
pricing_source: null              # leave null rather than guess
capacity_source: null             # leave null rather than guess
current_status: unknown
data_freshness: "2026-07-17"
contact_info: null
integration_status: sandbox_requested   # see truth-statuses.md
truth_status: PUBLIC_SOURCE              # PUBLIC_SOURCE | SIMULATED
source_url: https://www.kplabs.space/solutions/hardware/leopard
notes: >
  Short, sourced description. No invented pricing/capacity.
```

Then ingest (idempotent, keyed on `(provider_name, external_id)`):

```bash
cd orbital-cortex/apps/api && python -m app.scripts.ingest_providers
python -m app.scripts.show_registry       # inspect the ingested rows
```

Rules enforced at ingest time:

- Non-`SIMULATED` rows must carry a real `source_url`.
- `integration_status` must be one of the `IntegrationStatus` values.
- Fields that are not publicly disclosed (pricing, capacity, geography) stay
  `null` — Nomos never guesses them.

The app also runs the same idempotent ingest at seed/startup, so a fresh
deployment cannot silently start with an empty registry.

## How the planner uses the registry

At plan time the engine reads the registry into its context and attaches
`integration_status`, `source_url`, and `registry_truth_status` to cloud/edge
steps. Only `sandbox_connected` and `partner_connected` are treated as
connected; `documented_api` and `sandbox_requested` remain public-information
states and never imply live access. **No planner core code changes to add a
provider** — the file + ingest is the whole integration surface.

## What "connected" would take

To move a provider from `sandbox_requested` to `sandbox_connected`:

1. Obtain sandbox credentials (stored as server-side secrets, never exposed to
   the browser).
2. Implement the provider adapter behind the existing execution/provider
   interface.
3. Flip `integration_status` and record a real `data_freshness`.

Until that happens, the provider appears in plans as public information only.

## SDK error mapping

The Python SDK raises **typed** exceptions (not a generic HTTP error) so callers
can branch on customer-meaningful conditions. Each maps to a real API error
response. Base class: `orbitalcortex.NomosError` (a subclass of `APIError`, so
`status_code`, `code`, and `response` remain available).

| SDK exception | HTTP status | API error `code` | How it is triggered | Tested end-to-end |
| --- | --- | --- | --- | --- |
| `UnauthorizedMission` | 401 / 403 | `session_required` / `mission_forbidden` | Call a mission endpoint with no session, or open another session's mission. | ✅ |
| `ExpiredShareLink` | 403 | `share_token_invalid` | Use a revoked / expired / invalid share token. | ✅ |
| `InvalidGeographicInput` | 422 | `validation_error` (field = `area_of_interest`) | Create a mission with an invalid area of interest. | ✅ |
| `NoCatalogData` | 502 | `catalog_not_found` | Discover an unknown/invalid collection upstream. | — |
| `UpstreamProviderUnavailable` | 503 | `catalog_unavailable` / `catalog_rate_limited` | The STAC provider is down or rate-limits the request. Carries `.provider_name` (from the error payload's `provider`). | — |
| `NoFeasiblePlan` | 201 (no recommendation) | `no_feasible_plan` (SDK-synthesized) | `generate_plan()` when the real plan response recommends no feasible plan (all rejected/conditional). | — |
| `StaleOrbitalData` | n/a (truth status) | `stale_orbital_data` (reserved) | `infrastructure(..., raise_on_stale=True)` when the orbital snapshot truth status is `STALE`. Carries `.age_hours`. | — |

Notes on the last two rows (kept honest per the truth-status principle):

- **`NoFeasiblePlan`** is not an HTTP error. The API deliberately returns `201`
  with rejected plans (rejected plans are first-class output rendered on the
  mission brief). The SDK derives this exception from the **real** response when
  `recommended_plan_id` is null and no plan is feasible. Pass
  `require_feasible=False` to `generate_plan()` to get the raw plan set instead.
- **`StaleOrbitalData`** is surfaced by the API as a `STALE` truth status on the
  infrastructure payload, not as an HTTP error. The SDK raises it on request
  (`raise_on_stale=True`) so callers who require fresh orbital data can fail
  fast; `.age_hours` is a best-effort age from the snapshot's `retrieved_at`.

A generic `validation_error` that is **not** about geography raises
`MissionValidationError`. Any error code with no typed mapping raises the base
`APIError`, preserving backward compatibility for the legacy job resources.

## Verifying the mapping

```bash
cd orbital-cortex/apps/api && python -m pytest tests/test_sdk_missions_phase_q.py -v
```

The suite triggers the real API condition for `UnauthorizedMission`,
`ExpiredShareLink`, and `InvalidGeographicInput` and asserts the correct typed
exception is raised.
