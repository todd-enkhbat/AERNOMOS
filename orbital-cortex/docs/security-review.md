# Security review — private mission planning (Phase S)

Review date: 2026-07-19  
Scope: `orbital-cortex/apps/api` mission planner + legacy job demo surfaces  
Method: checklist investigation, targeted hardening, automated security tests

## Status summary

| Area | Result |
| --- | --- |
| Mission authorization (owner / share / example) | **pass** |
| Anonymous session cookies | **pass** |
| Share-token entropy / hashing / revoke / expiry | **pass** (query param deprecated) |
| Rate limiting | **pass** (after fix) |
| Input validation / GeoJSON / uploads | **pass** |
| Object storage / signed URLs | **pass** |
| Data retention / session cleanup | **pass** (opportunistic; documented) |
| Log redaction | **pass** (after fix) |
| Secrets / CORS / CSRF | **pass** (after production secret gate) |
| SSRF / remote URL allowlist | **pass** (after fix) |
| SQL injection | **pass** |
| Public API enumeration | **pass** (after job IDOR fix) |
| Export authorization | **pass** |

**High-severity findings fixed in this phase:** legacy job IDOR (unauthenticated read + simulate + signed URL minting), missing mission/discover/export/execute rate limits, share-token path logging, default production signing salts, unconstrained share `permissions`, remote URL allowlist for future fetches.

---

## Checklist

### 1. Mission authorization (owner vs share vs example) — **pass**

- Gate: `load_mission_for_access` / `get_mission_for_read` / `get_owned_mission` in `app/deps/auth.py`.
- Examples (`is_example=true`) are world-readable; mutations require ownership and reject examples.
- Share tokens grant **read** only (never passed into owned routes).
- Cross-session private access → `403 mission_forbidden`.
- Tests: `test_mission_sessions.py`, `test_security_phase_s.py`.

### 2. Anonymous session handling; cookie flags — **pass**

- Mint: `secrets.token_urlsafe(32)`; store SHA-256 only (`app/core/tokens.py`).
- Cookie: HttpOnly, Secure when `APP_ENV=production`, SameSite=Lax, optional `Domain`.
- Raw token never returned in JSON session bodies.
- Test: `test_session_cookie_flags_in_production`.

### 3. Share-token entropy; hashing; revocation; expiry — **pass**

- Same mint/hash as sessions; default TTL 7 days; owner revoke sets `revoked_at`.
- Resolve endpoint returns `mission_id` + metadata only.
- **Fix:** share `permissions` constrained to `["read"]` (API + store).
- **Fix:** prefer `X-Nomos-Share-Token` header; query param marked deprecated (Referer / proxy log risk).
- Path `/v1/share/{token}` remains for UX; request logs redact the token segment.

### 4. Rate limiting — **pass** (fixed)

| Endpoint class | Limit (default) |
| --- | --- |
| `POST /v1/jobs` | `RATE_LIMIT_JOBS` = 10/minute |
| Mission create | `RATE_LIMIT_MISSIONS` = 30/minute |
| Catalog discover | `RATE_LIMIT_DISCOVER` = 20/minute |
| JSON/PDF export | `RATE_LIMIT_EXPORT` = 10/minute |
| CPU execute | `RATE_LIMIT_EXECUTE` = 10/minute |
| Feedback / design-partner | `RATE_LIMIT_LEADS` = 5/hour |

### 5. Input validation; GeoJSON; uploads — **pass**

- AOI: max 200k chars, 5k vertices, 0.01–500,000 km², WGS84 Polygon/MultiPolygon/bbox (`app/core/mission_geo.py`).
- No multipart upload API for mission content.
- Execution: fixture name allowlist, same-mission artifact keys, max input bytes / timeout.

### 6. Object-storage permissions; signed URL expiry — **pass**

- Keys namespaced (`missions/{id}/…`, `results/{job_id}/…`).
- Signed URL TTL: `SIGNED_URL_EXPIRY_S` (default 3600).
- Mission execution downloads require owner session; private job results require job access token.
- Bucket ACL is an ops assumption (private R2); isolation is API + opaque keys + short-lived URLs.

