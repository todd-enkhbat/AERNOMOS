# Phase S — Security and privacy review + hardening

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

Produce `docs/security-review.md` (or `orbital-cortex/docs/security-review.md`) and **fix all high-severity findings**.

## Checklist (investigate each; record pass/fail/fix)

- Mission authorization (owner vs share vs example)
- Anonymous session handling; cookie flags (HttpOnly, Secure, SameSite, Domain)
- Share-token entropy; hashing (SHA-256); revocation; expiry
- Rate limiting (create mission, discover, export, feedback, execute)
- Input validation; GeoJSON limits; upload restrictions
- Object-storage permissions; signed URL expiry
- Data retention / session cleanup
- Log redaction (no raw tokens, no secrets)
- Secrets handling; CORS; CSRF considerations (same-origin proxy vs credentialed cross-origin)
- **SSRF** in remote asset retrieval (Phase M) — allowlist hosts (Planetary Computer, etc.)
- SQL injection (SQLAlchemy parameterization)
- Public API enumeration (missions, jobs)
- Export authorization

## Tests

Security tests for primary access paths: cross-session deny, share revoke, enumeration resistance, SSRF blocked host.

## Acceptance criteria

- [ ] `security-review.md` written
- [ ] No public mission enumeration
- [ ] No cross-session mission access
- [ ] Remote URLs allowlisted / validated
- [ ] Tokens never in logs
- [ ] High-severity issues fixed
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
security: harden private mission planning workflow
```

## Stop

Next is Phase T.
