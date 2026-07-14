# 002 — Make the Network Carousel Compositor-Friendly

- **Status:** DONE
- **Commit:** b551b82
- **Severity:** HIGH
- **Category:** Performance and continuity
- **Estimated scope:** 1 file

## Problem

The Network carousel changes active card width and height while selecting a
slide, moves the track with Framer Motion `x`, and animates a brightness filter.
Those choices cause layout/paint work during repeated navigation.

```tsx
// orbital-cortex/apps/web/components/network/NetworkMetricsCarousel.tsx:140
animate={{ x: offset }}
// :181
width: isActive ? "min(78vw, 860px)" : "min(34vw, 300px)",
height: isActive ? "min(52vh, 500px)" : "min(40vh, 360px)"
```

## Target

- Keep a stable card geometry at each responsive breakpoint.
- Move the track with an explicit `transform: translateX(...)` value.
- Emphasize the selected card with transform and opacity only.
- Preserve keyboard, click, screen-reader, and reduced-motion behavior.

## Steps

1. Replace selection-dependent inline width and height with stable responsive
   dimensions for all slides.
2. Drive the track from an explicit transform string, retaining the existing
   critically damped spring for pointer-initiated selection.
3. Replace filter animation with opacity plus a static overlay treatment.
4. Use transform-only active-card emphasis; remove layout-affecting animation.

## Boundaries

- Do not change slide content, copy, images, or navigation semantics.
- Do not change the `go` bounds behavior.

## Verification

- Rapidly select every slide by click and Arrow keys: no card reflow or jump.
- At 10% animation speed, the track moves continuously and selected emphasis
  does not double-expose cards.
- Toggle reduced motion: card selection updates without transform motion.
- Run lint and a production build.
