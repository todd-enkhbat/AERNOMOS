# Phase L — Isolate simulations into clearly labeled examples

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

Commit only if the user explicitly asks for a commit; if committing, use:

```
refactor: isolate simulations into clearly labeled examples
```

## Read first

- `AGENTS.md`
- `SOUL.md`
- `docs/NOMOS_BUILD_PLAN.md`
- `docs/BUILD_PROGRESS.md`
- `orbital-cortex/docs/capability-truth.md`
- `orbital-cortex/docs/current-system-audit.md`

Confirm current phase is L before editing.

## Product goal

No user should reasonably mistake simulated execution for real execution. The primary customer path is private mission planning: `/plan` → `/missions/[id]` → export/share. Curated examples remain compelling, but every simulated value is explicitly marked `SIMULATED` and explained. The legacy Job demo remains available only as a clearly labeled historical simulation demo.

## Existing context to reuse

- `/examples` already exists as a placeholder at `orbital-cortex/apps/web/app/examples/page.tsx`.
- Public example missions already have an API path: `GET /v1/missions/examples`.
- Frontend already has `listExampleMissions()` in `orbital-cortex/apps/web/lib/api.ts`.
- Curated examples use `Mission.is_example=true` and `EXAMPLES_ORGANIZATION_ID`.
- `ensure_example_mission()` currently seeds one thin example mission; expand into a real curated examples seed.
- `demo-reset` currently runs `python -m app.seed --reset --force`; make reset safe for curated examples.
- Phase J already removed fake detections from the mission brief; preserve that.
- Phase M is next (real CPU execution). Do **not** add execution providers now.

## Required work

### 1. Audit and isolate simulated output

Search user-facing API, web, docs, and seed code. At minimum inspect:

- Homepage, layout metadata, `/examples`, `/jobs`, job detail, `DemoLauncher`
- `DetectionPanel`, `SdkResultPreview`, `NetworkConsole`
- `mock_inference.py`, storage/missions seed helpers, `demo-reset.yml`
- `SOUL.md`, `capability-truth.md`

Remove, demote, or relabel from the **primary** customer path:

- Fabricated ship detections / confidence as product results
- Arbitrary confidence scores presented as observed
- Fictional provider prices / node availability as live
- Fictional onboard completion states
- Random job result maps as a mission outcome

Any remaining simulation must:

1. Be labeled `SIMULATED` near the value or section
2. Explain why it exists
3. Never be mixed with real values without distinction
4. Never appear to be customer-specific real output

### 2. Curated examples at `/examples`

Replace the placeholder `/examples` page with a polished library that fetches public `is_example` missions and renders cards.

Every example card (or linked detail) must disclose:

- which data is real
- which calculations are real
- which steps are estimated
- which steps are simulated
- which provider integrations are unavailable

Seed **at least four** curated public examples:

- Maritime monitoring
- Wildfire response
- Disaster imagery delivery
- Customer edge processing

Prefer real `is_example` mission records with stable titles, AOIs, objectives, and structured disclosure metadata in `customer_systems` / notes. Do **not** fabricate provider execution, pricing, live detections, or live availability.

### 3. Legacy Job demo

- `/jobs` and `DemoLauncher` become an **explicitly labeled example** (“Historical simulation demo”) — not the main CTA
- `mock_inference.py` may remain for that path but UI must scream `SIMULATED`
- Detection confidence must read as simulated/demo confidence, not observed
- Homepage / primary CTA remain `/plan` and `/examples`
- Do **not** delete the Job demo, router, replay, or mock inference pipeline

### 4. Make demo-reset safe

Update `.github/workflows/demo-reset.yml` and seed/reset code so nightly reset:

- May delete visitor-submitted jobs
- Must **not** delete curated example missions (`is_example=true`)
- Must idempotently upsert curated example missions
- Curated example jobs must be preserved or recreated deterministically

Add tests for seed idempotency and reset behavior around examples.

### 5. Docs soul update

Update in the same change set:

- `SOUL.md`
- `orbital-cortex/docs/capability-truth.md`
- `docs/BUILD_PROGRESS.md`

## Tests / validation

- API tests: example listing, private isolation, seed idempotency, reset preserves/reseeds examples
- `pytest tests -q` in `orbital-cortex/apps/api`
- `ruff check app tests scripts`
- `npm run lint` + `npm run build` in `orbital-cortex/apps/web`
- If API schemas change: export OpenAPI + regenerate web types

## Acceptance criteria

- [ ] Customer mission flow does not present fake detections as real output
- [ ] `/examples` is a useful curated library (not a placeholder) with real/sim disclosures
- [ ] Legacy `/jobs` and DemoLauncher labeled and demoted as historical simulation demo
- [ ] Simulated detection/confidence UI clearly says simulated/demo
- [ ] demo-reset seeds examples safely and does not erase curated example missions
- [ ] Docs updated; builds/tests pass
- [ ] `BUILD_PROGRESS.md` records work, files, tests, issues, decisions, next phase

## Commit message

```
refactor: isolate simulations into clearly labeled examples
```

## Stop

Next is Phase M. Do not start it.
