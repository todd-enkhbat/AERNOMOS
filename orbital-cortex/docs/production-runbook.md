# Production runbook — Nomos Orbital

Operational reference for the live demo. Secrets live in platform stores only (Fly, Vercel, Upstash, Neon, Cloudflare) — never in git.

## Live URLs

| Service | URL |
| --- | --- |
| Website | https://nomosorbital.com |
| Website (www) | https://www.nomosorbital.com |
| API | https://api.nomosorbital.com |
| Fly hostname | https://orbital-cortex-api.fly.dev |

## Health checks

```bash
curl https://api.nomosorbital.com/healthz
# {"status":"ok","service":"nomos-orbital-api"}

curl https://api.nomosorbital.com/readyz
# {"status":"ready","checks":{"database":true,"redis":true}}
```

- `database: false` → check Neon `DATABASE_URL` on Fly
- `redis: false` → check `REDIS_URL` (must be Upstash `rediss://` URL, not CLI command)

## Secrets inventory

### Fly.io (`orbital-cortex-api`)

| Secret | Purpose |
| --- | --- |
| `DATABASE_URL` | Neon Postgres (pooled, PostGIS) |
| `REDIS_URL` | Upstash Redis (`rediss://default:...@....upstash.io:6379`) |
| `S3_BUCKET` | Cloudflare R2 bucket name |
| `S3_ENDPOINT_URL` | `https://<account_id>.r2.cloudflarestorage.com` |
| `S3_REGION` | `auto` |
| `S3_ACCESS_KEY_ID` | R2 API token |
| `S3_SECRET_ACCESS_KEY` | R2 API token |
| `CORS_ORIGINS` | Comma-separated web origins (must include live Vercel/domain URLs) |
| `PUBLIC_BASE_URL` | `https://api.nomosorbital.com` (signed artifact URLs) |
| `ARTIFACT_SIGNING_SECRET` | HMAC for local artifact backend (if used) |
| `APP_ENV` | `production` (set in fly.toml) |

List names only: `fly secrets list -a orbital-cortex-api`

### Vercel (`orbital-cortex/apps/web`)

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | `https://api.nomosorbital.com` |

**Important:** `NEXT_PUBLIC_*` is baked at **build time**. Changing it requires a **Redeploy** in Vercel.

### Cloudflare

| Piece | Where |
| --- | --- |
| R2 bucket | Dashboard → R2 → bucket + S3 API credentials |
| DNS `nomosorbital.com` | CNAME → Vercel (or Vercel nameservers) |
| DNS `api.nomosorbital.com` | A → Fly IP, AAAA → Fly IPv6 (grey cloud / DNS only) |

Fly cert: `fly certs check api.nomosorbital.com`

### GitHub Actions

| Secret | Purpose |
| --- | --- |
| `FLY_API_TOKEN` | Auto-deploy API on push to `main` |
| `DEMO_DATABASE_URL` | Optional nightly demo reset |

## Processes on Fly

| Process | Role | Count (typical) |
| --- | --- | --- |
| `app` | FastAPI (uvicorn) | 2 (auto-start/stop with HTTP traffic) |
| `worker` | ARQ job executor | 1 (must run for jobs to complete) |

```bash
fly machines list -a orbital-cortex-api
fly scale show -a orbital-cortex-api
```

## Troubleshooting

### Jobs stuck in `queued`

**Symptom:** POST /v1/jobs succeeds; status never advances.

**Cause:** Worker machine stopped (common after idle or deploy).

**Fix:**

```bash
fly machines list -a orbital-cortex-api
# Find machine with PROCESS GROUP = worker and STATE = stopped
fly machine start <WORKER_MACHINE_ID> -a orbital-cortex-api
```

Verify worker logs: `fly logs -a orbital-cortex-api | grep -i worker`

**Prevention:** `fly.toml` includes `[[restart]] policy = "always"` for `worker` process.

**Fallback (dev only):** `POST /v1/simulate/run/{job_id}` advances job without worker.

### "Failed to fetch" in browser

**Cause A:** Vercel bundle still points at `http://127.0.0.1:8000` → set `NEXT_PUBLIC_API_BASE_URL` and **Redeploy**.

**Cause B:** CORS — browser origin not in Fly `CORS_ORIGINS`.

```bash
fly secrets set CORS_ORIGINS="https://nomosorbital.com,https://www.nomosorbital.com,https://api.nomosorbital.com"
```

Test CORS:

```bash
curl -s -D - "https://api.nomosorbital.com/v1/jobs" \
  -H "Origin: https://nomosorbital.com" -o /dev/null | grep -i access-control
# expect: access-control-allow-origin: https://nomosorbital.com
```

### Redis URL wrong

**Symptom:** `redis: false` after setting `REDIS_URL`.

**Cause:** Pasted Upstash `redis-cli --tls -u redis://...` instead of the URL.

**Fix:** Use only `rediss://default:PASSWORD@HOST.upstash.io:6379` in `fly secrets set REDIS_URL='...'`

### Map / results empty but job complete

- Check R2 secrets on Fly
- Check `GET /v1/jobs/{id}/result` returns signed `artifacts[].url`
- Ensure `PUBLIC_BASE_URL` is production API URL

## Deploy commands

```bash
cd orbital-cortex
fly deploy --remote-only          # API + worker
fly secrets set KEY=value       # triggers rolling restart
```

Vercel: push to `main` if connected, or `cd apps/web && vercel --prod`

## Demo API key

Frontend default: `oc_test_123` (cosmetic; not real auth).
