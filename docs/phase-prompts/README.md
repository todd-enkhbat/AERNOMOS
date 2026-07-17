# Nomos phase prompts (copy-paste agent instructions)

Phases **A–C are done**. Use these files as **standalone agent prompts** for the remaining work.

## How to use

1. Open [`docs/BUILD_PROGRESS.md`](../BUILD_PROGRESS.md) and confirm the current phase.
2. Open the matching file below.
3. Copy the **entire** file into a new Cursor chat (or agent run).
4. Do **not** paste more than one phase at a time.
5. After the phase passes acceptance criteria, update `BUILD_PROGRESS.md` and commit with the message in the prompt (only if you asked the agent to commit).

## Canonical order (do not skip ahead)

| Step | File | Phase | Commit message |
| --- | --- | --- | --- |
| 4 | [`04-phase-F-stac-catalog.md`](04-phase-F-stac-catalog.md) | F — STAC discovery | `feat: integrate real STAC satellite data discovery` |
| 5 | [`05-phase-H-orbital-provenance.md`](05-phase-H-orbital-provenance.md) | H — Orbital provenance | `feat: add fresh orbital data provenance and mission-specific infrastructure` |
| 6 | [`06-phase-G-truth-ui.md`](06-phase-G-truth-ui.md) | G — Truth-status UI | `feat: add source provenance and truth-status labeling` |
| 7 | [`07-phase-E-mission-builder.md`](07-phase-E-mission-builder.md) | E — Guided builder | `feat: add guided customer-facing mission builder` |
| 8 | [`08-phase-I-planning-engine.md`](08-phase-I-planning-engine.md) | I — Planning engine | `feat: build source-backed mission feasibility and planning engine` |
| 9 | [`09-phase-J-mission-result.md`](09-phase-J-mission-result.md) | J — Result page | `feat: replace simulated job output with customer mission brief` |
| 10 | [`10-phase-D-homepage.md`](10-phase-D-homepage.md) | D — Homepage | `feat: simplify homepage around mission planning outcomes` |
| 11 | [`11-phase-K-exports-sharing.md`](11-phase-K-exports-sharing.md) | K — PDF/JSON/share | `feat: add mission brief PDF JSON and private sharing` |
| 12 | [`12-phase-L-isolate-simulations.md`](12-phase-L-isolate-simulations.md) | L — Examples only | `refactor: isolate simulations into clearly labeled examples` |
| 13 | [`13-phase-M-cpu-execution.md`](13-phase-M-cpu-execution.md) | M — CPU execution | `feat: add lightweight real CPU execution provider` |
| 14 | [`14-phase-N-provider-registry.md`](14-phase-N-provider-registry.md) | N — Provider registry | `feat: add extensible infrastructure provider registry` |
| 15 | [`15-phase-O-analytics.md`](15-phase-O-analytics.md) | O — Analytics | `feat: add privacy-safe product and planning analytics` |
| 16 | [`16-phase-P-feedback-leads.md`](16-phase-P-feedback-leads.md) | P — Feedback / leads | `feat: add mission feedback and design partner requests` |
| 17 | [`17-phase-Q-docs-sdk.md`](17-phase-Q-docs-sdk.md) | Q — Docs + SDK | `docs: document mission planner APIs data sources and limitations` |
| 18 | [`18-phase-R-accelerator-demos.md`](18-phase-R-accelerator-demos.md) | R — Accelerator demos | `feat: add accelerator-ready mission planning demos` |
| 19 | [`19-phase-S-security-review.md`](19-phase-S-security-review.md) | S — Security | `security: harden private mission planning workflow` |
| 20 | [`20-phase-T-final-validation.md`](20-phase-T-final-validation.md) | T — Final validation | `chore: complete mission planner validation and release documentation` |

Master overview (not a phase prompt): [`docs/NOMOS_BUILD_PLAN.md`](../NOMOS_BUILD_PLAN.md).

## Already completed (do not re-run)

| Phase | What exists |
| --- | --- |
| A | `orbital-cortex/docs/current-system-audit.md` |
| B | `app/db/mission_orm.py`, `app/db/truth.py`, Alembic mission tables, UUID PKs, `TruthStatus` enum |
| C | Anonymous sessions, share links, `/missions`, demo banner, jobs list curated to `is_example` only |

## Global rules every prompt already includes

- Inspect before editing; reuse architecture; keep legacy Job demo until Phase L.
- Never fabricate data; every important number needs a truth status.
- After API schema changes: export OpenAPI + regenerate web types.
- Update `docs/BUILD_PROGRESS.md` before declaring the phase done.
- Stop after **this** phase — do not start the next one.
