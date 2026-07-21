# Animation Execution Plans

| Plan | Status | Severity | Dependency |
| --- | --- | --- | --- |
| [001 — Crisp Motion Foundation](001-crisp-motion-foundation.md) | DONE | High | None |
| [002 — Compositor-Friendly Network Carousel](002-compositor-friendly-network-carousel.md) | DONE | High | 001 |
| [003 — Ambient Motion Lifecycle](003-ambient-motion-lifecycle.md) | DONE | High | 001 |
| [004 — Safe Reusable Scroll Stages](004-safe-reusable-scroll-stages.md) | DONE | Medium | 001 |
| [005 — Compositor transforms and sub-300ms UI fills](005-compositor-transforms-ui-fills.md) | DONE | High | 001 |

Execute in numerical order. Every plan requires lint, production build, slow-motion
inspection, and reduced-motion verification before moving to the next plan.
