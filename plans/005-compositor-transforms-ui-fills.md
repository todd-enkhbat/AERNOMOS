# 005 — Compositor transforms and sub-300ms UI fills

- **Status:** DONE
- **Commit:** 3d6e3c9 (authored against)
- **Severity:** HIGH
- **Category:** Performance, easing & duration, cohesion

## Problem

Framer Motion `y`/`scale` shorthands ran on the main thread across homepage
FadeIns and liquid CTAs. ScoreBar (900ms) and JobStepper (600ms) exceeded the
UI duration budget. Liquid specular wrote `--x`/`--y` on the glass host,
forcing subtree style recalc under pointer move. Bare Tailwind `transition`
acted like a broad property set on color-only hovers.

## Target (shipped)

- FadeIn / StaggerItem / liquid hover-tap / Sputnik pillars use full
  `transform: "translateY(…)"` / `scale(…)` strings.
- ScoreBar fill `0.28s`; JobStepper connector `0.24s`; contact-window fill
  `0.28s` — all with strong ease-out curves already in the repo.
- Specular radial moved to `.liquid-glass__specular` + rAF-throttled
  `useLiquidMouse` writes only to `[data-liquid-specular]`.
- Rating chips and other color hovers use `transition-colors`.
- Feedback/lead success copy uses opacity-only `feedback-success-fade` (160ms).

## Verification

- `npm run lint` + `npm run build`
- Slow-mo: homepage FadeIn, liquid button press, job score bar, feedback success
- `prefers-reduced-motion`: no lift/specular; success fade disabled
