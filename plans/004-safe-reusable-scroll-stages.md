# 004 — Make Reusable Scroll Stages Safe Before Reuse

- **Status:** DONE
- **Commit:** b551b82
- **Severity:** MEDIUM
- **Category:** Accessibility and cohesion
- **Estimated scope:** 2 files

## Problem

The dormant reusable scroll stages hard-code sticky offsets and unconditionally
apply scroll-driven transforms. Reusing them would create header overlap and
reduced-motion regressions.

```tsx
// orbital-cortex/apps/web/components/motion/ScrollSketchfab.tsx:32
<div className="sticky top-[72px] flex h-[min(72vh,640px)] items-center justify-center">
```

## Target

- Use `top: var(--header-offset)` for sticky stages.
- Honor `useReducedMotion()` by retaining content and opacity while dropping
  scroll-driven translation, scaling, and rotation.
- Avoid pinned empty space on mobile.

## Steps

1. Add `useReducedMotion()` to `OrbitalScrollStage` and `ScrollSketchfab`.
2. Branch their style transforms to static values when reduced motion is enabled.
3. Replace fixed sticky offsets with the header-offset token.
4. Retain current responsive heights only where the component is actually
   mounted; if still unused, leave removal as a separate explicit decision.

## Boundaries

- Do not mount these components on any page.
- Do not remove dormant components without explicit approval.

## Verification

- Test a simulated mobile width and reduced-motion setting.
- Confirm sticky stages align beneath the responsive header offset.
- Run lint and build.
