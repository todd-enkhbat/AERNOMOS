# 006 — Homepage scroll section rhythm

- **Status**: DONE
- **Commit**: cd47ba8
- **Severity**: HIGH
- **Category**: Purpose & frequency / Missed opportunities (jarring scroll seams)
- **Estimated scope**: 3 files (`page.tsx`, `primitives.tsx`, `globals.css`)

## Problem

Homepage scroll feels awkward: large empty blue bands between sections, late
`FadeIn` entrances, and hard blue↔parchment color flips.

Evidence:

```tsx
// orbital-cortex/apps/web/components/motion/primitives.tsx:32-46 — current
const hidden = { opacity: 0, transform: `translateY(${y}px)` };
// default y = 12
viewport: { once: true, margin: "-40px", amount: 0.15 },
```

```css
/* orbital-cortex/apps/web/app/globals.css:132-134 — current */
.section-gap {
  margin-top: 4rem;
}
```

```tsx
// orbital-cortex/apps/web/app/page.tsx — LiquidSection mt-4 then parchment with section-gap
<LiquidSection className="mt-4 page-shell">...</LiquidSection>
<section className="klein-parchment-band section-gap ...">
```

The `-40px` viewport margin delays whileInView until content is already 40px
into the viewport, so users scroll through empty space before copy appears.
Combined with `translateY(12px)` and `4rem` gaps, section transitions feel
disconnected rather than continuous.

## Target

1. Homepage section FadeIns use a short travel (`y={6}`) and a looser trigger
   (`viewport.margin: "0px 0px -8% 0px"` or `amount: 0.05` with `margin: "0px"`)
   so content begins entering as it approaches the viewport.
2. Homepage vertical rhythm uses a shared compact gap (`2.5rem` desktop /
   `2rem` mobile) instead of `section-gap` 4rem between hero → steps → parchment.
3. Soft bridge gradients at the hero bottom and parchment top/bottom so color
   bands do not hard-cut.
4. Keep motion under 300ms feel via existing `springSoft`; reduced motion still
   skips translate, keeps opacity.

```tsx
// target homepage usage
<FadeIn y={6} viewportMargin="0px">...</FadeIn>
```

```css
/* target */
.home-band {
  margin-top: 2.5rem;
}
.philosophy-hero::after {
  /* soft fade into next blue band */
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 4.5rem;
  pointer-events: none;
  background: linear-gradient(to bottom, transparent, var(--klein-deep));
}
```

## Repo conventions to follow

- Easing / springs live in `orbital-cortex/apps/web/components/motion/primitives.tsx`
  (`springSoft`) and CSS tokens `--ease-out` / `--ease-in-out` in `globals.css`.
- Prefer full transform strings (`transform: "translateY(...)"`), not Framer `y`.
- Exemplar of mount-time hero motion already using `when="mount"`:
  `orbital-cortex/apps/web/app/page.tsx` hero FadeIns.

## Steps

1. In `primitives.tsx`, add optional `viewportMargin?: string` (default keep
   current `"-40px"` for other pages). Homepage passes `"0px"`.
2. On homepage scroll sections (steps, parchment, demo), set `y={6}` and
   `viewportMargin="0px"`. Keep hero at `when="mount"`.
3. Replace homepage `section-gap` / loose `mt-4` with `.home-band` (2.5rem).
4. Add `.philosophy-hero__bridge` bottom fade and soften parchment band edges
   with 1px hairlines or short gradient masks — do not animate layout height.
5. Do not change About/Network sticky scroll stages in this plan.

## Boundaries

- Do NOT touch `OrbitalScrollStage`, `ScrollSketchfab`, `ImmersiveScrollBand`,
  About/Network story stages.
- Do NOT add new motion libraries.
- Do NOT animate `margin`, `height`, or `padding` for the bridges — static
  gradients only.
- If file drift prevents matching these excerpts, STOP and report.

## Verification

- **Mechanical**: from `orbital-cortex/apps/web`, run lint/typecheck on touched
  files; `npm run build` must succeed.
- **Feel check**:
  - Scroll homepage at normal speed: each section’s copy should begin fading in
    as it enters, not after a blank pause.
  - In DevTools Animations panel at 10% speed, FadeIn travel should be a short
    upward settle (≈6px), not a 12px hop.
  - Toggle `prefers-reduced-motion: reduce` — no translate, opacity may remain.
  - Confirm no large empty blue strip between hero and “How it works”.
- **Done when**: homepage scroll has continuous section rhythm with soft color
  bridges and early FadeIn triggers; other pages unchanged by default FadeIn
  margin.
