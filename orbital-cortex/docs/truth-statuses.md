# Truth statuses

This is the **single source of truth** for the two provenance vocabularies used
across Nomos Orbital. Every other doc, API field, UI badge, and export legend
references these definitions rather than redefining them. If a new state is ever
needed, add it here first.

Both enums live in code:

- `truth_status` → `app/db/truth.py` (`TruthStatus`)
- `integration_status` → `app/db/infrastructure_types.py` (`IntegrationStatus`)

## Status

**Real today:** Both enums are enforced in code. `truth_status` is attached to
every headline value in the API envelope, the UI truth badges, and both export
formats. `integration_status` is attached to every provider-backed plan step.

**Simulated:** The `SIMULATED` / `simulated` states are used deliberately for the
demo cloud provider, curated example scenes, and ground-station operational
parameters.

**Not yet built:** No new states are planned. `sandbox_connected` and
`partner_connected` are defined but not yet earned by any live provider.

---

## `truth_status` — value provenance

Applied to individual **values** (a duration, a footprint, a contact time, a
byte count). Answers: "how do we know this number?"

| Status | Meaning | Example in Nomos |
| --- | --- | --- |
| `OBSERVED` | Directly measured from a real run. | CPU-execution duration and output byte count on the ARQ worker. |
| `CALCULATED` | Deterministically computed from real inputs. | Contact windows via SGP4/Skyfield from a specific TLE snapshot. |
| `PROVIDER_REPORTED` | Reported by an external provider, stored verbatim. | Sentinel scene IDs, acquisition times, footprints from the STAC catalog; ground-station coordinates. |
| `ESTIMATED` | Derived by a heuristic/model, not measured. | Planner transfer/duration estimates. |
| `SIMULATED` | Generated for demonstration; not connected to real infrastructure. | Demo cloud provider steps; authored example scenes; ground-station latency/downlink/availability. |
| `STALE` | Real once, but past its freshness window. | TLEs older than 7 days, or a pinned snapshot used because CelesTrak was unreachable. |
| `UNAVAILABLE` | Nomos has not connected to a provider that can produce this value. | All cost figures; satellite ground-track coordinates. |

Rules of use (enforced by the build loop and Phase G/N/O work):

1. Never show a headline value without one of these statuses.
2. Never upgrade a status you cannot justify (e.g. never label a heuristic
   `CALCULATED`, never label an estimate `OBSERVED`).
3. When a real source is unavailable, prefer `UNAVAILABLE` or `SIMULATED`
   (clearly labeled) over inventing a value.

## `integration_status` — provider connection state

Applied to a **provider/resource**, describing how connected Nomos actually is.
Answers: "can Nomos really use this provider right now?"

| Status | Connected? | Meaning |
| --- | --- | --- |
| `public_data_only` | No | Only public product/marketing information is known. |
| `documented_api` | No | A public API is documented, but Nomos has not integrated it. |
| `sandbox_requested` | No | Sandbox/eval access has been requested but not connected. |
| `sandbox_connected` | **Yes (sandbox)** | A working sandbox connection exists. |
| `partner_connected` | **Yes (live)** | A production partner integration exists. |
| `simulated` | No | A placeholder provider used only for demonstration. |
| `unavailable` | No | Known to exist but not usable by Nomos. |

Only `sandbox_connected` and `partner_connected` count as **connected**.
`documented_api` and `sandbox_requested` are public-information states and never
imply live access. See [`provider-integrations.md`](provider-integrations.md)
for the current per-provider states and how a new provider is added.

## Badge colors (UI)

Defined in Phase G and kept consistent across the app:

- Cobalt: `OBSERVED`, `CALCULATED`, `PROVIDER_REPORTED` (grounded in real data).
- Hatched gold: `SIMULATED`, `ESTIMATED` (generated / derived).
- Vermilion: `STALE`, `UNAVAILABLE` (caution — not currently reliable/available).
