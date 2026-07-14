# Design Engineering Workflow

Use this with the visual direction in [`SOUL.md`](../../SOUL.md). It turns the
installed design-engineering skills into project-specific quality gates.

## Before editing

1. Name the user goal and the emotion: calm, confident, and technically credible.
2. Identify the primary action and proof. The first viewport must make both obvious.
3. Decide why each visual or animation exists: explanation, state, feedback, spatial
   continuity, or preventing a jarring change. Remove motion with no purpose.
4. Inspect the surrounding sections in the browser. Do not design a component in
   isolation from the page rhythm.

## Composition and imagery

- Simplicity is not emptiness. Use hierarchy, grouping, and concise context instead
  of oversized blank intervals.
- Every major section needs a visual anchor, product proof, or meaningful transition.
  Decorative space alone does not earn a viewport.
- Generated artwork must be visibly used, named for its role, cropped intentionally,
  and paired with real content. Do not hide new artwork behind WebGL or use it only as
  an error fallback.
- Preserve semantic ownership: the spinning Golden Record belongs to the About story;
  the network uses satellite and routing imagery.
- Use one dominant image per visual beat. Keep text contrast high with directional
  gradients rather than flattening the image under a heavy uniform overlay.
- Proximity communicates relationship. Keep captions, controls, and evidence next to
  what they explain.
- Large headings use tight leading and slightly negative tracking; body copy uses
  comfortable leading. Text and spacing must survive browser text scaling.

## Interaction and motion

- Feedback begins on pointer-down. Pressable controls use subtle `scale(0.97)` feedback
  around 100–160 ms.
- UI entrances and exits use strong ease-out; on-screen movement uses ease-in-out;
  ambient constant rotation uses linear motion. Never use ease-in for UI response.
- Keep routine UI motion under 300 ms. Longer motion is reserved for explanatory,
  first-time storytelling.
- Use critically damped, interruptible springs for gesture-driven movement. Add bounce
  only when the gesture carries momentum.
- Animate `transform` and `opacity`; avoid animating layout dimensions and spacing.
- Use CSS for predetermined motion and JavaScript only when motion is dynamic,
  scroll-linked, or interruptible.
- Reduced motion keeps useful fades and color feedback while removing parallax,
  tumbling, overshoot, and large positional movement.
- Gate hover-only movement behind `(hover: hover) and (pointer: fine)`.
- Enter and exit through the same spatial path and anchor popovers to their trigger.

House curves:

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

## Verification loop

1. Build and lint.
2. Review the complete page at desktop and mobile widths, not only the edited crop.
3. Check section-to-section rhythm for accidental empty bands and sticky-stage gaps.
4. Verify image loading, intended crops, WebGL fallback, and slow connections.
5. Verify keyboard navigation, focus, touch behavior, reduced motion, and contrast.
6. Inspect uncertain motion in slow motion or frame-by-frame.
7. Revisit high-impact motion with fresh eyes before release.

## Cursor skills

The supplied `emilkowalski/skills` package is installed in the user's Cursor skills
directory. Apply these when relevant:

- `emil-design-eng` for UI implementation and detailed design review
- `apple-design` for fluid interaction, hierarchy, materials, typography, and access
- `animation-vocabulary` when specifying motion precisely
- `review-animations` for strict review of changed motion
- `improve-animations` for a codebase-wide audit and executable plans

Source: Emil Kowalski, *Skills for Design Engineers* (MIT License).
