import dynamic from "next/dynamic";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { DemoLauncher } from "@/components/jobs/DemoLauncher";
import { FadeIn, Stagger, StaggerItem } from "@/components/motion/primitives";

const OrbitalScene = dynamic(
  () => import("@/components/orbital/OrbitalScene"),
  { ssr: false }
);

const specBlocks = [
  {
    index: "001",
    title: "Request",
    body: "A versioned job spec: sensor, area of interest, priority, budget. One POST, no ceremony.",
    stat: "POST /v1/jobs"
  },
  {
    index: "002",
    title: "Score",
    body: "Every orbital and cloud node is scored on model support, latency, cost, availability, and contact windows.",
    stat: "7 weighted factors"
  },
  {
    index: "003",
    title: "Route",
    body: "The winning node is selected deterministically. The decision is hashed so any audit can replay it bit-for-bit.",
    stat: "sha256 decision hash"
  },
  {
    index: "004",
    title: "Return",
    body: "Detections come back as GeoJSON with signed artifact URLs. Inspect the map, the logs, and the route that produced them.",
    stat: "GeoJSON + signed URLs"
  }
];

const missionPhases = [
  { label: "Submit", detail: "Job accepted, persisted, enqueued" },
  { label: "Route", detail: "Candidates scored, node selected" },
  { label: "Execute", detail: "Inference runs on the chosen node" },
  { label: "Downlink", detail: "Results pass a contact window" },
  { label: "Complete", detail: "Artifacts signed and delivered" }
];