### 7. Data retention / session cleanup — **pass** (with note)

- `cleanup_expired_sessions` runs on `POST /v1/sessions` (CASCADE removes owned missions).
- No separate long-term retention cron; documented in `privacy-model.md`.
- Severity residual: **low** — opportunistic sweeper only.

### 8. Log redaction — **pass** (fixed)

- Request middleware logs method / redacted path / status / duration only (no cookies, Authorization, or query strings).
- **Fix:** `/v1/share/{token}` paths log as `/v1/share/[redacted]`.
- Analytics: HMAC session hashes; share events use link id, never raw token.

### 9. Secrets; CORS; CSRF — **pass** (fixed)

- CORS: explicit origin list, credentials allowed, never `*`.
- CSRF: SameSite=Lax + CORS allowlist (same-origin `/api/oc` proxy in local/dev).
- **Fix:** production boot refuses `dev-only-*` defaults for `ARTIFACT_SIGNING_SECRET` and `ANALYTICS_HASH_SALT`.

### 10. SSRF in remote asset retrieval — **pass** (fixed)

- Phase M `input_ref` still allows only `fixture:` / same-mission `artifact:` (no remote fetch).
- **Fix:** `app/security/remote_urls.py` allowlists Planetary Computer / Azure blob hosts, HTTPS-only, blocks credentials, localhost, and private/link-local/metadata addresses after DNS resolution.
- HTTPS `input_ref` values are validated against the allowlist then rejected until remote fetch is explicitly enabled.
- Tests: `test_ssrf_blocked_hosts`, execution allowlist rejections.

### 11. SQL injection — **pass**

- SQLAlchemy ORM / bound parameters throughout; no user-string SQL concatenation on request paths.

### 12. Public API enumeration — **pass** (fixed)

- Missions: list requires session and returns only that session’s non-example missions.
- Jobs list: curated `is_example` only.
- **Fix (was HIGH):** private visitor jobs require `X-Nomos-Job-Token` (hash stored at create; raw returned once). Unauthenticated GET-by-ID / simulate / result / routing / detections / scene → 401/403.
- Example jobs remain publicly readable by ID (intentional curated demos).

### 13. Export authorization — **pass**

- JSON export: owner, valid share, or example (`get_mission_for_read`).
- PDF create/status: owner only.
- Admin leads/analytics export: `X-Nomos-Admin-Token` with constant-time compare.

---

## Fixes shipped in Phase S

1. Job access tokens + auth dependency on all private job read/mutate routes.
2. Mission create / discover / export / execute rate limits.
3. Remote URL allowlist module + wiring for rejected remote `input_ref`s.
4. Share permissions forced to read-only.
5. Share path redaction in request logs; prefer share header.
6. Production refusal of default signing / analytics salts.
7. Frontend stores job access token in `sessionStorage` and sends `X-Nomos-Job-Token`.

## Residual / accepted risks

| Severity | Item |
| --- | --- |
| Low | Session cleanup is opportunistic (on session create), not a scheduled job. |
| Low | Share tokens still appear in browser history for `/share/{token}` and `/v1/share/{token}` (product UX); app logs redact API paths. |
| Low | Possession of a signed artifact URL allows download until expiry (normal for presigned URLs). |
| Medium (ops) | Confirm Fly secrets override signing salts and R2 credentials before each production deploy. |

## Tests

`tests/test_security_phase_s.py` covers:

- Cross-session mission deny
- Mission list not public without session
- Share revoke blocks further access
- Private job enumeration resistance + token gate
- SSRF blocked hosts
- Share path redaction
- Write share permissions rejected

## Related docs

- [`privacy-model.md`](privacy-model.md) — customer-facing privacy narrative
- [`demo-limitations.md`](demo-limitations.md) — capability honesty
- [`capability-truth.md`](capability-truth.md) — claim boundaries
