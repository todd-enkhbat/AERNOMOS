# Phase R — Accelerator-ready curated demos

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

Three reliable demos for accelerator conversations, plus a finished 90-second script. No hidden manual DB edits.

## Demo 1 — Existing Sentinel imagery

Inputs: New York Harbor, recent Sentinel-1, deadline, U.S. data residency  
Output: real candidates, recommended route, real scene metadata, calculated planning, clear unavailable onboard option

## Demo 2 — Disaster response

Urgent deadline; compare existing imagery vs new acquisition vs cloud processing  
Output: feasibility comparison, assumptions, timeline, next actions

## Demo 3 — Customer edge processing

Real scene + customer-controlled CPU preference  
Output: cloud vs edge comparison, **one real lightweight CPU execution** (Phase M), measured duration, artifact

## Delivery

- Seed/reset scripts (extend `app.seed` and `demo-reset.yml`)
- Each demo: reset instructions in docs
- Every simulated step disclosed
- Finish `docs/accelerator-demo-script.md` or `orbital-cortex/docs/accelerator-demo-script.md` covering:

1. Customer problem  
2. Mission input  
3. Real data discovery  
4. Real orbital/infrastructure calculation  
5. Feasible + rejected plans  
6. Recommendation  
7. Truth labels  
8. Exported report  
9. Clear next provider integration  

## Acceptance criteria

- [ ] Each demo runs reliably from seed
- [ ] No manual DB surgery required
- [ ] Disclosures complete
- [ ] 90s script finished
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
feat: add accelerator-ready mission planning demos
```

## Stop

Next is Phase S.
