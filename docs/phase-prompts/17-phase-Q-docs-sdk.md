# Phase Q — Documentation and Python SDK for missions

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Docs to create (under `orbital-cortex/docs/` or `docs/` — be consistent; prefer `orbital-cortex/docs/` for product engineering docs and link from AGENTS.md)

Create or flesh out:

- `mission-planner-overview.md`
- `data-sources.md`
- `truth-statuses.md`
- `planning-engine.md`
- `privacy-model.md`
- `provider-integrations.md`
- `demo-limitations.md`
- `accelerator-demo-script.md` (skeleton OK; Phase R finishes the 90s script)

Each must clearly separate real vs simulated vs unavailable.

## SDK (`orbital-cortex/sdk/python`)

Add customer-friendly API:

```python
mission = client.missions.create(...)
plan = client.missions.generate_plan(mission.id)
report = client.missions.export_pdf(mission.id)
```

Typed errors for:

- no catalog data
- no feasible plan
- upstream provider unavailable
- unauthorized mission
- expired share link
- stale orbital data
- invalid geographic input

SDK must not force users to understand ORM models. Regenerate OpenAPI-based client pieces if that is the repo pattern.

Update `AGENTS.md` key docs table + phase status blurb.

## Acceptance criteria

- [ ] Short SDK example works against local/API
- [ ] Docs explain real vs simulated
- [ ] Public examples use customer terminology
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
docs: document mission planner APIs data sources and limitations
```

## Stop

Next is Phase R.
