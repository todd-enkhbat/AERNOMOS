# Phase O — Privacy-safe product and planning analytics

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

Measure accelerator-relevant usage and ops health **without** recording sensitive mission content (no notes, no raw AOI polygons, no proprietary text in analytics).

## Product events (examples)

- mission_started, mission_completed
- plan_generated
- data_candidates_found (counts only)
- plan_exported, plan_shared
- example_viewed
- user_returned
- provider_connection_requested
- planning_failure_reason (enum/code only)

Store in Postgres table or structured logs + aggregate table — choose one and document schema.

## Operational metrics

- catalog provider latency / failures
- orbital-data freshness
- planner duration
- missions per status
- export failures
- share-link usage
- CPU execution success rate

## Admin

Simple internal summary endpoint (protect with shared admin token env var or local-only) — not public.

## Privacy rules

- Hash or omit session ids in exports if needed
- Never log share/session raw tokens
- Document event schemas in `orbital-cortex/docs/` or under `docs/`

## Acceptance criteria

- [ ] Events fire on key flows
- [ ] No sensitive mission content in analytics payloads
- [ ] Ops metrics observable
- [ ] Schemas documented
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
feat: add privacy-safe product and planning analytics
```

## Stop

Next is Phase P.
