# Nomos Orbital — Mission Planner Master Plan

Persistent master plan for transforming the simulated orbital-compute demo into a
credible, privacy-safe, source-backed mission-planning product.

**Do not execute phases A–T in one shot.** Work one phase at a time using the
goal-based loop in [`.cursor/rules/nomos-build-loop.mdc`](../.cursor/rules/nomos-build-loop.mdc)
and track status in [`BUILD_PROGRESS.md`](BUILD_PROGRESS.md).

### Copy-paste agent prompts (detailed)

Phases **A–C are complete**. For each remaining phase, use the standalone prompt in:

**[`docs/phase-prompts/`](phase-prompts/README.md)**

Those files are the implementation-level instructions (exact paths, checklists,
non-goals, validation commands). The lettered sections below remain the product
spec / acceptance source of truth; when they conflict on *how* to implement,
prefer the phase-prompt file plus decisions already recorded in
`BUILD_PROGRESS.md`.

Companion audit (Phase A output):
[`orbital-cortex/docs/current-system-audit.md`](../orbital-cortex/docs/current-system-audit.md).

---

## Product north star

The core product should become:

> Turn a space-data objective into a real, source-backed infrastructure plan.

The long-term product remains a vendor-neutral control plane for planning,
scheduling, and eventually executing workloads across satellite, ground, edge,
and cloud infrastructure.

For this build, focus on planning, truthfulness, real data, explainability,
privacy, and useful outputs.

**Do not** redesign the company into an AI model company.
**Do not** focus on GPU inference as the primary customer value.
**Do not** prioritize visual polish before the underlying customer workflow works.

---

## Canonical execution order (dependency-corrected)

Letter labels (A–T) are stable IDs from the full specifications below.
**Agents must follow this numbered order**, not alphabetical letter order,
unless the user explicitly overrides it.

| Step | Phase | Title | Commit message |
| --- | --- | --- | --- |
| 1 | A | System audit doc | `docs: audit current Nomos system and simulation boundaries` |
| 2 | B | Mission data model + TruthStatus | `feat: add private mission planning data model` |
| 3 | C | Anonymous private sessions | `feat: add private anonymous mission sessions and share links` |
| 4 | F | STAC catalog discovery | `feat: integrate real STAC satellite data discovery` |
| 5 | H | Orbital data provenance | `feat: add fresh orbital data provenance and mission-specific infrastructure` |
| 6 | G | Truth-status UI system | `feat: add source provenance and truth-status labeling` |
| 7 | E | Guided mission builder `/plan` | `feat: add guided customer-facing mission builder` |
| 8 | I | Planning engine | `feat: build source-backed mission feasibility and planning engine` |
| 9 | J | Mission result page | `feat: replace simulated job output with customer mission brief` |
| 10 | D | Homepage rewrite | `feat: simplify homepage around mission planning outcomes` |
| 11 | K | Exports and sharing | `feat: add mission brief PDF JSON and private sharing` |
| 12 | L | Isolate simulations into examples | `refactor: isolate simulations into clearly labeled examples` |
| 13 | M | Real CPU execution | `feat: add lightweight real CPU execution provider` |
| 14 | N | Provider registry | `feat: add extensible infrastructure provider registry` |
| 15 | O | Analytics and ops metrics | `feat: add privacy-safe product and planning analytics` |
| 16 | P | Feedback and design-partner capture | `feat: add mission feedback and design partner requests` |
| 17 | Q | Docs and SDK | `docs: document mission planner APIs data sources and limitations` |
| 18 | R | Accelerator demos | `feat: add accelerator-ready mission planning demos` |
| 19 | S | Security review | `security: harden private mission planning workflow` |
| 20 | T | Final validation and deploy | `chore: complete mission planner validation and release documentation` |

### Why this order differs from A→T letter order

1. Homepage rewrite (**D**) waits until `/plan` (**E**) and the result page (**J**) exist so CTAs are not dead ends.
2. Truth-status vocabulary starts in the data model (**B**); frontend provenance components (**G**) come after orbital provenance (**H**) and before the result page (**J**).
3. Privacy (**C**) stays early — `GET /v1/jobs` and `/jobs` are public today.
4. STAC (**F**) and orbital provenance (**H**) precede the planner (**I**) so plans can cite real sources.

### Concrete tech choices (decided; do not re-litigate per phase)

