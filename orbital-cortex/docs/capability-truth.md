# Capability Truth

Use this reference before publishing product copy. Specificity is a feature.

## Safe top-level description

Nomos Orbital is a production-deployed orchestration demo. The API, database,
queue, worker, routing audit, PostGIS storage, and artifact delivery are real.
Routing uses deterministic SGP4 contact windows over public, pinned orbital data.
Compute execution and inference are simulated, and the New York Harbor SAR output
is an offline reference result.

## Truth classes

### Production infrastructure

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
- dated CelesTrak TLE snapshot, pinned by default
- public ground-station names and coordinates
- Skyfield/SGP4 AOS, culmination, LOS, elevation mask, duration
- modeled downlink volume from rate and duration

Safe language: **real orbital mechanics**, **SGP4 pass calculations**,
**pinned public TLE snapshot**, **reference ground-station geometry**.

Do not say: **live tasking**, **real-time scheduling**, **operational station
network**, or **ground-station partners**.

### Simulated execution

- orbital and cloud compute nodes
- hardware classes and model support
- node availability, latency, and provider costs
- workload reservation and execution
- ship, crop, and disaster inference

Safe language: **simulated compute candidates**, **modeled estimates**,
**deterministic demo inference**.

Do not say: **orbital nodes online**, **live orbital inference**, or
**provider inventory**.

### Offline reference data

- New York Harbor Sentinel-1-style scene metadata
- canned GeoJSON vessel detections
- authored AIS correlation flags
- mock COG URL, not a served SAR raster

Safe language: **offline reference scene**, **canned demo detections**,
**illustrative AIS correlation**.

Do not say: **live SAR**, **live AIS**, **current vessel intelligence**, or
**satellite imagery processed on demand**.

## Important qualifications

- `oc_demo_public` is a shared demo credential. The API does not enforce auth.
- Job creation is rate-limited by IP.
- Events are append-only. Routing decisions carry hashes. Events are not
  cryptographically signed.
- The worker normally completes queued jobs. `/v1/simulate/run/{id}` is a
  synchronous local/dev fallback.
- Only ship detection receives the rich NY Harbor reference scene.
- Ground-station operational parameters are authored simulator values.

## Customer-facing proof

| Proof | Endpoint |
| --- | --- |
| Submit and track a job | `POST /v1/jobs`, `GET /v1/jobs/{id}` |
| Inspect lifecycle | `GET /v1/jobs/{id}/events` |
| Explain a route | `GET /v1/jobs/{id}/routing` |
| Verify deterministic replay | `POST /v1/jobs/{id}/replay` |
| Read orbital registry | `GET /v1/satellites` |
| Inspect SGP4 passes | `GET /v1/contact-windows` |
| Read scene provenance | `GET /v1/jobs/{id}/scene` |
| Retrieve detections | `GET /v1/jobs/{id}/detections` |
| Retrieve artifact manifest | `GET /v1/jobs/{id}/result` |
| Check service health | `GET /healthz`, `GET /readyz` |

## Deferred

Authentication and tenancy, real node adapters, live satellite tasking, provider
station scheduling, live SAR processing, real orbital GPU execution, billing,
webhooks, and cryptographic event signing.
