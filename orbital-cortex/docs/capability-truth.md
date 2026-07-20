# Capability Truth

Use this reference before publishing product copy. Specificity is a feature.

## Safe top-level description

**Allowed product claim:**

> Nomos turns a space-data objective into a source-backed infrastructure plan.
> It searches real public data catalogs, calculates orbital and communication
> constraints, compares feasible execution paths, explains assumptions, and
> produces a shareable technical mission brief.

Nomos Orbital plans how space-data workloads should move across satellite,
ground, and cloud infrastructure. Visitors describe a mission and constraints;
Nomos searches real public catalogs, calculates contact opportunities, compares
feasible routes, and returns a source-backed technical mission brief with labeled
assumptions.

Live satellite tasking, ground-station reservation, onboard execution, private
telemetry, and commercial pricing guarantees require provider integrations that
are not yet connected. Those gaps are labeled, not invented.

A separate historical simulation demo remains at `/jobs`: production API,
database, queue, worker, routing audit, and artifact delivery are real; compute
execution, detections, and confidence scores are SIMULATED and labeled as such.

Curated public example missions live at `/examples`. Each example discloses what
is real, calculated, estimated, simulated, and unavailable.

## What Nomos does today

Safe to claim on the homepage and customer surfaces:

- searches real public data catalogs (Microsoft Planetary Computer STAC)
- calculates satellite and ground contact opportunities (SGP4 / Skyfield over
  CelesTrak TLEs, live or pinned)
- compares feasible infrastructure routes (mission planner patterns)
- labels assumptions and unavailable integrations with truth status
- generates a technical mission brief at `/missions/[id]`
- keeps visitor missions private to an anonymous browser session
- runs an optional owner-only CPU demo (fixture crop + thumbnail) with OBSERVED metrics on the real worker

Safe language: **source-backed execution plan**, **real orbital and
infrastructure data**, **technical mission brief**, **labeled assumptions**,
**private mission plan**.

## What requires provider integration

Do not claim these as live product capabilities:

- satellite tasking
- ground-station reservation
- onboard execution
- private telemetry
- commercial pricing guarantees

Safe language: **requires provider integration**, **unavailable until connected**,
**labeled on the plan**.

## Forbidden claims

Do not write or imply:

- AI ran onboard a satellite
- Satellite was tasked
- Ground station reserved
- Commercial pricing guaranteed
- Private provider availability is live
- Execution occurred unless a real adapter completed it

## Truth classes

### Mission planning (customer path)

- guided builder at `/plan`
- private anonymous sessions and optional share links
- STAC catalog candidates with `PROVIDER_REPORTED` metadata
- contact windows as `CALCULATED` from TLEs (`PROVIDER_REPORTED` or `STALE`)
- versioned provider-registry records with source URLs for every non-simulated entry
- plan steps, feasibility, and source evidence on mission briefs
- cost estimates remain `UNAVAILABLE` until a real pricing source exists

Safe language: **private mission**, **recommended plan**, **source evidence**,
**feasibility summary**.

Provider integration status is separate from truth status:

- `public_data_only`, `documented_api`, and `sandbox_requested` describe cited
  public information; they do not claim live access
- `sandbox_connected` and `partner_connected` are the only connected statuses
- `simulated` identifies an authored placeholder and must carry `SIMULATED`
- provider selection prefers a mission's named compute location, then ranks
  integration readiness deterministically; the reason is stored on the plan step

### Real CPU demo execution (Phase M — mission brief, owner-only)

Nomos can run a **lightweight real CPU demo** on the production ARQ worker for
mission owners from `/missions/[id]`:

- tasks: `crop_geotiff` (rasterio) then `thumbnail` (PNG) chained
- input: **fixture GeoTIFF** (`fixture:sample.tif`), not the mission STAC scene
- output: artifacts in object storage; durations and byte counts labeled **OBSERVED**
- cost estimate: **$0** (local CPU on existing worker)
- plan steps show **planned vs executed**; planner ESTIMATED durations are not overwritten

Safe language: **real CPU demo**, **measured OBSERVED execution**, **fixture
raster**, **owner-only**, **not live catalog download**.

Do not claim: **GPU inference**, **onboard execution**, **your catalog scene was
processed**, **operational cloud billing**, or **production imagery pipeline**.