- STAC: Microsoft Planetary Computer via `pystac-client` (Sentinel-1 GRD first, Sentinel-2 L2A second); Earth Search (Element84) behind the same `DataCatalogProvider` abstraction.
- PDF: WeasyPrint from a Jinja HTML template in the worker → R2 via existing object store.
- Map drawing: MapLibre + terra-draw or maplibre-gl-draw.
- Tokens: `secrets.token_urlsafe(32)`, store SHA-256 hash only (session + share).
- Session cookie (prod): `Domain=.nomosorbital.com; HttpOnly; Secure; SameSite=Lax` + CORS `allow_credentials`. Local: Next.js rewrite proxy `/api/*` → API for same-origin.

### Repo-specific standing requirements

- Update `SOUL.md`, `AGENTS.md`, and `orbital-cortex/docs/capability-truth.md` when copy or product boundaries change.
- After API schema changes: `python -m scripts.export_openapi ../../openapi.json` then `npm run generate:api-types`.
- Keep Skyfield/SGP4 contact windows, TLE cache, routing/replay, ARQ worker, object store, and the Job pipeline until Phase L re-homes the demo.
- Update `.github/workflows/demo-reset.yml` when curated examples exist (Phase L+); never delete them in reset.

---

## Mission-planner default entry

When the user says any of: "continue the build", "next phase", "work on Nomos", "continue Nomos":

1. Read `docs/NOMOS_BUILD_PLAN.md` and `docs/BUILD_PROGRESS.md`.
2. Execute **only** the phase listed as current / in progress.
3. Follow `.cursor/rules/nomos-build-loop.mdc` until that phase's acceptance criteria pass.
4. Update `BUILD_PROGRESS.md` and stop (do not start the next phase unless asked).
5. Commit only when the user explicitly asks to commit, unless the phase prompt already requests the phase commit message.

---

## Full phase specifications (A–T)

The sections below are the authoritative acceptance criteria, required work, and
commit messages for each lettered phase. Use the **canonical execution order**
table above to decide which phase to implement next.

# Global operating rules

Work through the phases below in order.

For every phase:

1. Inspect the existing implementation before changing anything.
2. Reuse existing architecture where reasonable.
3. Avoid unnecessary rewrites.
4. Keep the existing demo working while migrating it.
5. Add tests for all important logic.
6. Run lint, type checks, tests, frontend build, and Docker build when applicable.
7. Fix failures before moving on.
8. Commit each completed phase separately with a clear commit message.
9. Update documentation after each phase.
10. Continue automatically to the next phase after validation.

Never silently invent data.

Every important number shown to a user must carry one of these truth statuses:

* OBSERVED
* CALCULATED
* PROVIDER_REPORTED
* ESTIMATED
* SIMULATED
* STALE
* UNAVAILABLE

Any feature that is not connected to a real provider must say so clearly.

Do not imply that Nomos is tasking satellites, reserving ground stations, running onboard compute, or executing real orbital AI unless a real provider integration exists.

Do not expose submitted user data publicly.

Do not display all jobs from all users in one public feed.

Do not remove existing useful backend infrastructure such as FastAPI, Postgres/PostGIS, Redis/ARQ, R2 object storage, the SDK, route scoring, contact-window calculations, or the current frontend unless a replacement is fully implemented.

# Target customer experience

A user should be able to:

1. Open the website.
2. Understand the product within five seconds.
3. Start a private mission plan without creating an account.
4. Describe a real space-data objective.
5. Select or define an area of interest.
6. Set a deadline and operational constraints.
7. Search real public satellite-data catalogs.
8. See real satellite and infrastructure information.
9. Receive multiple feasible and infeasible infrastructure plans.
10. Understand why Nomos recommended one plan.
11. See which values are observed, calculated, estimated, simulated, stale, or unavailable.
12. Export a professional mission brief.
13. Share the plan through a private unguessable link.
14. See clear next actions required to make the plan executable.

# Target product structure

The product should have two clearly separated surfaces.

## Public marketing surface

Routes such as:

* `/`
* `/how-it-works`
* `/examples`
* `/docs`

This surface explains the product simply and includes curated example missions.

## Private mission workspace

Routes such as:

* `/plan`
* `/missions`
* `/missions/[id]`
* `/share/[token]`

This surface contains the private mission-planning workflow.

Do not call the main user action “submit compute job.”

Use customer language such as:

* Build a mission plan
* Describe your objective
* Compare infrastructure options
* Generate plan
* View recommendation
* Export mission brief

# Phase A: Audit the current system

Before making changes, inspect the repository and create:

`docs/current-system-audit.md`

Document:

