# Nomos Orbital Design System

This file is the visual implementation contract for Nomos Orbital. `SOUL.md`
remains the source of truth for product positioning, language, and the larger
brand world. This document turns that direction into repeatable interface rules.

## Design read

Nomos is a technical space-infrastructure product for operators, developers,
partners, and investors. It should feel calm, cinematic, exact, and credible.
The interface is an orbital field manual, not a generic AI SaaS template.

Working dials:

- Design variance: 6/10. Use controlled asymmetry, never visual chaos.
- Motion intensity: 4/10. Motion explains hierarchy, state, or causality.
- Visual density: 4/10. Product proof is detailed, but each viewport has one job.

## Sources of truth

1. The homepage hero establishes the primary marketing grammar.
2. Real product surfaces establish the proof grammar.
3. `SOUL.md` controls voice, claims, truth labels, and brand meaning.
4. External design skills are audit frameworks. They do not replace this system.

## Visual grammar

- Use a dark, blue-tinted orbital field as the default marketing canvas.
- Use real mission imagery, sourced archive material, and real product proof at
  large scale. Do not fill space with decorative cards or fake dashboards.
- Use one dominant visual per section.
- Brass marks active signal, selection, or the recommended route. It is not a
  general decoration color.
- Fine dividers organize real content. Do not add grids or crosshairs that carry
  no information.
- Keep every website route inside the dark Nomos field. Parchment may appear in
  exported documents or isolated reading artifacts, not as an inverted page section.

## Color roles

- Deep canvas: `#02050d`
- Nomos blue: `#002fa7`
- Deep blue: `#001045`
- Primary text: `#f2eee4`
- Secondary text: `#d8d4cb` at 62-82% opacity
- Signal gold: `#e3c05c`
- Brass: `#a8842c`
- Technical silver: `#8a86a8`
- Parchment: `#e8e2d4`, reserved for exported documents and isolated reading artifacts

Do not introduce purple glows, neon gradients, pure-black glass, or a second
accent color.

## Typography

### Marketing and product explanation

- Inter Tight is the display and body family.
- Large headlines use weight 500, line-height 0.88-1.02, and tight tracking.
- Section headlines use the same family as the hero. Scale and spacing create
  hierarchy, not a font-family switch.
- Body copy uses weight 400 with line-height 1.55-1.7 and a maximum of 65ch.

### Editorial and manifesto surfaces

- Fraunces is reserved for About, manifesto passages, archival quotations, and
  rare narrative moments.
- Do not use Fraunces for product steps, plan results, controls, product page
  headers, or conversion sections.

### Technical notation

- IBM Plex Mono is for IDs, coordinates, status vocabulary, provenance,
  measurements, and concise instrument labels.
- Small mono text must remain readable. Use it only when the content is
  genuinely technical.

### Route typography contract

- Product routes (`/`, `/plan`, `/examples`, `/missions`, `/jobs`, `/network`,
  `/dashboard`, `/capabilities`, `/docs`, `/calendar`, and shared mission pages)
  use Inter Tight for headings and body copy.
- Editorial routes (`/about` and `/about/final-symposium`) may use Fraunces for
  narrative headings and essay prose. Controls, metadata, status, and navigation
  remain sans or mono.
- The shared `.display` utility is always sans. Editorial surfaces opt in with
  `.display-editorial`; serif must never arrive through accidental inheritance.

## Layout and spacing

- Global content width: 1180px with fluid side gutters.
- Section spacing: 80-128px desktop, 56-80px mobile.
- One section, one message. Pair it with one proof surface or one clear action.
- Split compositions collapse to one column below 900px.
- Avoid empty bands larger than the content they separate.
- Do not repeat the same split layout more than twice in sequence.
- Product proof panels should be large enough to read without zooming.

## Shape and depth

- Technical panels: 0-6px radius.
- Reading surfaces: 8-12px radius only when containment improves comprehension.
- Primary and secondary action buttons may remain pill-shaped.
- The navigation may use a single 16px glass container because it is persistent
  interactive chrome.
- Use shadows sparingly. Prefer image lighting, tonal fields, and hairlines.
- Glass belongs on interactive chrome, not on every section or card.

## Interaction and motion

- Every route participates in one scroll cadence: the next major section enters,
  the active section resolves at full contrast, and the previous section recedes.
  This shared rhythm is reversible when the user scrolls back.
- Sticky scroll stages are reserved for causal explanations whose content changes
  in place. Forms, tables, maps, and mission records keep normal document flow.
- Scroll-linked orbital linework may unify route transitions, but it stays behind
  content and never substitutes for product proof.
- Every link and button has hover, active, and visible focus states.
- Press feedback starts immediately with a subtle 0.97-0.98 scale.
- Animate only transform and opacity.
- Routine interaction completes within 300ms.
- Respect `prefers-reduced-motion`; remove large movement and ambient loops.
- Hover-only effects are gated behind `(hover: hover) and (pointer: fine)`.
- Autoplay motion longer than five seconds needs a pause path or must be purely
  decorative and hidden when reduced motion is requested.

## Product truth

- Keep LIVE, REFERENCE, SIMULATED, and PLANNED visually consistent.
- Never represent missing provider access as an empty successful state.
- Never invent provider data, prices, execution results, or satellite activity.
- Mission-plan specimens must correspond to real application behavior and use
  the same truth language as the product.

## Accessibility and responsive quality

- Maintain WCAG AA contrast for body text and controls.
- Use semantic links for navigation and buttons for actions.
- Provide visible `:focus-visible` treatment.
- Images declare useful alt text or `alt=""` when decorative.
- Full-bleed media reserves its dimensions and uses intentional crops.
- Multi-column sections define an explicit mobile collapse.
- Validate the complete page at desktop and mobile widths, including keyboard
  navigation, reduced motion, long text, and image fallbacks.

## Avoid

- Generic Vercel, Linear, or AI-SaaS imitation
- Random font changes between adjacent sections
- Repeated theme inversion while scrolling
- Charcoal or near-black marketing bands that break the Nomos blue field
- Excessive glassmorphism, glows, pills, and rounded cards
- Tiny dashboard UI used as marketing decoration
- Fake precision, fake metrics, and decorative status labels
- Stock astronaut imagery and generic glossy globes
- Long empty scroll bands