This is distinct from the `/jobs` historical simulation demo (SIMULATED detections).

### Production infrastructure (job demo and APIs)

- FastAPI and ARQ worker on Fly.io
- Neon Postgres with PostGIS
- Upstash Redis queue
- Cloudflare R2 artifact storage with signed URLs
- persisted job state machine and append-only lifecycle events
- deterministic routing decisions and replay hashes
- rate-limited public job submission

Safe language: **production API**, **async worker**, **persisted audit trail**,
**signed artifact URLs**, **deterministic replay**.

### Public and pinned physics

- real NORAD satellite identities
- dated CelesTrak TLE snapshot, pinned when live refresh fails
- public ground-station names and coordinates
- Skyfield/SGP4 AOS, culmination, LOS, elevation mask, duration
- modeled downlink volume from rate and duration

Safe language: **real orbital mechanics**, **SGP4 pass calculations**,
**pinned public TLE snapshot**, **reference ground-station geometry**.

Do not say: **live tasking**, **real-time scheduling**, **operational station
network**, or **ground-station partners**.

### Simulated execution (historical simulation demo only)

- orbital and cloud compute nodes
- hardware classes and model support
- node availability, latency, and provider costs
- workload reservation and execution
- ship, crop, and disaster inference
- confidence scores on demo detections

Safe language: **historical simulation demo**, **simulated compute candidates**,
**modeled estimates**, **deterministic demo inference**, **simulated confidence**.

Do not say: **orbital nodes online**, **live orbital inference**,
**observed confidence**, or **provider inventory**.

These outputs must never appear as the primary customer mission outcome.

### Offline reference data (job demo)

- New York Harbor Sentinel-1-style scene metadata
- canned GeoJSON vessel detections
- authored AIS correlation flags
- mock COG URL, not a served SAR raster

Safe language: **offline reference scene**, **canned demo detections**,
**illustrative AIS correlation**.

Do not say: **live SAR**, **live AIS**, **current vessel intelligence**, or
**satellite imagery processed on demand**.

## Important qualifications

- Homepage primary CTA is mission planning (`/plan`), secondary is `/examples`.
- `/jobs` is a labeled historical simulation demo, not the primary product path.
- Curated examples are `missions.is_example=true` with disclosure metadata;
  demo reset preserves or reseeds them and never deletes example missions.
- `oc_demo_public` is a shared demo credential for the job path. Mission
  sessions use HttpOnly cookies, not that key.
- Job creation is rate-limited by IP.
- Events are append-only. Routing decisions carry hashes. Events are not
  cryptographically signed.
- The worker normally completes queued jobs. `/v1/simulate/run/{id}` is a
  synchronous local/dev fallback.
- Only ship detection receives the rich NY Harbor reference scene.
- Ground-station operational parameters may include authored simulator values
  labeled `SIMULATED`.

## Customer-facing proof

| Proof | Endpoint / surface |
| --- | --- |
| Build a private mission | `/plan`, `POST /v1/missions` |
| Browse curated examples | `/examples`, `GET /v1/missions/examples` |
| Discover catalog candidates | `POST /v1/missions/{id}/catalog/discover` |
| Generate plans | `POST /v1/missions/{id}/plans` |
| Read mission brief | `/missions/[id]`, `GET /v1/missions/{id}/plans/{plan_id}` |
| Submit and track a job (historical demo) | `POST /v1/jobs`, `GET /v1/jobs/{id}` |
| Inspect lifecycle | `GET /v1/jobs/{id}/events` |
| Explain a route | `GET /v1/jobs/{id}/routing` |
| Verify deterministic replay | `POST /v1/jobs/{id}/replay` |
| Read orbital registry | `GET /v1/satellites` |
| Inspect SGP4 passes | `GET /v1/contact-windows` |
| Read scene provenance | `GET /v1/jobs/{id}/scene` |
| Retrieve SIMULATED detections | `GET /v1/jobs/{id}/detections` |
| Retrieve artifact manifest | `GET /v1/jobs/{id}/result` |
| Check service health | `GET /healthz`, `GET /readyz` |

## Deferred

Authentication and tenancy, real node adapters, live satellite tasking, provider
station scheduling, live SAR processing, real orbital GPU execution, billing,
webhooks, and cryptographic event signing.