1. Existing backend architecture.
2. Existing frontend pages.
3. Current database models.
4. Current job lifecycle.
5. Existing routing logic.
6. Existing satellite and TLE data sources.
7. Existing ground-station data.
8. Existing simulated node data.
9. Existing simulated inference and output generation.
10. Existing authentication behavior.
11. Existing public job exposure.
12. Existing deployment setup.
13. Existing test coverage.
14. Existing technical debt.
15. Which parts are real, estimated, simulated, or unavailable.

Create a table with columns:

* Component
* Current implementation
* Truth status
* Customer value
* Required change

Acceptance criteria:

* The audit is detailed enough that another engineer can understand the current system.
* All current simulation points are identified.
* All current privacy risks are identified.
* No production behavior is changed in this phase.

Commit message:

`docs: audit current Nomos system and simulation boundaries`

# Phase B: Define the new product data model

Create or update database models to support private mission plans.

Add entities conceptually equivalent to:

## AnonymousSession

Fields:

* id
* session_token_hash
* created_at
* last_seen_at
* expires_at
* converted_user_id nullable

## Mission

Fields:

* id
* anonymous_session_id nullable
* organization_id nullable
* title
* objective_type
* status
* area_of_interest geometry
* start_time nullable
* end_time nullable
* deadline nullable
* max_cost_usd nullable
* max_data_volume_mb nullable
* preferred_compute_location nullable
* allowed_regions JSON
* data_source_preference JSON
* customer_systems JSON
* notes nullable
* created_at
* updated_at

## MissionDataCandidate

Fields:

* id
* mission_id
* source_provider
* collection
* external_item_id
* acquisition_time
* footprint geometry
* asset_metadata JSON
* estimated_size_bytes nullable
* source_url nullable
* source_timestamp
* truth_status
* created_at

## InfrastructureResource

Fields:

* id
* provider_name
* resource_type
* external_resource_id nullable
* name
* location geometry nullable
* capabilities JSON
* constraints JSON
* pricing JSON nullable
* access_level
* source_metadata JSON
* truth_status
* data_freshness_at nullable
* active

Resource types should support:

* satellite
* orbital_compute
* ground_station
* cloud_compute
* customer_edge
* storage
* network

## MissionPlan

Fields:

* id
* mission_id
* version
* recommended
* status
* summary
* estimated_total_time_seconds nullable
* estimated_total_cost_usd nullable
* confidence nullable
* assumptions JSON
* created_at

## MissionPlanStep

Fields:

* id
* mission_plan_id
* sequence
* step_type
* provider_name
* resource_id nullable
* title
* description
* start_time nullable
* end_time nullable
* duration_seconds nullable
* estimated_cost_usd nullable
* input_artifact nullable
* output_artifact nullable
* truth_status
* source_metadata JSON
* feasibility_status
* rejection_reason nullable

## SourceEvidence

Fields:

* id
* mission_id
* mission_plan_id nullable
* mission_plan_step_id nullable
* source_name
* source_type
* source_url nullable
* retrieved_at
* effective_at nullable
* raw_value JSON
* transformed_value JSON
* transformation_method nullable
* truth_status

## ShareLink

Fields:

* id
* mission_id
* token_hash
* created_at
* expires_at nullable
* revoked_at nullable
* permissions

Use migrations.

Add indexes for:

* mission ownership/session lookup
* mission creation time
* geographic search
* external catalog item IDs
* share tokens
* infrastructure provider and type

Acceptance criteria:

* Migrations run cleanly.
* Existing demo data remains compatible or is migrated safely.
* Mission data is isolated by anonymous session or organization.
* Database tests cover ownership and share-link access.

Commit message:

`feat: add private mission planning data model`

# Phase C: Implement anonymous private sessions

Implement a no-login private session system.

On first visit to the mission workspace:

1. Generate a cryptographically secure random session token.
2. Store only a hash in the database.
3. Store the raw token in a secure, HTTP-only, same-site cookie.
4. Associate new missions with that anonymous session.
5. Prevent one session from accessing another session’s missions.
6. Allow a mission to be accessed through a valid private share token.
7. Do not expose sequential internal IDs as the only access control.
8. Add expiration and cleanup behavior.

Create backend middleware or dependencies for:

* current anonymous session
* mission ownership validation
* share-token validation

Update the frontend so:

* `/missions` shows only the current session’s missions.
* Public example missions are stored separately and explicitly marked as examples.
* The old public all-jobs feed is removed from public navigation.
* Existing demo routes may remain internally accessible but must not expose user submissions publicly.

Add a visible warning:

“Demo environment. Do not submit proprietary or export-controlled information.”

Acceptance criteria:

* Two separate browser sessions cannot see each other’s missions.
* Public users cannot enumerate missions.
* Share links work only with valid tokens.
* Revoked or expired links fail.
* Tests cover unauthorized access.
* Security-sensitive cookies are configured properly in production.

Commit message:

`feat: add private anonymous mission sessions and share links`

# Phase D: Replace the homepage messaging

Rewrite the homepage for clarity.

The hero must communicate:

Headline:

“Plan how your space-data workload should move across satellite, ground, and cloud infrastructure.”

Subheadline:

“Describe your mission and constraints. Nomos generates a source-backed execution plan using real orbital and infrastructure data.”

Primary CTA:

“Build a mission plan”

Secondary CTA:

“View example plan”

The homepage should explain the product in three steps:

1. Describe the mission.
2. Nomos evaluates real data and infrastructure.
3. Receive a traceable recommended plan.

Add a section titled:

“What Nomos does today”

Clearly state:

* searches real public data catalogs,
* calculates satellite and ground contact opportunities,
* compares feasible infrastructure routes,
* labels assumptions and unavailable integrations,
* generates a technical mission brief.

Add a section titled:

“What requires provider integration”

Clearly state:

* satellite tasking,
* ground-station reservation,
* onboard execution,
* private telemetry,
* commercial pricing guarantees.

Remove or reduce homepage language that relies heavily on:

* orchestration layer
* deterministic routing
* control plane
* compliance-aware infrastructure
* autonomous orbital intelligence
* multi-domain workload placement

These concepts may appear later in technical sections, but not as the initial explanation.

Acceptance criteria:

* A nontechnical person can understand the product from the homepage.
* No false execution claims remain.
* The primary CTA leads to the mission-planning workflow.
* The existing visual identity may remain, but readability is more important than decorative complexity.

Commit message:

`feat: simplify homepage around mission planning outcomes`

# Phase E: Build the guided mission form

Create a customer-facing multi-step mission builder at `/plan`.

## Step 1: Objective

Offer options such as:

* Analyze existing satellite imagery
* Plan data delivery from a satellite
* Compare onboard, ground, edge, and cloud processing
* Plan a remote-sensing workflow
* Other

## Step 2: Area and time

Collect:

* area of interest using map drawing or coordinates
* date range
* desired data freshness
* optional specific satellite or sensor

Support:

* bounding box
* polygon
* uploaded GeoJSON if simple and safe

## Step 3: Constraints

Collect:

* deadline
* maximum cost
* maximum data volume
* preferred compute location
* allowed geographic regions
* data residency requirement
* existing cloud or infrastructure provider
* whether onboard processing is required, preferred, or unnecessary

## Step 4: Mission context

Collect:

* mission title
* organization name optional
* use case
* technical notes
* whether this is exploratory or an active mission

## Step 5: Review

Show a clear summary before generating the plan.

Use simple labels.

Hide advanced fields under an expandable section.

Validate all inputs on both frontend and backend.

Acceptance criteria:

* A user can create a mission without knowing technical Nomos terminology.
* Geographic input is valid.
* Required fields are clear.
* Form state survives navigation between steps.
* Submitting creates a private Mission record.
* Tests cover validation failures.

Commit message:

`feat: add guided customer-facing mission builder`

# Phase F: Add real satellite catalog discovery

Implement a real public satellite-data catalog integration.

Use a provider abstraction.

Create an interface conceptually similar to:

```python
class DataCatalogProvider:
    async def search(self, query: CatalogSearchQuery) -> list[CatalogItem]:
        ...

    async def get_item(self, external_item_id: str) -> CatalogItem:
        ...

    async def get_assets(self, external_item_id: str) -> list[CatalogAsset]:
        ...
```

Implement at least one real STAC provider.

Preferred initial source:

Microsoft Planetary Computer STAC or Copernicus Data Space STAC.

The implementation must:

1. Search by area of interest.
2. Search by date range.
3. Filter by collection or sensor.
4. Return real item IDs.
5. Return acquisition timestamps.
6. Return footprints.
7. Return asset metadata.
8. Return available file formats.
9. Estimate or retrieve asset size where available.
10. Record the source URL and retrieval timestamp.
11. Cache results appropriately.
12. Handle rate limits and upstream failures.
13. Never fabricate catalog items.

Start with Sentinel-1 SAR and optionally Sentinel-2.

Persist results as MissionDataCandidate records.

Show users:

* satellite or collection
* acquisition date
* footprint
* available assets
* estimated size
* source
* freshness
* truth status

Acceptance criteria:

* A real search over New York Harbor returns actual catalog items.
* Source metadata is persisted.
* Upstream outages produce clear errors.
* Duplicate catalog items are not inserted repeatedly.
* Tests mock provider responses.
* At least one integration test can run optionally against the real service.

Commit message:

`feat: integrate real STAC satellite data discovery`

# Phase G: Build the truth-status system

Create a reusable truth-status model across backend and frontend.

Every important field shown to the user must support:

* status
* source
* timestamp
* explanation
* calculation method
* freshness

Create frontend components such as:

* `TruthBadge`
* `SourcePopover`
* `FreshnessIndicator`
* `AssumptionPanel`

Example:

“Next contact window: 18:42 UTC”

Badge:

`CALCULATED`

Popover:

* Source: CelesTrak TLE snapshot
* Retrieved: timestamp
* Method: SGP4 propagation
* Ground station elevation mask: value
* TLE epoch: timestamp

For simulated values:

Badge:

`SIMULATED`

Popover:

“This value is generated for demonstration and is not connected to a provider.”

For unavailable functions:

Badge:

`UNAVAILABLE`

Popover:

“Nomos has not connected to a provider capable of performing this action.”

Acceptance criteria:

* No core mission-plan number appears without a truth status.
* Source and timestamp can be inspected.
* Simulated and estimated values are visually distinct.
* Truth statuses are included in API and export formats.

Commit message:

`feat: add source provenance and truth-status labeling`

# Phase H: Improve orbital and infrastructure data

Audit the current TLE and ground-station pipeline.

Implement:

1. A provider for current public orbital elements.
2. Scheduled refresh with caching.
3. Storage of TLE source and epoch.
4. Staleness detection.
5. Clear fallback to pinned demo data when the live source is unavailable.
6. Truth status of STALE or SIMULATED when fallback data is used.
7. Contact-window calculations tied to a specific orbital-data version.
8. Infrastructure-source metadata for ground stations.
9. Access-level labeling such as:

   * public information
   * sandbox available
   * partner required
   * private
   * simulated

Do not render all 30,000 tracked objects by default.

Only load and display relevant satellites for the user’s mission.

Acceptance criteria:

* A mission plan records which orbital-data snapshot was used.
* Contact-window calculations are reproducible.
* Stale data is clearly labeled.
* The map remains performant.
* Satellite selection is mission-specific.

Commit message:

`feat: add fresh orbital data provenance and mission-specific infrastructure`

# Phase I: Build the mission-planning engine

Replace the current “choose a fictional node” emphasis with a real feasibility and plan-generation engine.

Separate hard constraints from preferences.

## Hard constraints

Examples:

* data exists
* data covers the area of interest
* data is recent enough
* deadline is achievable
* resource supports required input type
* region is allowed
* data volume is within limits
* provider access exists
* estimated cost does not exceed maximum
* contact window exists when required

## Preferences

Examples:

* lowest latency
* lowest cost
* least data movement
* most recent data
* prefer onboard
* prefer customer environment
* highest confidence
* simplest operational path

Generate multiple MissionPlan records.

Each plan should contain ordered MissionPlanStep records.

Supported plan patterns should include:

## Existing imagery to cloud

Catalog scene
→ retrieve asset
→ transfer to cloud or customer storage
→ process
→ return result

## Existing imagery to customer edge

Catalog scene
→ retrieve asset
→ transfer to customer edge
→ process locally
→ return result

## Satellite to ground to cloud

Satellite acquisition
→ next eligible contact window
→ candidate ground station
→ transfer
→ cloud processing

This plan may be conditional if no real tasking or reservation API exists.

## Onboard processing

Satellite acquisition
→ onboard model execution
→ prioritized downlink
→ result delivery

Mark infeasible or conditional unless a real provider exists.

The planner must:

1. Generate candidate plans.
2. Evaluate hard constraints.
3. Reject impossible plans.
4. Record rejection reasons.
5. Estimate duration.
6. Estimate data movement.
7. Estimate cost only when a source exists.
8. Rank feasible plans.
9. Select a recommendation.
10. Explain the recommendation in plain language.
11. Preserve all assumptions.
12. Produce deterministic results for the same inputs and source snapshot.

Do not use an LLM as the source of truth for feasibility.

An LLM may be used only to rewrite structured planner output into a customer-friendly explanation.

The structured planner must work without an LLM.

Acceptance criteria:

* At least three candidate plans are generated where relevant.
* Impossible plans are rejected explicitly.
* The selected plan is based on structured scoring.
* Every estimate has provenance.
* Tests cover deadline, cost, geography, unavailable provider, stale data, and missing catalog scenarios.

