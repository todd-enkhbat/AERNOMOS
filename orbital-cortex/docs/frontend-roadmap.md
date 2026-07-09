# Frontend roadmap — Phase B and beyond

Phase A shipped a functional demo UI wired to the full API. Phase B turns **nomosorbital.com** into a credible product surface.

## Current frontend (Phase A baseline)

- **Stack:** Next.js 14 App Router, TypeScript, Tailwind, MapLibre GL
- **Location:** `orbital-cortex/apps/web/`
- **Data:** Client-side `fetch` via `lib/api.ts`; types from OpenAPI (`npm run generate:api-types`)
- **Pages:** `/`, `/dashboard`, `/jobs`, `/jobs/[id]`, `/network`, `/docs`
- **Deployed:** Vercel, root `orbital-cortex/apps/web`

### What works today

- Submit job, poll status, view routing scores, timeline, GeoJSON map
- Network: nodes, ground stations, satellites, contact windows
- Job detail: scene metadata, routing replay audit hash
- Honest empty states when API is down (no fake mock data)

### Known limitations

- Demo aesthetic ("Orbital Cortex" desert theme); not yet a marketing site
- No OpenAPI-generated fetch client (types only)
- Client-only data fetching (no React Query / SSR)
- Fake Bearer token in job form
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
