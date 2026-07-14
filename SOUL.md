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

Space is filling with compute, sensors, and satellites faster than anyone can coordinate them. Every satellite collects more than it can send home. Ground-station passes last minutes, and most sensor data is discarded before a human asks a question of it. The bottleneck is no longer collection. It is orchestration: deciding where a job should run, routing it, and proving what happened.

Nomos is that layer. It routes space-data AI jobs across satellites and clouds, scores every node, explains every decision, and returns every result with an auditable trail. It is a control plane, not a black box.

Nomos means order, law, and the act of binding things together. Astronomy is star-arranging. The long mission is to make machinery in orbit legible and accountable so that intelligence moving off-planet remains something humans can direct, audit, and trust.

Satellites should become agentic collaborators working on human missions, not opaque schedulers. The near-term product earns that future by being useful and honest today.

Intellectual lineage: Carl Sagan and the Golden Record, engineering humility, Russell's clarity, and the idea that order is a human act of will. Golden, ancient, exact.

## 2. Positioning

- **Primary tagline:** *Order, for the orbital age.*
- **Category:** Orbital compute orchestration.
- **Elevator:** Nomos routes space-data AI jobs across satellites and clouds, scoring every node, explaining every decision, and returning every result with an auditable trail.
- **Developer framing:** A control plane, not a black box.
- **Internal analogy only:** Stripe for orbital compute. Kubernetes for orbital infrastructure.
- **Problem:** Satellites collect more than they can send home.

Nomos is not a satellite operator, launch company, ground-station provider, or data reseller. It is the routing, orchestration, and verification layer above those systems.

## 3. Source of truth

- **Company:** Nomos Orbital
- **Repository:** AERNOMOS
- **Live site:** https://nomosorbital.com
- **API:** https://api.nomosorbital.com
- **Larger mission:** *The Final Symposium*, used sparingly and only from About
- **Founder:** Tsogt "Todd" Enkhbat
- **Team experience:** Columbia plasma physics lab (CSX stellarator), NASA-adjacent quantum satellite research (T-REX, Brown University), astrophysics research (Harvard-Smithsonian / TESS). Describe this as experience, never endorsement.

### Product primitives

- **Job:** a space-data AI task submitted to the network.
- **Node:** a possible compute target, orbital or cloud.
- **Score:** seven weighted factors used to rank nodes for a job and priority.
- **Route:** the selected path. Every route carries a sha256 replay hash.
- **Return:** GeoJSON plus signed artifact URLs.
- **Control plane:** the public API exposing routes, lifecycle events, and replayable decisions.

### Canonical pipeline

1. **Request** — `POST /v1/jobs`
2. **Score** — seven weighted factors
3. **Route** — sha256 replay hash
4. **Return** — GeoJSON plus signed URLs

### Demo truth

- The API, database, async queue, worker, routing audit, PostGIS storage, and artifact delivery run on production infrastructure.
- Contact windows are real SGP4 calculations over a dated, pinned public TLE snapshot and public ground-station coordinates.
- Compute nodes, operational availability, provider costs, execution, and inference are simulated.
- Ship detections use an offline, canned New York Harbor reference scene. There is no live satellite tasking or live SAR processing.
- The shared demo credential is not customer authentication. Job creation is rate-limited by IP.
- Event trails are append-only and decisions are hashed. Events are not cryptographically signed.

### Demo vocabulary

- Missions: Ship Detection, Crop Health, Disaster Response
- Priorities: Fastest, Cheapest, Most Reliable
- Reference scene: SAR, New York Harbor, bbox −74.3, 40.3, −73.5, 41.0
- Promise: No account needed. Runs against the production API with simulated execution.

### Unknowns

`[TBD]` pricing, interest-form URL, GitHub organization URL, public contact email, launch date, named customers.

## 4. Site architecture

The site has two jobs:

1. Prove the system is real to developers with the demo, docs, and exact primitives.
2. Convey the mission to investors and believers.

The developer proof is the spine. The mission earns its place around it.

### Homepage order

1. Hero: category, promise, demo
2. Pipeline: Request → Score → Route → Return
3. Problem: satellites collect more than they can send home
4. Developer proof: public control plane, curl, routing audit
5. About: Golden Record, research roots, mission
6. Contact and footer

Keep the main navigation product-first: Dashboard, Jobs, Network, Calendar, About, Docs. The Final Symposium remains an About subpage. Calendar is a shared verified industry register the public can use. Presence is framed as "you may see us there," not confirmed attendance. Include a register-interest path for business and operations conversations. Export ICS/CSV/JSON.

## 5. Hero narrative

The hero is a four-phase scroll narrative:

1. **SIGNVM / Flux:** granular signal, particles, nodes, raw intent.
2. **FVSIO / Fusion:** energetic orbital paths reveal a connected planetary system.
3. **SPHÆRA / Convergence:** paths become deliberate and form an ordered celestial network.
4. **LITHOGRAPHIA / Golden Record:** motion resolves into a still engraved record.

The arc is chaos to order, energy to stillness. The final frame should feel launchable as an etched artifact. Reduced-motion users see Phase 4.

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
- Never obscure simulation boundaries.

## 8. Approved copy

- **Hero:** Order, for the orbital age.
- **Hero subline:** Nomos routes space-data AI jobs across satellites and clouds, scoring every node, explaining every decision, and returning every result with an auditable trail.
- **Eyebrow:** Orbital compute orchestration
- **Problem:** Satellites collect more than they can send home.
- **Problem body:** Every ground-station pass is minutes long. Nomos runs inference where it is fastest and downlinks only the answer.
- **Developer header:** A control plane, not a black box.
- **Developer body:** Routing scores, lifecycle events, replayable decision hashes. Public and documented.
- **About:** Nomos, the Golden Record, Columbia plasma lab.
- **Demo:** No account needed. Production API, real orbital math, simulated execution.
- **Footer:** est. among the stars · Open control plane for space-data AI. Every job routed, every decision explained, every artifact returned.

## 9. Instructions for agents

1. Preserve Request → Score → Route → Return.
2. Lead with the working product.
3. Do not claim live tasking, operational ground-station access, real orbital compute, live inference, real authentication, or cryptographically signed events.
4. Design toward an instrument archive, not generic space technology.
5. End motion in order.
6. Prefer the shorter and truer sentence.
7. Write lasting decisions back into this file.