Commit message:

`feat: build source-backed mission feasibility and planning engine`

# Phase J: Create the mission result experience

Redesign `/missions/[id]` around customer value.

The result page must include:

## 1. Executive recommendation

Example:

“Recommended plan: existing imagery to U.S. cloud processing”

Explain:

* why it is recommended
* whether it is executable now
* what assumptions were used
* what integrations are missing

## 2. Feasibility summary

Display:

* feasible now
* feasible with provider access
* estimated only
* unavailable

## 3. Mission timeline

Show ordered steps with:

* start time
* duration
* truth status
* provider
* dependency
* current availability

## 4. Geographic visualization

Show only relevant objects:

* area of interest
* selected scene footprint
* relevant satellite track
* candidate ground stations
* communication windows
* destination region

## 5. Alternative plans

Comparison table:

* plan
* feasibility
* estimated total time
* estimated cost
* data movement
* access required
* key reason

## 6. Assumptions and sources

Show:

* source list
* retrieval timestamps
* orbital-data epoch
* pricing assumptions
* unavailable integrations
* stale inputs

## 7. Next actions

Generate practical actions such as:

* Connect provider account
* Request ground-station access
* Upload payload capabilities
* Confirm data residency
* Export plan
* Share with engineering team

## 8. Demo disclosure

Display clearly:

“This mission plan uses real public orbital and catalog data where available. Satellite tasking, provider reservation, onboard execution, and commercial guarantees are not performed unless explicitly marked as connected.”

Acceptance criteria:

* The page is understandable to a technical customer without reading documentation.
* Random simulated detections are no longer the main output.
* The recommendation is the dominant visual element.
* Alternative plans are easy to compare.
* Sources and assumptions are inspectable.

Commit message:

`feat: replace simulated job output with customer mission brief`

# Phase K: Add report export

Create exports for:

## PDF mission brief

Include:

* mission summary
* area and timeframe
* recommendation
* plan timeline
* alternative plans
* map image or static geographic summary
* assumptions
* source list
* truth-status legend
* missing integrations
* next actions
* generation timestamp

## JSON export

Include:

* mission input
* source snapshots
* candidate plans
* selected plan
* plan steps
* assumptions
* truth statuses
* rejection reasons
* source evidence

## Shareable private page

Use the ShareLink model.

Allow:

* read-only sharing
* expiration
* revocation
* copy share link

Acceptance criteria:

* PDF is readable and professional.
* JSON is valid and versioned.
* Shared links do not expose unrelated missions.
* Exported reports clearly disclose simulations and unavailable integrations.

Commit message:

`feat: add mission brief PDF JSON and private sharing`

# Phase L: Remove misleading simulated outputs

Audit all user-facing simulated output.

Remove or demote:

* fabricated ship detections
* arbitrary confidence scores
* fictional provider prices
* fictional node availability
* fictional onboard completion states
* random job result maps

Keep simulations only as curated examples.

Any remaining simulation must:

1. Be labeled SIMULATED.
2. Explain why it exists.
3. Never be mixed with real values without distinction.
4. Never appear to be customer-specific real output.

Create curated example missions under `/examples`.

Examples may include:

* Maritime monitoring
* Wildfire response
* Disaster imagery delivery
* Customer edge processing

Each example should state:

* which data is real
* which calculations are real
* which steps are estimated
* which steps are simulated
* which provider integrations are unavailable

Acceptance criteria:

* No user can reasonably mistake simulated execution for real execution.
* Curated examples remain visually compelling.
* The main customer workflow produces a mission plan, not fake detections.

Commit message:

`refactor: isolate simulations into clearly labeled examples`

# Phase M: Add lightweight real execution without GPUs

Do not build GPU inference.

Add one optional CPU-based execution path to prove that Nomos can execute a plan.

Implement a simple provider adapter for local or cloud CPU execution.

The first real executable tasks may include:

* fetch remote metadata
* copy an asset
* crop a GeoTIFF
* generate a thumbnail
* calculate image statistics
* calculate a checksum
* inspect raster dimensions
* convert metadata into JSON
* save a result artifact to object storage

Create an interface conceptually similar to:

```python
class ExecutionProvider:
    async def capabilities(self) -> ProviderCapabilities:
        ...

    async def estimate(self, task: ExecutionTask) -> ExecutionEstimate:
        ...

    async def submit(self, task: ExecutionTask, idempotency_key: str) -> ExternalJob:
        ...

    async def status(self, external_job_id: str) -> ExternalJobStatus:
        ...

    async def cancel(self, external_job_id: str) -> None:
        ...

    async def result(self, external_job_id: str) -> ExecutionResult:
        ...
```

