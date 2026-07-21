# Accelerator demo script

The ~90-second live pitch for Nomos Orbital. Section order matches the
**actual** demo arc (see [`demo-limitations.md`](demo-limitations.md)), not an
idealized one. Truth-status vocabulary:
[`truth-statuses.md`](truth-statuses.md).

## Status

**Real today:** Three accelerator demos reset from one command each, run offline
on pinned real STAC fixtures by default, and Demo 3 triggers a live Phase M CPU
execution with `OBSERVED` metrics. This script is finished and timed.

**Simulated:** Cloud process steps use the `SIMULATED` demo cloud provider;
labels are visible on the mission brief.

**Not yet built:** Live satellite tasking, ground-station reservation, onboard
execution, commercial pricing.

---

## Reset commands (no manual DB surgery)

```bash
cd orbital-cortex/apps/api
export DATABASE_URL=...   # local or demo DB

python -m app.seed --demo=1 --reset          # NY Harbor / Sentinel-1
python -m app.seed --demo=2 --reset          # Disaster / Gulf Coast
python -m app.seed --demo=3 --reset --execute  # Edge compare + real CPU crop

# Optional: prove live STAC connectivity to a technical audience
python -m app.seed --demo=1 --reset --live
```

Default catalog mode for demos is **pinned fixtures** (real Planetary Computer
items captured once). `--live` re-fetches from the network.

Mission IDs are stable. Open `/missions/{mission_id}` after seed (use the
`session_token` from the CLI JSON as the `nomos_session` cookie, or run the
flow from a browser session you own).

---

## Spoken script (~90 seconds)

<!-- TIMING: Spoken body ≈206 words across sections 1–9.
     Measured 2026-07-17: macOS `say -r 150` of the full spoken script → 94.2s
     (afinfo estimated duration). Natural pitch ≈140–150 wpm → ~88–94s.
     Cap ≤100s. Re-time after any edit:
       say -r 150 -o /tmp/script.aiff "$(paste spoken paragraphs)"
       afinfo /tmp/script.aiff | grep duration
-->

### 1. Opening hook — customer problem
Space teams waste weeks arguing how a workload should move across satellite,
ground, edge, and cloud — usually with slides, not source-backed plans.

### 2. Mission input
Here is Demo 1: New York Harbor, Sentinel-1, a deadline, U.S. data residency.
No login. Private session. Build a mission plan.

### 3. Real data discovery
Catalog discovery returns real Sentinel scenes — item IDs, acquisition times,
footprints — labeled `PROVIDER_REPORTED`. For the pitch we use pinned fixtures
of real Planetary Computer data so wifi cannot kill the demo.

### 4. Real orbital / infrastructure calculation
Contact windows are `CALCULATED` from a TLE snapshot. Coordinates are
`PROVIDER_REPORTED`. Ops parameters that we do not have live stay `SIMULATED`.

### 5. Feasible and rejected plans
Generate plans. Existing imagery to cloud is feasible. Tasking is conditional.
Onboard is rejected — unavailable, not hidden.

### 6. Recommendation + truth labels
The recommendation leads. Every headline number has a truth badge. Open a
source popover — you can audit the claim.

### 7. The OBSERVED-execution moment
Demo 3: click Run CPU demo. A real crop runs on our worker. Duration appears
as `OBSERVED` — measured, not estimated. That is the honest edge of execution
today.

### 8. Exported report + share
Export the PDF brief. Share a private link. Another browser sees only this
mission.

### 9. Close / the ask
Next integration: a real edge sandbox — KP Labs Smart Mission Lab — or a
connected cloud account. That is the design-partner conversation we want.

---

## Demo map

| Demo | Command | What you show |
| --- | --- | --- |
| 1 — Existing Sentinel imagery | `--demo=1 --reset` | Pinned real S1 candidates, feasible cloud route, onboard unavailable |
| 2 — Disaster response | `--demo=2 --reset` | Feasibility comparison table under urgent deadline; assumptions + next actions |
| 3 — Customer edge + CPU | `--demo=3 --reset --execute` | Cloud vs edge comparison; live CPU crop with `OBSERVED` duration |

## Fixture disclosure (truth-status, not a secret)

Accelerator demos **default to pinned fixtures** — real STAC items fetched once
from Microsoft Planetary Computer and checked into
`app/catalog/fixtures/`. They are `PROVIDER_REPORTED`, not fabricated. See
[`demo-limitations.md`](demo-limitations.md).
