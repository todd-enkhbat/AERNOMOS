# Phase E — Guided customer-facing mission builder (`/plan`)

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- A–C complete (private missions API exists)
- F recommended (discover can run after create); G helpful for labels but not required to ship form

## Product goal

A non-technical user can create a **private Mission** through a multi-step form at `/plan` without Nomos jargon. Submitting creates a Mission owned by the anonymous session. Language: “Build a mission plan”, never “submit compute job”.

## Route & navigation

- Primary route: `/plan` in `orbital-cortex/apps/web`
- CTA from `/missions` and site header should point here (do not rewrite full homepage — that is Phase D; linking is fine)
- Keep `/missions` list; after create, redirect to `/missions/[id]` (or stay on review with link)

## Form steps (required)

### Step 1 — Objective

Options (map to `objective_type` string enum — define consistently backend+frontend):

- Analyze existing satellite imagery
- Plan data delivery from a satellite
- Compare onboard, ground, edge, and cloud processing
- Plan a remote-sensing workflow
- Other

### Step 2 — Area and time

Collect:

- Area of interest: map drawing (bbox and/or polygon) **or** lat/lon coordinates
- Optional simple GeoJSON upload (validate strictly; reject huge files / non-Polygon)
- Date range (`start_time` / `end_time`)
- Desired data freshness (e.g. max age days) — store in preferences JSON if no column
- Optional specific satellite/sensor preference → `data_source_preference`

**Map stack:** MapLibre (already used via HarborMap) + terra-draw **or** maplibre-gl-draw.

Validate geometry:

- Closed polygon / valid bbox
- Area within a sane max (define limit, e.g. reject continent-scale AOIs)
- Coordinates WGS84

### Step 3 — Constraints

- Deadline
- Max cost USD (optional)
- Max data volume MB (optional)
- Preferred compute location (`preferred_compute_location`)
- Allowed geographic regions (`allowed_regions`)
- Data residency requirement (part of `allowed_regions` or `customer_systems`)
- Existing cloud/infra provider (customer_systems)
- Onboard processing: required / preferred / unnecessary

Hide advanced fields under an expandable “Advanced” section.

### Step 4 — Mission context

- Title (required)
- Organization name optional (store in notes or customer_systems — no orgs table yet)
- Use case
- Technical notes (`notes`)
- Exploratory vs active mission (status or flag in JSON)

### Step 5 — Review

Show a clear summary of all inputs; confirm → `POST /v1/missions` (extend `MissionCreate` schema as needed).

## State management

- Single reducer or form store that **survives step navigation** (no lost fields when going back)
- Client validation: zod (or existing pattern)
- Server validation: Pydantic mirroring the same rules — **both sides**

## Backend changes

- Extend `MissionCreate` / `mission_to_dict` for any new fields collected
- Ensure AOI written as PostGIS polygon (existing helpers in `app/core/missions.py`)
- Return clear 422 errors for invalid geo / missing required fields
- Session cookie required (existing)

Optional after create: button to call Phase F `discover` — nice-to-have, not blocking.

## Frontend UX rules

- Simple labels; customer language
- Demo environment banner must remain visible
- Do not require account creation
- Accessible focus order; mobile usable

## Tests

Backend:

- Invalid GeoJSON / oversized AOI / missing title → 422
- Valid create → 201 + owned by session
- Cross-session cannot see new mission

Frontend:

- If no component test harness, document manual checklist in BUILD_PROGRESS; prefer minimal vitest/playwright only if already configured

## Validation

```bash
cd orbital-cortex/apps/api && ruff check app tests scripts && mypy app && pytest tests -q
cd ../web && npm run lint && npm run build
```

Regenerate OpenAPI/types after schema changes.

## Acceptance criteria

- [ ] `/plan` five-step builder works end-to-end
- [ ] Geographic input validated FE + BE
- [ ] Form state survives step navigation
- [ ] Submit creates private Mission
- [ ] No “compute job” customer language on this flow
- [ ] Tests cover validation failures
- [ ] `BUILD_PROGRESS.md` updated

## Non-goals

- Do not implement planner ranking (Phase I)
- Do not redesign homepage (Phase D)
- Do not build PDF export

## Commit message

```
feat: add guided customer-facing mission builder
```

## Stop

Next is Phase I (planning engine).
