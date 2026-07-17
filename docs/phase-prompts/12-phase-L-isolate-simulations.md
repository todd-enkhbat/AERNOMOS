# Phase L — Isolate simulations into clearly labeled examples

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

No user should reasonably mistake simulated execution for real execution. Curated examples remain compelling. The main customer path produces a **mission plan**, not fake detections.

## Required work

### 1. Audit user-facing simulated output

Find and demote/remove from the **primary** customer path:

- Fabricated ship detections / confidence as “results”
- Arbitrary confidence scores presented as observed
- Fictional provider prices / node availability as live
- Fictional onboard completion states
- Random job result maps as the mission outcome

Keep simulations **only** as curated examples, always labeled `SIMULATED`.

### 2. Curated examples at `/examples`

Build `/examples` listing cards that link to public `is_example` missions (and/or static narrative pages).

Suggested examples:

- Maritime monitoring
- Wildfire response
- Disaster imagery delivery
- Customer edge processing

Each example must state explicitly:

- which data is real
- which calculations are real
- which steps are estimated
- which steps are simulated
- which provider integrations are unavailable

### 3. Legacy Job demo

- `/jobs` and DemoLauncher become an **explicitly labeled example** (“Historical simulation demo”) — not the main CTA
- `mock_inference.py` may remain for that path but UI must scream SIMULATED
- Update `.github/workflows/demo-reset.yml` to **seed curated example missions** and never delete them

### 4. Docs soul update

Update in the same commit:

- `SOUL.md`
- `orbital-cortex/docs/capability-truth.md`
- `docs/BUILD_PROGRESS.md`

## Acceptance criteria

- [ ] Customer mission flow does not present fake detections as real output
- [ ] Examples exist with real/sim disclosures
- [ ] Legacy demo labeled and demoted
- [ ] demo-reset seeds examples safely
- [ ] Builds/tests pass

## Commit message

```
refactor: isolate simulations into clearly labeled examples
```

## Stop

Next is Phase M.
