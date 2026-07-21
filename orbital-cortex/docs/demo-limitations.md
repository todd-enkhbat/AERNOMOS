# Demo limitations

Read this five minutes before a live call. It is the unhedged list of what a
Nomos Orbital demo will and will not show working end to end **right now**. If
an investor or design partner pushes on any claim here, the honest answer is
already written down. Nothing in this file is aspirational.

Truth-status vocabulary used below is defined once in
[`truth-statuses.md`](truth-statuses.md).

## Status

**Real today:**
- Real public catalog search over a drawn area of interest (Microsoft Planetary
  Computer STAC; Sentinel-1 GRD by default, Sentinel-2 L2A optional). Returned
  scene IDs, acquisition times, footprints, and asset lists are
  `PROVIDER_REPORTED`.
- Real orbital math: TLEs pulled from CelesTrak (`PROVIDER_REPORTED` when fresh,
  `STALE` when the epoch is older than 7 days or a pinned snapshot is used).
  Contact windows are `CALCULATED` with SGP4/Skyfield and tied to a specific
  snapshot ID so they are reproducible.
- A structured, deterministic planning engine (no LLM in the feasibility path)
  that generates feasible, conditional, and rejected plans with explicit
  rejection reasons and a recommendation.
- Truth-status labels on every headline value, in the API envelope, the UI, and
  both export formats (PDF + versioned JSON).
- Private anonymous sessions, mission isolation between sessions, and private
  share links (raw token shown once, only a SHA-256 hash stored).
- One real CPU execution path: `crop_geotiff` and `thumbnail` run on the ARQ
  worker, producing `OBSERVED` durations/byte counts and a real artifact in
  object storage.

**Simulated:**
- The cloud compute option (`Nomos simulated cloud`) is a `SIMULATED` provider,
  not a connected cloud account.
- Ground-station **operational** parameters (latency, downlink, availability)
  are `SIMULATED`. Ground-station **coordinates** are `PROVIDER_REPORTED`.
- Curated `/examples` missions each seed one authored reference scene labeled
  `SIMULATED` so a brief always renders even when the live catalog returns
  nothing.
- The legacy `/jobs` ship-detection demo is fully `SIMULATED` and isolated from
  the mission workflow. It is not linked from primary navigation.
- Design-partner providers in the registry (Unibap, Ubotica, KP Labs, EDGX,
  Aethero) are seeded from **public information only**
  (`public_data_only` / `sandbox_requested`). No live sandbox is connected.

**Not yet built:**
- Satellite tasking, ground-station reservation, and onboard execution are not
  performed. Plans that require them are `conditional` (tasking) or `rejected`
  (onboard), with the reason attached.
- Commercial pricing. Cost estimates are always `UNAVAILABLE`; a mission with a
  `max_cost_usd` is rejected with `cost_unavailable` rather than inventing a
  price.
- Satellite ground-track coordinates are not exposed by the API, so the map
  labels the track `UNAVAILABLE`.
- Planetary Computer SAS asset signing is deferred, so raw asset **download**
  from the catalog is limited to what the allowlist supports.
- Accounts / organizations / enterprise auth. Sessions are anonymous only.

## What a live demo shows working end to end

1. Draw an AOI at `/plan`, set an objective and constraints, create a private
   mission (no login).
2. Run catalog discovery and see **real** Sentinel scene candidates with
   provenance and freshness.
3. Generate plans and see a recommended plan plus feasible / conditional /
   rejected alternatives, each with reasons.
4. Inspect truth badges and source popovers on every headline value.
5. Export a PDF and a versioned JSON brief; create a private share link and open
   it in a second browser.
6. Run one real CPU task (crop → thumbnail) and see `OBSERVED` duration and a
   real output thumbnail.

## What will NOT work in a live demo (say so plainly)

- No satellite is tasked and no ground station is reserved. The
  satellite→ground→cloud plan is explicitly `conditional`
  (`tasking_api_unavailable`).
- No onboard/edge model runs on a satellite. Onboard plans are `rejected`
  (`onboard_provider_unavailable`).
- No dollar figure is real. Every cost is `UNAVAILABLE` by design.
- Cloud processing in a plan is a `SIMULATED` provider step, not a run on a
  connected cloud account. (The separate CPU-execution demo is the only real
  execution, and it runs on Nomos's own worker, not a customer cloud.)
- Free-form `/plan` catalog discovery is live, so if Planetary Computer is down
  or rate-limits us, discovery returns a typed `catalog_unavailable` /
  `catalog_rate_limited` error and shows **no** candidates. We never fabricate
  scenes to fill the gap. **Accelerator demos 1–3** bypass this by default:
  they load pinned real STAC fixtures (see below).

## Accelerator demos (Phase R) — pinned fixtures by default

Three curated demos reset from a single command each
(`python -m app.seed --demo=1|2|3 --reset`). Full pitch script:
[`accelerator-demo-script.md`](accelerator-demo-script.md).

| Demo | Default catalog | Why |
| --- | --- | --- |
| 1 — NY Harbor / Sentinel-1 | Pinned fixture (`demo1_maritime_ny_harbor_s1.json`) | Live PC outage or flaky wifi must not kill the pitch |
| 2 — Disaster / Gulf | Pinned fixture (`demo2_disaster_gulf_s1.json`) | Same — urgent framing does not skip truth labels |
| 3 — Edge + CPU | Pinned fixture (`demo3_edge_bayarea_s2.json`) | Catalog offline; CPU crop still runs live on Nomos worker |

Fixtures are **real Planetary Computer STAC items** captured once and checked
into `app/catalog/fixtures/` — dated acquisitions with real item IDs, not
invented scenes. Truth status remains `PROVIDER_REPORTED` with
`asset_metadata.nomos_fixture` provenance. Pass `--live` on seed to re-fetch
from the network when you specifically want to prove live connectivity.

This is a truth-status disclosure, not something to hide on a call: say
“pinned real catalog responses so the demo survives bad wifi.”

## Demo fragility / preconditions

- **Interactive `/plan` discovery is live upstream.** For free-form AOIs (not
  the three accelerator demos), Planetary Computer must be reachable. Have a
  curated `/examples` mission open as a fallback; its brief renders from a
  seeded `SIMULATED` scene.
- **Accelerator demos 1–3 do not need live PC** when seeded with the default
  (fixture) path. They still need the local API + DB; Demo 3 CPU needs Redis
  or the sync fallback.
- **CPU execution needs a feasible `cloud_process` / `edge_process` step.** For
  Demo 3 use `python -m app.seed --demo=3 --reset --execute`, or generate plans
  then click **Run CPU demo** on the brief.
- **Orbital data can be `STALE`.** If CelesTrak was unreachable at the last
  refresh, contact windows are computed from a pinned snapshot and labeled
  `STALE`. This is correct behavior, not a bug — but call it out before someone
  else does.
- **Redis down locally** falls back to synchronous in-process execution; results
  are identical but there is no async job queue in that mode.

## The one-sentence honest pitch

> Nomos turns a space-data objective into a source-backed infrastructure plan:
> it searches real public catalogs, calculates real orbital and communication
> constraints, compares feasible execution paths, labels every assumption, runs
> one real CPU task to prove execution, and produces a shareable brief — without
> claiming any satellite tasking, ground-station booking, onboard execution, or
> commercial pricing that it does not actually perform.
