# Phase J — Mission result experience (`/missions/[id]`)

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- Phase I planner APIs return plans/steps/evidence
- Phase G truth components exist — **use them**

## Product goal

Redesign `/missions/[id]` so the **recommendation is the dominant element**. Remove fake detections as the main output of this page. A technical customer should understand the plan without reading docs.

## Page sections (all required)

### 1. Executive recommendation

Example tone:

> Recommended plan: existing imagery to U.S. cloud processing

Explain:

- Why recommended
- Whether executable now
- Assumptions used
- Missing integrations

### 2. Feasibility summary

Buckets: feasible now / feasible with provider access / estimated only / unavailable

### 3. Mission timeline

Ordered steps with start, duration, truth badge, provider, dependency, availability

### 4. Geographic visualization

Mission-scoped only:

- AOI
- Selected scene footprint(s)
- Relevant satellite track (if available)
- Candidate ground stations
- Communication windows
- Destination region

Reuse/adapt `NetworkGlobeMap`, `ContactWindowTimeline`, MapLibre — **do not** dump unrelated fleet.

### 5. Alternative plans table

Columns: plan, feasibility, est. time, est. cost, data movement, access required, key reason

### 6. Assumptions and sources

Source list, retrieval timestamps, orbital snapshot epoch, pricing assumptions, unavailable integrations, stale inputs — use `AssumptionPanel` + `SourcePopover`

### 7. Next actions

Practical checklist, e.g.:

- Connect provider account
- Request ground-station access
- Upload payload capabilities
- Confirm data residency
- Export plan (stub link OK until Phase K)
- Share with engineering team (stub until K)

### 8. Demo disclosure (always visible)

> This mission plan uses real public orbital and catalog data where available. Satellite tasking, provider reservation, onboard execution, and commercial guarantees are not performed unless explicitly marked as connected.

## UX rules

- Recommendation = primary visual hierarchy
- No random simulated ship detections as the hero output
- Truth badges on every important number
- Works on mobile + desktop; keep Nomos visual identity
- Customer language throughout

## Data loading

- Fetch mission, candidates, plans, steps, evidence, infrastructure snapshot via existing APIs
- Empty states: no plans yet → CTA “Generate plan” calling Phase I endpoint
- Loading and error states clear

## Tests / QA

- Document responsive + a11y smoke in BUILD_PROGRESS
- `npm run lint` + `npm run build` must pass

## Acceptance criteria

- [ ] All 8 sections present and understandable
- [ ] Recommendation dominant; alternatives comparable
- [ ] Sources/assumptions inspectable
- [ ] No fake detections as main output
- [ ] Demo disclosure visible
- [ ] `BUILD_PROGRESS.md` updated

## Non-goals

- Do not rewrite marketing homepage (Phase D) beyond fixing links to this page if broken
- Do not implement PDF generation (Phase K) — buttons may say “Export coming soon” or call a 501 stub briefly; prefer honest disabled button with note

## Commit message

```
feat: replace simulated job output with customer mission brief
```

## Stop

Next is Phase D (homepage rewrite).
