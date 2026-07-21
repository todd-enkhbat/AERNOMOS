# Phase D — Simplify homepage around mission planning outcomes

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Prerequisites

- `/plan` (Phase E) and meaningful `/missions/[id]` (Phase J) exist so CTAs are not dead ends
- `/examples` may still be a stub until Phase L — secondary CTA can go to `/examples` with a simple placeholder page if missing

## Product goal

A non-technical visitor understands Nomos in ~5 seconds. No false execution claims. Primary CTA starts the private mission workflow.

## Required homepage content

### Hero

**Headline (use this or extremely close):**

> Plan how your space-data workload should move across satellite, ground, and cloud infrastructure.

**Subheadline:**

> Describe your mission and constraints. Nomos generates a source-backed execution plan using real orbital and infrastructure data.

**Primary CTA:** Build a mission plan → `/plan`  
**Secondary CTA:** View example plan → `/examples` (or first public example mission)

Keep visual identity: `OrbitalScene`, `NomosMark`, fonts — but **readability > decorative complexity**. Hero budget: brand, one headline, one subhead, CTAs, one dominant visual. No stat strips / fake metrics in the first viewport.

### Three steps

1. Describe the mission  
2. Nomos evaluates real data and infrastructure  
3. Receive a traceable recommended plan  

### Section: “What Nomos does today”

Must clearly state:

- searches real public data catalogs
- calculates satellite and ground contact opportunities
- compares feasible infrastructure routes
- labels assumptions and unavailable integrations
- generates a technical mission brief

### Section: “What requires provider integration”

Must clearly state:

- satellite tasking
- ground-station reservation
- onboard execution
- private telemetry
- commercial pricing guarantees

### Language to remove or demote from the homepage hero/first screen

Do **not** lead with:

- orchestration layer
- deterministic routing
- control plane
- compliance-aware infrastructure
- autonomous orbital intelligence
- multi-domain workload placement

Those may remain in `/docs` or deep technical sections only.

### DemoLauncher / Job CTA

- Demote “Run demo” / job submit as secondary or move to examples later (Phase L finishes isolation)
- Do not delete the Job API; just stop making it the homepage primary action

## Canonical docs to update **in the same commit**

These are product-soul files — update them to match the new homepage claims:

- `SOUL.md` (positioning / demo truth / homepage-facing language)
- `orbital-cortex/docs/capability-truth.md`
- Optionally a short note in `AGENTS.md` phase status if it still describes old homepage positioning

## Acceptance criteria

- [ ] Nontechnical reader understands the product from the homepage
- [ ] No false execution claims
- [ ] Primary CTA → `/plan`
- [ ] “Does today” vs “requires provider” sections accurate
- [ ] SOUL + capability-truth updated
- [ ] `npm run lint` + `npm run build` pass
- [ ] `BUILD_PROGRESS.md` updated

## Non-goals

- Do not implement exports (K) or full examples library (L) beyond a stub `/examples` page if needed for the CTA
- Do not redesign the entire site chrome

## Commit message

```
feat: simplify homepage around mission planning outcomes
```

## Stop

Next is Phase K.
