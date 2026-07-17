# Nomos Orbital — Soul & Context

> Canonical context for anyone building, writing, or designing for Nomos Orbital.
> When a lasting decision is not covered here, make it in this spirit and add it back.

## 0. How to use this file

- Read Sections 1–3 before writing copy or code. Read Sections 6–8 before visual or editorial work.
- This file wins over stray prompts. Do not invent features, metrics, customers, partnerships, or endorsements. Unknown facts remain `[TBD]`.
- The voice test: would this sit comfortably beside the Voyager Golden Record and a Stripe API document?
- Product proof is the spine. Philosophy is connective tissue.

## 1. Manifesto

Nomos Orbital brings **order to the orbital age**.

Space is filling with compute, sensors, and satellites faster than anyone can coordinate them. Every satellite collects more than it can send home. Ground-station passes last minutes, and most sensor data is discarded before a human asks a question of it. The bottleneck is no longer collection. It is deciding where a space-data workload should move, and proving why.

Nomos helps operators plan that movement across satellite, ground, and cloud infrastructure. It searches real public data, calculates contact opportunities, compares feasible routes, and returns a source-backed mission brief with labeled assumptions. Live tasking, reservation, and onboard execution require provider integrations that Nomos does not pretend to have.

Nomos means order, law, and the act of binding things together. Astronomy is star-arranging. The long mission is to make machinery in orbit legible and accountable so that intelligence moving off-planet remains something humans can direct, audit, and trust.

Satellites should become agentic collaborators working on human missions, not opaque schedulers. The near-term product earns that future by being useful and honest today.

Intellectual lineage: Carl Sagan and the Golden Record, engineering humility, Russell's clarity, and the idea that order is a human act of will. Golden, ancient, exact.

## 2. Positioning

- **Primary tagline:** *Order, for the orbital age.*
- **Category:** Mission planning for space-data workloads.
- **Elevator:** Nomos plans how space-data workloads should move across satellite, ground, and cloud infrastructure, using real orbital and catalog data, and returns a source-backed execution plan.
- **Homepage promise:** Describe your mission and constraints. Nomos generates a source-backed execution plan using real orbital and infrastructure data.
- **Developer framing (docs / deep technical only):** A control plane for routing and audit when jobs are submitted. Do not lead the homepage with this language.
- **Internal analogy only:** Stripe for orbital compute. Kubernetes for orbital infrastructure.
- **Problem:** Satellites collect more than they can send home. Operators need a traceable plan before they commit to a route.

Nomos is not a satellite operator, launch company, ground-station provider, or data reseller. It is the planning and verification layer above those systems.

### Homepage-facing language (prefer)

- Plan how your space-data workload should move
- Source-backed execution plan
- Real orbital and infrastructure data
- Technical mission brief
- Assumptions and unavailable integrations

### Language to demote from hero / first screen

Keep these in `/docs` or deep technical sections only:

- orchestration layer
- deterministic routing
- control plane
- compliance-aware infrastructure
- autonomous orbital intelligence
- multi-domain workload placement

## 3. Source of truth

- **Company:** Nomos Orbital
- **Repository:** AERNOMOS
- **Live site:** https://nomosorbital.com
- **API:** https://api.nomosorbital.com
- **Larger mission:** *The Final Symposium*, used sparingly and only from About
- **Founder:** Tsogt "Todd" Enkhbat
- **Team experience:** NASA-adjacent quantum satellite research (T-REX, Brown University) and astrophysics research (Harvard-Smithsonian / TESS). Describe this as experience, never endorsement.

### Product primitives (customer path)

- **Mission:** a private customer plan for a space-data workload.
- **Plan:** a ranked, source-backed recommendation with ordered steps and evidence.
- **Truth status:** OBSERVED, CALCULATED, PROVIDER_REPORTED, ESTIMATED, SIMULATED, STALE, or UNAVAILABLE on user-facing values.
- **Brief:** the technical mission result: recommendation, feasibility, timeline, geography, assumptions, next actions.

### Product primitives (developer historical simulation demo)

- **Job:** a space-data AI task submitted to the legacy historical simulation demo.
- **Node:** a possible compute target, orbital or cloud (simulated availability).
- **Score:** seven weighted factors used to rank nodes for a job and priority.
- **Route:** the selected path. Every route carries a sha256 replay hash.
- **Return:** GeoJSON plus signed artifact URLs (SIMULATED detections on this path).
- **Example mission:** a curated public `is_example` mission at `/examples` with explicit real/sim disclosures.

### Canonical customer pipeline

1. **Describe** — guided builder at `/plan`
2. **Evaluate** — catalogs, contact windows, infrastructure comparison
3. **Recommend** — source-backed mission brief at `/missions/[id]`

Browse curated examples at `/examples` before or instead of building a private plan.

### Legacy historical simulation pipeline

1. **Request** — `POST /v1/jobs`
2. **Score** — seven weighted factors
3. **Route** — sha256 replay hash
4. **Return** — SIMULATED GeoJSON plus signed URLs

Label this path **Historical simulation demo**. It is not the primary CTA.

### Demo truth

- Mission planning searches real public catalogs (Microsoft Planetary Computer), calculates SGP4 contact windows from CelesTrak TLEs (live or pinned), and compares feasible infrastructure patterns.
- Plans label assumptions, unavailable integrations, and truth status. Cost estimates are UNAVAILABLE until a real pricing source exists.
- Satellite tasking, ground-station reservation, onboard execution, private telemetry, and commercial pricing guarantees require provider integration and are not claimed as live.
- Curated public examples at `/examples` are `is_example` missions with explicit disclosures for real data, real calculations, estimated steps, simulated steps, and unavailable integrations.
- The legacy Job API, database, async queue, worker, routing audit, PostGIS storage, and artifact delivery run on production infrastructure with simulated compute execution and canned ship-detection output. UI must scream SIMULATED.
- Demo reset may wipe visitor jobs; curated example missions and curated example jobs are preserved or idempotently reseeded.
- Anonymous private sessions protect visitor missions. Share links are explicit. Missions are not publicly enumerable.
- The shared demo credential `oc_demo_public` is not customer authentication. Job creation is rate-limited by IP.
- Event trails are append-only and decisions are hashed. Events are not cryptographically signed.

