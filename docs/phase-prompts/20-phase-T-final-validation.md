# Phase T — Final validation and release documentation

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

Prove the private mission flow works end-to-end, document reality vs simulation, and leave deployable release notes. Produce `docs/final-validation-report.md`.

## Automated suite (run and record)

### Backend

- ruff, mypy, pytest
- migrations from empty DB
- migrations from current demo DB
- API contract / authz / planner / catalog / export / execution tests

### Frontend

- lint, typecheck, production build
- responsive + a11y smoke notes
- mission builder, result, share, examples

### Infrastructure

- Docker build
- docker-compose startup
- health + readiness
- object storage, Redis worker, migrations
- scheduled TLE refresh / demo cleanup as applicable

## Manual acceptance flow (verify and check off)

1. Open homepage — understand in ~5s  
2. Create private anonymous mission  
3. Search real satellite data  
4. Generate multiple plans  
5. See rejected routes + reasons  
6. See truth labels + sources  
7. Export PDF + JSON  
8. Create private share link  
9. Open share in another browser profile  
10. Confirm unrelated missions inaccessible  
11. Execute one lightweight CPU step  
12. See measured OBSERVED values  
13. Submit feedback  
14. Request design-partner contact  
15. Confirm no false tasking/reservation/onboard claims  

## Final claim (allowed)

> Nomos turns a space-data objective into a source-backed infrastructure plan. It searches real public data catalogs, calculates orbital and communication constraints, compares feasible execution paths, explains assumptions, and produces a shareable technical mission brief.

## Forbidden claims (must not appear)

- AI ran onboard a satellite  
- Satellite was tasked  
- Ground station reserved  
- Commercial pricing guaranteed  
- Private provider availability is live  
- Execution occurred unless a real adapter completed it  

## `final-validation-report.md` must include

- completed features  
- tests run  
- known limitations  
- remaining simulations  
- unavailable integrations  
- local run instructions  
- deploy instructions  
- accelerator demo instructions  
- highest-priority next provider integration  

Align `SOUL.md`, `AGENTS.md`, `capability-truth.md` with the allowed claim.

## Deploy

Deploy only if the user explicitly asks; otherwise document the deploy steps and leave artifacts ready. Do not block on GPU, tasking, billing, or full org auth.

## Acceptance criteria

- [ ] All completion conditions from the master plan satisfied
- [ ] Report written
- [ ] Soul/docs aligned
- [ ] Concise final summary produced for the user

## Commit message

```
chore: complete mission planner validation and release documentation
```

## Stop

This is the last phase. After it, summarize what is real vs simulated and how to demo.
