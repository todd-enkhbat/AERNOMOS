# 003 — Add an Ambient Motion Lifecycle

- **Status:** DONE
- **Commit:** b551b82
- **Severity:** HIGH
- **Category:** Performance and accessibility
- **Estimated scope:** 2 files

## Problem

The Harbor map highlight pulse continues its requestAnimationFrame loop until
unmount. The reusable Golden Record scene runs an unrestricted WebGL loop and
does not honor reduced motion.

```tsx
// orbital-cortex/apps/web/components/HarborMap.tsx:286
const tick = () => {
  // ...
  raf = requestAnimationFrame(tick);
};
```

## Target

- Pause ambient RAF work when the component is off-screen or the page is hidden.
- Resume from present state rather than recreating the animation.
- In reduced motion, render a static, meaningful Golden Record frame.
- Preserve the Golden Record’s ownership in About; never use it as a Network fallback.

## Steps

1. Add visibility and document-visibility state to the Harbor map pulse effect;
   request frames only when the map is visible, pulse is enabled, and reduced
   motion is off.
2. Add the same lifecycle guard to `GoldenRecordSphere`.
3. Branch record rotation/tilt and label/glow transforms for
   `useReducedMotion()`, retaining a static rendered disc.
4. Clean up observers and `visibilitychange` listeners on unmount.

## Boundaries

- Do not change map controls, baseline map data, About copy, or record artwork.
- Do not introduce a global animation loop or new dependency.

## Verification

- Navigate away or background the tab: RAF work stops.
- Scroll each surface outside the viewport, then return: visual state resumes
  without a reset or blank canvas.
- Enable reduced motion: map pulse and record rotation stop while content remains legible.
- Run lint and build.