Implement:

* `LocalCpuExecutionProvider`
* optionally `CloudCpuExecutionProvider`

Measure actual:

* transfer time
* execution duration
* input size
* output size
* storage location

Store measured values as OBSERVED.

Acceptance criteria:

* At least one real CPU task can execute end to end.
* The result is stored in R2 or local object storage.
* Actual measured duration is shown.
* Retries are idempotent.
* Failures are visible and recoverable.
* The planner distinguishes planned versus executed steps.

Commit message:

`feat: add lightweight real CPU execution provider`

# Phase N: Add provider registry and capability ingestion

Build a provider registry for future integrations.

Provider resources should support:

* provider name
* resource type
* API availability
* sandbox availability
* authentication required
* supported task types
* supported data formats
* geography
* pricing source
* capacity source
* current status
* data freshness
* contact information
* integration status

Integration statuses:

* public_data_only
* documented_api
* sandbox_requested
* sandbox_connected
* partner_connected
* simulated
* unavailable

Create an internal admin or configuration workflow for maintaining providers.

Do not expose secrets to the browser.

Allow provider information to come from:

* checked-in versioned configuration
* admin-managed records
* public API ingestion
* future provider heartbeats

Acceptance criteria:

* The planner uses the registry instead of hardcoded fictional nodes.
* Public information is clearly distinguished from live connected availability.
* A new provider can be added without changing planner core logic.

Commit message:

`feat: add extensible infrastructure provider registry`

# Phase O: Add telemetry and product analytics

Add product analytics that respect privacy.

Track:

* mission started
* mission completed
* plan generated
* data candidates found
* plan exported
* plan shared
* example viewed
* user returned
* provider connection requested
* planning failure reason

Do not record sensitive mission notes in analytics.

Add operational metrics:

* catalog-provider latency
* catalog-provider failures
* orbital-data freshness
* planner duration
* missions per status
* export failures
* share-link usage
* CPU execution success rate

Create an internal admin summary.

Acceptance criteria:

* Accelerator-relevant usage can be measured.
* Analytics do not expose mission content.
* Operational failures are observable.
* Events have documented schemas.

Commit message:

`feat: add privacy-safe product and planning analytics`

# Phase P: Add customer feedback and design-partner capture

Add a lightweight call to action after each generated plan:

“Was this plan useful?”

Collect:

* yes
* partly
* no
* optional comment

Add:

“Use this for a real mission”

Collect:

* name
* work email
* organization
* role
* mission type
* requested integration
* permission to contact

Do not require this before plan generation.

Create a simple internal view or export for leads.

Acceptance criteria:

* Users can provide feedback quickly.
* Interested organizations can request a design-partner conversation.
* Lead data is private.
* Spam protection is included.

Commit message:

`feat: add mission feedback and design partner requests`

# Phase Q: Improve documentation and SDK

Update documentation around the new product.

Create:

* `docs/mission-planner-overview.md`
* `docs/data-sources.md`
* `docs/truth-statuses.md`
* `docs/planning-engine.md`
* `docs/privacy-model.md`
* `docs/provider-integrations.md`
* `docs/demo-limitations.md`
* `docs/accelerator-demo-script.md`

Update the Python SDK with simple methods:

```python
mission = client.missions.create(...)
plan = client.missions.generate_plan(mission.id)
report = client.missions.export_pdf(mission.id)
```

The SDK should not require users to understand internal database models.

Add typed errors for:

* no catalog data
* no feasible plan
* upstream provider unavailable
* unauthorized mission
* expired share link
* stale orbital data
* invalid geographic input

Acceptance criteria:

* A developer can create and retrieve a mission plan with a short SDK example.
* Documentation clearly explains real versus simulated features.
* Public API examples use customer terminology.

Commit message:

`docs: document mission planner APIs data sources and limitations`

# Phase R: Create accelerator-ready curated demos

Create three high-quality curated missions.

## Demo 1: Existing Sentinel imagery

Inputs:

* New York Harbor
* recent Sentinel-1 data
* deadline
* U.S. data residency

Output:

* real data candidates
* recommended route
* real scene metadata
* calculated planning result
* clear unavailable onboard option

## Demo 2: Disaster response

Inputs:

* recent affected area
* urgent deadline
* compare existing imagery, new acquisition, and cloud processing

Output:

* feasibility comparison
* assumptions
* timeline
* next actions

## Demo 3: Customer edge processing

Inputs:

* real scene
* customer-controlled CPU node
* privacy preference

