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

Nomos helps operators orchestrate that movement across satellite, ground, and cloud infrastructure. It searches real public data, calculates contact opportunities, compares feasible routes, runs the job with a source-backed audit trail, and labels assumptions honestly. Live commercial tasking, reservation, and onboard provider execution require integrations that Nomos does not pretend to have.

Nomos means order, law, and the act of binding things together. Astronomy is star-arranging. The long mission is to make machinery in orbit legible and accountable so that intelligence moving off-planet remains something humans can direct, audit, and trust.

Satellites should become agentic collaborators working on human missions, not opaque schedulers. The near-term product earns that future by being useful and honest today.

Intellectual lineage: Carl Sagan and the Golden Record, engineering humility, Russell's clarity, and the idea that order is a human act of will. Golden, ancient, exact.

## 2. Positioning

- **Primary tagline:** *Order, for the orbital age.*
- **Category:** Space intelligence infrastructure. The intelligence and orchestration layer for space infrastructure.
- **Category rule:** Mission planning is a current product surface and an output, never the company category. The company is the layer that turns fragmented space infrastructure into a programmable network. Do not let current limitations define the company; state them as product maturity.
- **One-line description:** Nomos turns fragmented space infrastructure into a programmable network.
- **Interaction model:** Tell the network what you need. Nomos determines how the space stack can deliver it.
- **North star:** One request. The whole space stack. Space should be callable.
- **Final product claim (allowed):** Nomos turns a space-data objective into a source-backed infrastructure plan, then routes and runs the job with a traceable record. It searches real public data catalogs, calculates orbital and communication constraints, compares feasible execution paths, explains assumptions, and produces a shareable technical mission brief. Live commercial tasking, reservation, and onboard provider execution require integrations Nomos does not pretend to have.
- **Elevator:** Nomos is building the intelligence layer for space. It reasons across satellites, ground infrastructure, and cloud compute to determine how a space-data objective should be fulfilled, and explains every decision. Today it recommends and routes with real public data; provider integrations turn those decisions into execution.
- **Homepage promise:** Tell the network what you need. Nomos determines how satellites, ground systems, and cloud compute deliver it.
- **Developer framing (docs / deep technical):** A control plane for routing, execution, and audit when jobs are submitted.
- **Internal analogy only:** Uber-style abstraction for space infrastructure. Stripe for orbital compute. Kubernetes for orbital infrastructure. Never shipped as copy.
- **Problem:** Space is powerful; access to it is still bespoke. Every team coordinates operators, spacecraft, ground networks, compute environments, and constraints by hand.
- **Progression (vision spine):** Understand → Recommend → Route → Orchestrate → Execute. The first three exist today; the last two arrive with integrations and stay labeled until then.

Nomos is not a satellite operator, launch company, ground-station provider, or data reseller. It is the intelligence and orchestration layer above those systems. Do not reduce Nomos to a router, a mission planner, an onboard-inference company, a ground-station marketplace, or cloud for satellites; each is one component or output beneath the abstraction.

### Homepage-facing language (prefer)

- The intelligence layer for space
- Space intelligence infrastructure
- Different infrastructure. One interface.
- The infrastructure can stay heterogeneous. Access to it should not.
- One request. The whole space stack.
- Run a request (primary CTA)
- Recommended execution path (output)
- Assumptions and unavailable integrations

### Status labels (marketing surfaces)

Use one consistent status system instead of repeated caveat paragraphs: **LIVE** (working now, on real data), **REFERENCE** (real public facts in the registry, cited), **SIMULATED** (modeled behavior, always labeled), **PLANNED** (requires provider integration, never claimed early). Defined on the homepage maturity band and `/capabilities`.

### Marketing framing (homepage / brand, not product proof)

Use these as metaphors for the long mission. They must never be read as live marketplace claims.

- **Conductor:** Nomos is the connectivity orchestrator for the space industry. Like a conductor, it does not replace the instruments. It holds the score so satellite, ground, and cloud can play the same mission.
- **On-demand fleet:** Satellites should become callable infrastructure, closer to ordering a ride than filing a weeks-long tasking ticket. Near-term product earns that future with source-backed plans. Live commercial tasking still requires provider integrations.
- **Category line (aspirational, homepage-ok when paired with truth):** The intelligence layer for space. Job routing is one mechanism inside it.
- **Do not say:** Nomos is Uber for satellites as a completed product fact, or that operators can currently task arbitrary satellites through Nomos.

### Language to keep precise (do not overclaim)

Forbidden live claims stay forbidden (Section 3). Prefer:

- orchestration / job orchestrator (homepage-ok)
- routed execution path
- source-backed audit trail

Keep these in `/docs` or deep technical sections unless the product surface already proves them:

- deterministic routing
- compliance-aware infrastructure
- autonomous orbital intelligence
- multi-domain workload placement
- live satellite tasking / ground reservation as completed fact

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

### Forbidden claims (must not appear)

- AI ran onboard a satellite
- Satellite was tasked
- Ground station reserved
- Commercial pricing guaranteed
- Private provider availability is live
- Execution occurred unless a real adapter completed it

### Demo truth

