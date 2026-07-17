# Phase K — Mission brief PDF, JSON export, and private sharing UI

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- Mission result page (J) and ShareLink model (B/C) exist

## Product goal

Users can export a professional mission brief (PDF + versioned JSON) and share a mission via a private unguessable link with expiry/revocation.

## PDF (WeasyPrint)

- Render HTML via Jinja template → PDF in the **ARQ worker** (not on the request thread for large jobs; small sync OK for MVP if fast)
- Store artifact via existing `app/core/object_store.py` (R2 or local)
- Include: mission summary, AOI/timeframe, recommendation, timeline, alternatives, map image or static geo summary, assumptions, sources, truth-status legend, missing integrations, next actions, generation timestamp
- Disclose simulations / unavailable integrations clearly in the PDF
- System deps: WeasyPrint may need OS libs in `Dockerfile` — update Docker build and verify `docker build` for API image

Endpoints (owner session):

- `POST /v1/missions/{id}/exports/pdf` → starts job / returns artifact URL when ready
- `GET` status or signed download URL

## JSON export

Versioned document, e.g. `schema_version: 1`, including:

- mission input
- source snapshots
- candidate plans + steps
- selected plan
- assumptions, truth statuses, rejection reasons, source evidence

`GET /v1/missions/{id}/exports/json` (owner or valid share with permission)

## Shareable private page

- Frontend route `/share/[token]` (raw token in URL — only hash stored server-side; existing ShareLink create/revoke from Phase C)
- Read-only mission brief view (subset of J)
- UI on owned mission: copy link, set expiry, revoke
- Invalid / expired / revoked → clear error, no data leak
- Shared links must not expose unrelated missions

## Tests

- Export authorization (other session 401/403)
- Share isolation
- Revoked/expired share fails
- JSON schema version present and valid
- PDF generation smoke test (may mock WeasyPrint in unit tests + one integration if feasible in CI)

## Acceptance criteria

- [ ] PDF readable/professional with disclosures
- [ ] JSON valid and versioned
- [ ] Share page works; revoke/expiry enforced
- [ ] Unrelated missions inaccessible
- [ ] Docker/API deps updated if needed
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
feat: add mission brief PDF JSON and private sharing
```

## Stop

Next is Phase L.