Output:

* cloud versus customer edge comparison
* one real lightweight CPU execution
* measured duration
* resulting artifact

Create a 90-second demo script in:

`docs/accelerator-demo-script.md`

The script should show:

1. Customer problem.
2. Mission input.
3. Real data discovery.
4. Real orbital or infrastructure calculation.
5. Feasible and rejected plans.
6. Recommendation.
7. Truth labels.
8. Exported report.
9. Clear next provider integration.

Acceptance criteria:

* Each demo runs reliably.
* No hidden manual database edits are required.
* Each demo has reset and seed instructions.
* Every simulated step is disclosed.

Commit message:

`feat: add accelerator-ready mission planning demos`

# Phase S: Security and privacy review

Perform a security review.

Check:

* mission authorization
* anonymous session handling
* cookie security
* share-token entropy
* token hashing
* link revocation
* rate limiting
* input validation
* GeoJSON validation
* file upload restrictions
* object-storage permissions
* signed URL expiration
* data retention
* log redaction
* secrets handling
* CORS
* CSRF considerations
* SSRF risks in remote asset retrieval
* SQL injection
* public API enumeration
* export authorization

Create:

`docs/security-review.md`

Fix all high-severity findings.

Acceptance criteria:

* No public mission enumeration.
* No cross-session mission access.
* Remote URLs are allowlisted or safely validated.
* Sensitive tokens never appear in logs.
* Security tests cover the primary access paths.

Commit message:

`security: harden private mission planning workflow`

# Phase T: Final validation

Run the complete validation suite.

Required checks:

## Backend

* ruff
* mypy
* pytest
* migrations from empty database
* migrations from current demo database
* API contract tests
* authorization tests
* planner tests
* catalog-provider tests
* export tests
* execution-provider tests

## Frontend

* lint
* typecheck
* production build
* responsive tests
* accessibility checks
* mission builder flow
* result page
* share page
* example pages

## Infrastructure

* Docker build
* docker-compose startup
* health endpoints
* readiness endpoints
* object storage
* Redis worker
* database migration
* scheduled orbital-data refresh
* scheduled demo cleanup

## Manual acceptance flow

Verify:

1. Open the homepage.
2. Understand product within five seconds.
3. Create a private anonymous mission.
4. Search real satellite data.
5. Generate multiple plans.
6. See rejected routes and reasons.
7. See truth labels and sources.
8. Export PDF and JSON.
9. Create private share link.
10. Open share link in another browser.
11. Confirm unrelated missions remain inaccessible.
12. Execute one lightweight CPU step.
13. See measured values.
14. Submit product feedback.
15. Request design-partner contact.

Create:

`docs/final-validation-report.md`

Include:

* completed features
* tests run
* known limitations
* remaining simulations
* unavailable integrations
* deployment instructions
* accelerator demo instructions
* next recommended provider integration

Commit message:

`chore: complete mission planner validation and release documentation`

# Final deployment goal

Deploy the final product with:

* public marketing homepage
* private anonymous mission workspace
* curated public examples
* real satellite catalog search
* real orbital-data provenance
* source-backed mission planning
* truth-status labels
* downloadable mission report
* private sharing
* optional lightweight CPU execution
* analytics
* design-partner capture

Do not block final deployment on:

* GPU processing
* onboard satellite compute
* satellite tasking
* ground-station booking
* billing
* full organization accounts
* enterprise authentication
* marketplace settlement

These are later phases.

# Final product claim

The final product may truthfully claim:

“Nomos turns a space-data objective into a source-backed infrastructure plan. It searches real public data catalogs, calculates orbital and communication constraints, compares feasible execution paths, explains assumptions, and produces a shareable technical mission brief.”

The final product must not claim:

* that AI ran onboard a satellite,
* that a satellite was tasked,
* that a ground station was reserved,
* that commercial pricing is guaranteed,
* that private provider availability is live,
* that execution occurred unless a real provider adapter completed it.

# Completion condition

Do not declare the project complete until:

1. The private customer mission flow works end to end.
2. Real catalog data is visible.
3. The planner produces multiple structured plans.
4. Impossible plans are rejected clearly.
5. Every major value has provenance and truth status.
6. User missions are private.
7. Reports can be exported and shared.
8. One real lightweight CPU execution path works.
9. All tests and builds pass.
10. Documentation and final validation report are complete.

When everything is complete, produce a concise final summary containing:

* what was built,
* what is real,
* what remains simulated,
* how to run locally,
* how to deploy,
* how to run the accelerator demo,
* the highest-priority next provider integration.
</user_query>
