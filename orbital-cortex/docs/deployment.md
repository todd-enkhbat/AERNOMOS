# Deployment (Group F)

## Topology

| Piece | Where | Notes |
| --- | --- | --- |
| API + worker | Fly.io (`fly.toml`, two processes) | migrations run via `release_command` |
| Postgres + PostGIS | Neon | pooled connection string in `DATABASE_URL` |
| Redis (ARQ queue) | Fly Redis / Upstash | `REDIS_URL` |
| Object storage | Cloudflare R2 (S3-compatible, zero egress) | `S3_*` env vars |
| Web | Vercel (git integration) | `NEXT_PUBLIC_API_URL` points at the API |

## Object storage (F1)

`app/core/object_store.py` puts result artifacts in S3-compatible storage;
Postgres stores **only object keys** (`results/{job_id}/detections.geojson`).
`GET /v1/jobs/{id}/result` returns time-limited signed URLs generated at
read time.

- **Production**: set `S3_BUCKET`, `S3_ENDPOINT_URL`
  (`https://<account>.r2.cloudflarestorage.com` for R2), `S3_ACCESS_KEY_ID`,
  `S3_SECRET_ACCESS_KEY`. Signed URLs come straight from the bucket.
- **Dev/tests**: leave `S3_BUCKET` empty. Bytes land in
  `apps/api/var/artifacts` and are served by `GET /v1/artifacts/{key}` with
  an expiring HMAC signature — same contract, no cloud dependency.
  docker-compose shares that directory between `api` and `worker` via the
  `artifacts` volume.

## Production hardening checklist (F2)

- [x] CORS from `CORS_ORIGINS` env (explicit origins, never `*`)
- [x] Secrets only in the platform store; repo carries `.env.example` only
- [x] No SQLite/localhost assumptions in the serving path
- [x] `POST /v1/jobs` rate-limited per client IP (`RATE_LIMIT_JOBS`, slowapi)
- [x] structlog JSON logs; every response carries `x-request-id`
- [x] Sentry enabled when `SENTRY_DSN` is set
- [x] `/healthz` (liveness) + `/readyz` (DB-gated readiness; Redis reported
      but optional — jobs queue and can run via the manual path without it)

## CI/CD (F3)

`.github/workflows/deploy.yml` on every push/PR:

```
ruff → mypy → pytest (PostGIS + Redis service containers) → SDK tests → docker build
```

On `main`, if `FLY_API_TOKEN` is configured, `flyctl deploy` follows;
`fly.toml`'s `release_command = "alembic upgrade head"` applies migrations
before the new release takes traffic (the app also migrates at boot).

`.github/workflows/sdk.yml` (E2) regenerates the low-level OpenAPI client
(`sdk/python/orbitalcortex_api`) from the exported spec on merge and
commits it back when the spec changed.

## Demo reset (F4)

`.github/workflows/demo-reset.yml` runs nightly at 06:00 UTC when the
`DEMO_DATABASE_URL` secret is configured:

```bash
python -m app.seed --reset --force
```

`--reset` wipes all job data (events, results, routing decisions, scenes,
and detections cascade) and reseeds reference data. With
`APP_ENV=production` the CLI refuses to run without the explicit `--force`
flag, so real data can't be wiped by a fat-fingered local command.