- Mission planning searches real public catalogs (Microsoft Planetary Computer), calculates SGP4 contact windows from CelesTrak TLEs (live or pinned), and compares feasible infrastructure patterns.
- Infrastructure provider records are versioned, source-cited public facts or explicitly SIMULATED placeholders. `documented_api` and `sandbox_requested` do not mean Nomos has live access; only `sandbox_connected` and `partner_connected` are treated as connected.
- Plans label assumptions, unavailable integrations, and truth status. Cost estimates are UNAVAILABLE until a real pricing source exists.
- Mission owners can run a real CPU demo (fixture GeoTIFF crop + thumbnail) from the mission brief; measured durations are OBSERVED, not simulated. This is not live catalog download or GPU inference.
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

1. Hero: intelligence-layer category and promise, primary CTA "Run a request" to `/plan`, secondary CTA to `/network`, small "early access · live demo" status
2. Problem: space is powerful, access is bespoke; today's chain vs the Nomos chain
3. Network abstraction: one request → Nomos → orbital + ground + cloud → result; "Different infrastructure. One interface."
4. Intelligence loop: express the outcome → understand the environment → determine the path → execute across the network (04 labeled planned)
5. What exists today (available now) vs coming with network integrations, plus the status-label key
6. Product surfaces: run a request, example requests, the network; developer and sim-demo links demoted below
7. Vision close: one request, the whole space stack; Understand → Execute progression strip

Keep the main navigation brand-first and product-accessible: Request (`/plan`), Missions, Network, Control (`/dashboard`), Capabilities, About, Docs. Calendar stays reachable from the footer and About, not top navigation. UI labels may differ from internal routes; do not rename routes for branding. Capabilities (`/capabilities`) is the public truth map: live product, provider gaps, aspirations, and forward work. The Final Symposium remains an About subpage. Calendar is a shared verified industry register the public can use. Presence is framed as "you may see us there," not confirmed attendance. Include a register-interest path for business and operations conversations. Export ICS/CSV/JSON.

## 5. Hero narrative

The marketing hero is plain and category-led:

1. Eyebrow: space intelligence infrastructure (with the Nomos mark)
2. One headline naming the category: the intelligence layer for space
3. One subhead on the interaction model: tell the network what you need; Nomos determines how satellites, ground systems, and cloud deliver it
4. Primary CTA "Run a request" and secondary CTA to the network, fully inside the art's central portal, with a small early-access status line
5. One dominant visual (portal hero on homepage; About may use different art)

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

- Yves Klein field `#002FA7` (`--klein`), deepening to `#001a75` / `#001045`
- warm parchment and off-white for honesty / boundary bands
- brass and gold only for active signal, selected route, and scarce emphasis
- cream and silver for body copy on the blue field
- rare cobalt for provenance and archival source
- rare vermilion for stamp-like section indices
- do not use charcoal `#050506` or pure black glass on marketing or tool chrome; blue-tinted ink glass only

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

- **Final claim:** Nomos turns a space-data objective into a source-backed infrastructure plan. It searches real public data catalogs, calculates orbital and communication constraints, compares feasible execution paths, explains assumptions, and produces a shareable technical mission brief.
- **Hero eyebrow:** Space intelligence infrastructure
- **Hero:** The intelligence layer for space.
- **Hero subline:** Tell the network what you need. Nomos determines how satellites, ground systems, and cloud compute deliver it.
- **Hero (alt):** Make space programmable. / One request. The whole space stack.
- **Primary CTA:** Run a request
- **Secondary CTA:** See the network
- **Tagline (brand):** Order, for the orbital age.
- **Site title:** Nomos Orbital | Space Intelligence Infrastructure
- **Meta description:** Nomos Orbital is building the intelligence and orchestration layer across satellites, ground infrastructure, and cloud compute.
- **Problem:** Space is powerful. Access to it is still bespoke.
- **Network line:** Different infrastructure. One interface. / The infrastructure can stay heterogeneous. Access to it should not.
- **Does today:** Reasons over real public orbital and infrastructure data; calculates contact opportunities; compares feasible processing routes; exposes assumptions and sources; explores execution with labeled simulation.
- **Coming with integrations:** Satellite tasking; ground-station reservation; onboard workload execution; private telemetry; live commercial availability and pricing; automated multi-provider execution.
- **Request page (`/plan`):** eyebrow Nomos intelligence · H1 What do you need from the network? · output described as a recommended execution path or mission brief, never the company category.
- **About:** Order, for the orbital age. Belief → problem → role → name → Golden Record → today → direction.
- **Demo (jobs):** Historical simulation demo. No account needed. Production API, real orbital math, SIMULATED execution and detections.
- **Footer:** est. among the stars · Nomos Orbital is building the intelligence layer for space infrastructure: one request, routed across orbital, ground, and cloud systems, with every decision explained.

## 9. Instructions for agents

1. Lead every surface with the intelligence-layer category. Mission planning is a surface and an output, not the company; the job demo is demoted further still.
2. Keep `/examples` as the home for curated public examples with truth disclosures.
3. Preserve Request → Score → Route → Return for the historical simulation demo and docs; label it SIMULATED.
4. Do not claim live tasking, operational ground-station access, real orbital compute, live inference, commercial pricing guarantees, real authentication, or cryptographically signed events.
5. Design toward an instrument archive, not generic space technology.
6. Prefer readability over decorative complexity on first-viewport surfaces.
7. Prefer the shorter and truer sentence.
8. Write lasting decisions back into this file.
