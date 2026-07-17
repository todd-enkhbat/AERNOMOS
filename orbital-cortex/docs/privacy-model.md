# Privacy model

This is the document a design partner's legal or security contact would read. It
is written for a non-engineer. It describes how Nomos Orbital handles the
information you enter when planning a mission.

## Status

**Real today:** Private anonymous sessions, per-session mission isolation,
hashed session and share tokens, revocable/expiring private share links, and
privacy-safe analytics that never store your mission content. These are enforced
in code and covered by tests.

**Simulated:** Nothing about privacy is simulated. The simulation boundary is
about *capabilities* (see [`demo-limitations.md`](demo-limitations.md)), not
about how your data is handled.

**Not yet built:** User accounts, organizations, and enterprise SSO. Today
everything is anonymous. There is also no long-term data-retention automation
beyond session expiry/cleanup.

## The one thing to know first

> **This is a demo environment. Do not submit proprietary or export-controlled
> information.** This warning is shown in the product, and it is the honest
> operating assumption behind everything below.

## Who can see a mission

- A mission is created inside a **private anonymous session**. No login, no
  email, no account.
- Only the browser that created the session can list or open that session's
  missions. **Two different browsers cannot see each other's missions.**
- Missions are **not publicly enumerable** — there is no public feed of all
  missions, and knowing a mission's ID is not enough to open someone else's
  mission.
- Curated **example** missions are stored separately and explicitly marked as
  public examples. They are never mixed into a private session's list.

## How the session works (plainly)

- On first visit to the mission workspace, Nomos creates a random session token.
- Only a **one-way hash** of the token is stored on the server. The raw token
  lives only in a secure browser cookie.
- The cookie is **HttpOnly** (JavaScript can't read it), **Secure** (HTTPS only
  in production), and **SameSite=Lax**.
- Sessions expire and are cleaned up automatically.

## Sharing a mission

- You can create a **private share link**. The link contains an unguessable
  token; only a one-way hash is stored.
- Share links are **read-only**, can be given an **expiration**, and can be
  **revoked** at any time.
- Revoked or expired links stop working immediately.
- Resolving a share link returns **only** the one mission it points to — never a
  list, never unrelated missions.

## What we measure (analytics)

Nomos records privacy-safe product and operational analytics (Phase O), under a
strict rule: **your mission content is never stored in analytics.**

- Analytics events use an **allowlist** of fields. Anything not on the allowlist
  is rejected before it is ever written — this is enforced, not aspirational.
- Your area of interest, notes, titles, and other free-text mission content are
  **not** recorded in analytics.
- Sessions appear in analytics only as an **HMAC hash**, never as a raw token or
  cookie value. Share tokens are never logged.

## Feedback and design-partner requests

- If you submit feedback or request a design-partner conversation (Phase P),
  that data is stored in **private, write-only** tables. There is no public read
  endpoint.
- Providing contact details requires explicit permission-to-contact, and there
  is spam protection (a honeypot field and per-IP rate limiting).

## Remote data handling

- When Nomos searches catalogs, it queries **public** providers (e.g. Microsoft
  Planetary Computer). See [`data-sources.md`](data-sources.md).
- Nomos does not upload your mission content to third parties as part of
  planning. Catalog queries are derived from the geographic area and time range,
  not from your free-text notes.

## Summary for a security reviewer

| Control | Status |
| --- | --- |
| Cross-session mission access | Prevented (tested) |
| Public mission enumeration | Prevented (tested) |
| Session token storage | SHA-256 hash only; raw token in HttpOnly/Secure cookie |
| Share token storage | SHA-256 hash only; raw token shown once |
| Share link revocation / expiry | Supported (tested) |
| Analytics field control | Allowlist, unknown keys rejected at emit |
| Mission content in analytics | Never stored |
| Session identifiers in analytics | HMAC hash only |
| Lead / feedback data | Private, write-only; permission + rate limit |

A full adversarial review (SSRF, CSRF, input validation, object-storage
permissions, signed-URL expiry, log redaction) is scheduled as Phase S and will
be captured in `security-review.md`.