### Demo vocabulary

- Customer path: Build a mission plan → recommended brief
- Examples: Maritime monitoring, Wildfire response, Disaster imagery delivery, Customer edge processing
- Historical simulation demo: Ship Detection, Crop Health, Disaster Response on `/jobs`
- Priorities: Fastest, Cheapest, Most Reliable
- Reference scene: SAR, New York Harbor, bbox −74.3, 40.3, −73.5, 41.0
- Promise: No account needed for private planning. Job demo runs against the production API with simulated execution and is demoted from the primary path.

### Unknowns

`[TBD]` pricing, interest-form URL, GitHub organization URL, public contact email, launch date, named customers.

## 4. Site architecture

The site has two jobs:

1. Help a non-technical visitor understand Nomos in about five seconds and start a private mission plan.
2. Prove the system is real to developers with docs, the job demo, and exact primitives.

The customer planning path is the spine. The developer demo and mission narrative sit around it.

### Homepage order

1. Hero: mission-planning promise, primary CTA to `/plan`, secondary CTA to `/examples`
2. Three steps: describe → evaluate → recommended plan
3. What Nomos does today / What requires provider integration
4. Demoted historical simulation demo link to `/jobs` (not the primary action)
5. About, contact, and footer elsewhere in the site chrome

Keep the main navigation product-first: Dashboard, Plan, Missions, Network, Calendar, About, Docs. The Final Symposium remains an About subpage. Calendar is a shared verified industry register the public can use. Presence is framed as "you may see us there," not confirmed attendance. Include a register-interest path for business and operations conversations. Export ICS/CSV/JSON.

## 5. Hero narrative

The marketing hero is plain and outcome-led:

1. Brand: Nomos Orbital
2. One headline about planning workload movement across satellite, ground, and cloud
3. One subhead about source-backed plans from real data
4. Primary and secondary CTAs
5. One dominant visual (`OrbitalScene`)

Readability beats decorative complexity in the first viewport. No stat strips, fake metrics, or demo launcher in the hero.

The longer four-phase scroll narrative (SIGNVM → FVSIO → SPHÆRA → LITHOGRAPHIA) may still appear on About and immersive story surfaces. Reduced-motion users see the ordered final frame.

## 6. Visual direction

**Ancient celestial cartography meets modern orbital infrastructure.** A forgotten astronomical instrument rebuilt as a distributed computing network. Buddhist restraint meets Greek order.

Moodboard language:

- Voyager Golden Record and pulsar diagrams
- antique astronomy and constellation maps
- black-and-white physics notation and orbital schematics
- Chinese and Buddhist cosmology prints, referenced respectfully
- NASA stamps, archival seals, registration marks
- restrained editorial posters and scientific field manuals

Palette:

- near-black `#050506`
- warm parchment and off-white
- brass and gold only for active signal, selected route, and scarce emphasis
- rare cobalt for provenance and archival source
- rare vermilion for stamp-like section indices

Typography:

- editorial serif for manifesto and display
- restrained grotesk for explanation
- monospace for code, IDs, coordinates, and measurements

Use fine linework, generous spacing, controlled grain, engraved hatching, polar grids, and specimen labels. Ornament stays peripheral.

Avoid neon SaaS gradients, excessive blur, cartoon rockets, stock astronaut imagery, generic glossy globes, and AI clichés. Glass belongs on interactive control surfaces, not every decorative layer.

## 7. Voice

- Direct, plain, and exact.
- Short declarative sentences.
- Specific rather than salesy.
- Quietly grand, never inflated.
- No em dashes in shipped copy.
- Product copy is spare and technical. Mission copy may be lyrical but remains restrained.
- Never obscure simulation boundaries or missing provider integrations.

## 8. Approved copy

- **Hero:** Plan how your space-data workload should move across satellite, ground, and cloud infrastructure.
- **Hero subline:** Describe your mission and constraints. Nomos generates a source-backed execution plan using real orbital and infrastructure data.
- **Primary CTA:** Build a mission plan
- **Secondary CTA:** View example plan
- **Tagline (brand):** Order, for the orbital age.
- **Problem:** Satellites collect more than they can send home.
- **Does today:** Searches real public catalogs; calculates contact opportunities; compares feasible routes; labels assumptions; generates a technical mission brief.
- **Requires provider:** Satellite tasking; ground-station reservation; onboard execution; private telemetry; commercial pricing guarantees.
- **About:** Nomos, the Golden Record, and source-backed orbital planning.
- **Demo (jobs):** Historical simulation demo. No account needed. Production API, real orbital math, SIMULATED execution and detections.
- **Footer:** est. among the stars · Source-backed mission plans for space-data workloads.

## 9. Instructions for agents

1. Lead the homepage and customer path with mission planning, not the job demo.
2. Keep `/examples` as the home for curated public examples with truth disclosures.
3. Preserve Request → Score → Route → Return for the historical simulation demo and docs; label it SIMULATED.
4. Do not claim live tasking, operational ground-station access, real orbital compute, live inference, commercial pricing guarantees, real authentication, or cryptographically signed events.
5. Design toward an instrument archive, not generic space technology.
6. Prefer readability over decorative complexity on first-viewport surfaces.
7. Prefer the shorter and truer sentence.
8. Write lasting decisions back into this file.
