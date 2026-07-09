# Frontend roadmap — Phase B and beyond

Phase A shipped a functional demo UI wired to the full API. **Phase B (shipped July 2026)** rebuilt **nomosorbital.com** as the "Nomos Record" design: dark glass UI, Golden Record brand mark, three.js orbital hero, demo-first homepage.

## Current frontend (Phase B)

- **Stack:** Next.js 14 App Router, TypeScript, Tailwind, MapLibre GL, framer-motion, three.js
- **Location:** `orbital-cortex/apps/web/`
- **Data:** Client-side `fetch` via `lib/api.ts`; types from OpenAPI (`npm run generate:api-types`)
- **Pages:** `/`, `/dashboard`, `/jobs`, `/jobs/[id]`, `/network`, `/docs`
- **Deployed:** Vercel, root `orbital-cortex/apps/web`
- **Fonts:** Fraunces (display serif), Inter (UI), IBM Plex Mono (data) via `next/font`

### Phase B highlights

- **Brand:** `components/brand/NomosMark.tsx` — Golden Record homage SVG (pulsar burst, hydrogen atom, playback arc, waveform); favicon at `app/icon.svg`
- **Orbital hero:** `components/orbital/OrbitalScene.tsx` — three.js graticule globe, gold orbit rings, animated satellites, ground-station pins; mouse parallax; `prefers-reduced-motion` respected; camera pulls back on narrow viewports
- **Demo-first:** `components/jobs/DemoLauncher.tsx` glass panel in the hero — one-click job submit (no API key field), inline animated `JobStepper`, link to full mission view
- **Glass system:** `.glass` / `.glass-strong` / `.editorial` utilities in `globals.css`; dark void base with warm cream editorial islands (VAST-style dark/light mesh)
- **Network page:** contact-window Gantt (`components/network/ContactWindowTimeline.tsx`) + shared orbital scene
- **Job detail:** mission phase stepper, dark CARTO map tiles, audit match/mismatch styling

### Known limitations

- No OpenAPI-generated fetch client (types only)
- Client-only data fetching (no React Query / SSR)
- API has no real auth; demo uses shared `oc_demo_public` bearer (server rate-limits POST /v1/jobs per IP)
- Dashboard N+1 routing calls

---

## Phase B — Product website (recommended next chat)

**Goal:** Nomos Orbital feels like a real company, not an internal demo.

### 1. Marketing layer

Replace or expand `/` with:

- Value prop: **"Kubernetes for orbital infrastructure"**
- Problem → solution narrative (downlink cost, routing, one API)
- Social proof / use-case cards (maritime SAR demo as one example)
- Clear CTAs: **Try demo**, **Read API docs**, **Python SDK**
- Optional: `/about`, `/pricing` (placeholder), `/contact`

**Design direction:** Space-industrial, trustworthy, less "dev dashboard as homepage". Keep warm palette or evolve to cleaner Nomos brand system (typography, logo mark, navy/sand/orbit accent).

### 2. App shell vs marketing shell

Split layouts:

- `MarketingLayout` — public pages (/, /about, /docs intro)
- `AppLayout` — product console (`/dashboard`, `/jobs`, `/network`)

Navigation: Marketing header links into app; app header links back to home/docs.

### 3. Job flow UX

| Improvement | Why |
| --- | --- |
| React Query or SWR for polling | Cleaner job status updates, cache invalidation |
| Progress stepper | queued → routing → executing → downlinking → complete |
| Contact window timeline on job detail | Shows orbital physics differentiator |
| Routing replay surfaced prominently | Audit hash, match/mismatch badge |
| Empty states with actions | "Start worker" ops note for self-hosters |

### 4. Network / orbital story

- Interactive contact window timeline (Gantt-style passes)
- Map: ground stations + optional satellite ground tracks (MapLibre layers)
- Satellite detail drawer (TLE epoch, NORAD id, linked compute node)

### 5. Developer experience

- `/docs` → multi-page: Quickstart, API reference (embed OpenAPI or link Redoc), SDK install
- Copy-paste snippets with **production** `api.nomosorbital.com` base URL
- Optional: API key management UI (when backend auth exists)

### 6. Technical debt to pay in Phase B

| Item | Approach |
| --- | --- |
| Type drift | Keep `npm run generate:api-types` in CI; consider openapi-fetch |
| Auth | Next.js route handlers holding API key server-side; or real API keys |
| SEO | Metadata, OG images, sitemap for marketing pages |
| Performance | Code-split MapLibre; lazy load job detail map |
| Accessibility | Focus states, chart/table semantics |

### 7. Suggested build order

1. Brand system + marketing homepage
2. App shell split + navigation
3. Job flow polish (stepper, React Query)
4. Network timeline + contact windows viz
5. Docs site expansion
6. Auth stub (server-side proxy or API keys)

---

## Phase C — Platform UI (later)

- Multi-tenant dashboard, usage metrics, billing placeholders
- Webhook / integration settings
- Model registry browser
- Real-time job stream (SSE or WebSockets)
- Mobile-responsive ops console

---

## Files agents should know

```
orbital-cortex/apps/web/
  app/                    # Routes (App Router)
  components/             # AppFrame, HarborMap, RouteExplain, ...
  lib/
    api.ts                # REST client
    types.ts              # Re-exports from generated OpenAPI types
    generated/api-types.ts
    default-job-payload.ts
  public/                 # Static assets
  vercel.json
```

After API changes: regenerate types before UI work.

---

## Non-goals (Phase B)

- Real satellite tasking UI
- Payments / checkout
- Full design system documentation site
- Renaming npm package to `@nomos-orbital/web` (optional, low priority)