export default function HomePage() {
  return (
    <div className="pb-10">
      {/* ---------- hero ---------- */}
      <section className="relative">
        <OrbitalScene className="pointer-events-none absolute inset-0 -top-24 h-[calc(100%+6rem)] w-full opacity-90" />
        <div className="page-shell relative">
          <div className="grid min-h-[calc(100vh-140px)] items-center gap-12 py-14 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <FadeIn>
                <p className="chart-label flex items-center gap-2.5 text-gold">
                  <NomosMark size={22} />
                  Orbital compute orchestration
                </p>
              </FadeIn>
              <FadeIn delay={0.08}>
                <h1 className="display mt-6 text-5xl leading-[1.04] text-cream sm:text-6xl lg:text-7xl">
                  Order, for the
                  <br />
                  orbital age.
                </h1>
              </FadeIn>
              <FadeIn delay={0.16}>
                <p className="mt-7 max-w-xl text-lg leading-8 text-muted">
                  Nomos routes space-data AI jobs across satellites and clouds —
                  scoring every node, explaining every decision, signing every
                  result. Try it right now, on the live network.
                </p>
              </FadeIn>
              <FadeIn delay={0.24}>
                <div className="mt-9 flex flex-wrap items-center gap-5">
                  <Link
                    className="rounded-xl border border-line px-5 py-3 text-sm font-medium text-cream transition hover:border-gold/50 hover:text-gold-bright"
                    href="/network"
                  >
                    Explore the network
                  </Link>
                  <Link
                    className="text-sm text-muted underline decoration-line underline-offset-4 transition hover:text-cream"
                    href="/docs"
                  >
                    Read the API docs
                  </Link>
                </div>
              </FadeIn>
            </div>

            <FadeIn className="flex justify-center lg:justify-end" delay={0.2} y={20}>
              <DemoLauncher />
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ---------- problem (light editorial island) ---------- */}
      <section className="page-shell mt-10">
        <FadeIn>
          <div className="editorial mx-auto max-w-3xl px-8 py-12 sm:px-14 sm:py-16">
            <p className="chart-label text-teal-deep">The problem</p>
            <h2 className="display mt-5 text-3xl leading-snug text-ink sm:text-4xl">
              Satellites collect more than they can send home.
            </h2>
            <div className="mt-6 space-y-5 text-[17px] leading-8 text-ink/75">
              <p>
                Every pass over a ground station is a scarce, minutes-long
                window. Raw imagery queues for hours to downlink, then costs
                again to process in the cloud. Meanwhile, compute in orbit sits
                idle between captures.
              </p>
              <p>
                Nomos treats orbit like a scheduling problem. Run the model
                where it is cheapest and fastest — on the satellite, at the
                edge, or in the cloud — and downlink only the answer.
              </p>
            </div>
          </div>
        </FadeIn>
      </section>

      {/* ---------- how it works (glass spec grid) ---------- */}
      <section className="page-shell mt-28">
        <FadeIn>
          <p className="chart-label text-gold">How it works</p>
          <h2 className="display mt-4 max-w-2xl text-3xl text-cream sm:text-4xl">
            One request. Every path considered.
          </h2>
        </FadeIn>
        <Stagger className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {specBlocks.map((block) => (
            <StaggerItem key={block.index}>
              <div className="glass glass-hover h-full p-6">
                <p className="metric-value text-xs text-gold">{block.index}</p>
                <h3 className="mt-4 text-xl font-semibold text-cream">
                  {block.title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-muted">{block.body}</p>
                <p className="metric-value mt-5 border-t border-line pt-4 text-xs text-teal">
                  {block.stat}
                </p>
              </div>
            </StaggerItem>
          ))}
        </Stagger>
      </section>

      {/* ---------- mission phases timeline ---------- */}
      <section className="page-shell mt-28">
        <FadeIn>
          <div className="glass p-8 sm:p-10">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="chart-label text-gold">Mission lifecycle</p>
                <h2 className="display mt-3 text-2xl text-cream sm:text-3xl">
                  Five phases, fully observable
                </h2>
              </div>
              <Link
                className="text-sm text-muted underline decoration-line underline-offset-4 transition hover:text-cream"
                href="/jobs"
              >
                Watch one live →
              </Link>
            </div>

            <div className="mt-12 grid gap-8 sm:grid-cols-5">
              {missionPhases.map((phase, index) => (
                <div className="relative" key={phase.label}>
                  <div className="flex items-center gap-3">
                    <span className="metric-value text-xs text-gold">
                      {String(index + 1).padStart(3, "0")}
                    </span>
                    {index < missionPhases.length - 1 ? (
                      <span className="hidden h-px flex-1 bg-gradient-to-r from-gold/40 to-transparent sm:block" />
                    ) : null}
                  </div>
                  <h3 className="mt-4 text-base font-semibold text-cream">
                    {phase.label}
                  </h3>
                  <p className="mt-2 text-xs leading-5 text-muted">
                    {phase.detail}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </FadeIn>
      </section>

      {/* ---------- for developers (light island + code) ---------- */}
      <section className="page-shell mt-28">
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <FadeIn>
            <div className="editorial h-full px-8 py-12 sm:px-12">
              <p className="chart-label text-teal-deep">For developers</p>
              <h2 className="display mt-5 text-3xl leading-snug text-ink">
                A control plane, not a black box.
              </h2>
              <p className="mt-5 text-[17px] leading-8 text-ink/75">
                Everything the console shows, the API returns. Routing scores,
                constraint failures, lifecycle events, replayable decision
                hashes — all public, all documented.
              </p>
              <Link
                className="mt-8 inline-flex items-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-semibold text-cream transition hover:bg-ink/85"
                href="/docs"
              >
                Open the docs
              </Link>
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <pre className="code-block h-full !text-[13px]">
              {`$ curl -X POST https://api.nomosorbital.com/v1/jobs \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer oc_demo_public" \\
    -d '{
      "job_type": "ship_detection",
      "sensor": "SAR",
      "priority": "fastest",
      "compute_preference": "orbital_if_available",
      "max_cost_usd": 500,
      "area_of_interest": {
        "type": "bbox",
        "coordinates": [-74.3, 40.3, -73.5, 41.0]
      }
    }'

{
  "job": { "id": "job_…", "status": "queued" },
  "routing_decision": null
}`}
            </pre>
          </FadeIn>
        </div>
      </section>
    </div>
  );
}
