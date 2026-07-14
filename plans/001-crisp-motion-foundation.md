# 001 — Establish a Crisp Motion Foundation

- **Status:** DONE
- **Commit:** b551b82
- **Severity:** HIGH
- **Category:** Easing, physicality, accessibility, cohesion
- **Estimated scope:** 4 files

## Problem

`globals.css` uses several generic `ease` transitions, and the liquid primitives
combine large hover lift/scale with spring values intended for richer gestures.
Touch devices can receive hover-style effects, and reduced motion removes all
transition feedback rather than only movement.

```tsx
// orbital-cortex/apps/web/components/liquid/LiquidButton.tsx:51
whileHover: reduced || disabled ? undefined : { y: -5, scale: 1.03, transition: spring },
whileTap: reduced || disabled ? undefined : { y: 1, scale: 0.97, transition: spring },
```

## Target

- Add `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)` and
  `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)` to the root tokens.
- Gate CSS hover lift and glow behind `(hover: hover) and (pointer: fine)`.
- Use a critically damped 160 ms-equivalent press response at `scale(0.97)`;
  routine hover lift is subtle (`translateY(-2px)`, no scale).
- Reduced motion retains color and opacity feedback, but removes lift and scale.

## Steps

1. Add the two shared easing tokens in `orbital-cortex/apps/web/app/globals.css`.
2. Replace generic interaction curves in liquid CSS with exact property-specific
   transitions using the new tokens.
3. Move liquid hover rules into a fine-pointer media query; add reduced-motion
   overrides that retain border/color changes but remove transforms.
4. Update `LiquidButton`, `LiquidCard`, and `LiquidChip` to use their restrained
   hover/press behavior and skip hover transforms on coarse pointers.

## Boundaries

- Do not change liquid component markup or visual tokens.
- Do not add dependencies.
- Do not add bounce to controls.

## Verification

- `npm --prefix orbital-cortex/apps/web run lint`
- In a desktop browser, press and release primary, outline, and chip controls:
  press scales to 0.97 immediately and release remains crisp.
- In reduced motion, confirm color feedback remains and controls do not lift.
- Test a touch viewport: no persistent hover transform after a tap.
