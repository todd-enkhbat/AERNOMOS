import dynamic from "next/dynamic";
import Image from "next/image";

import {
  ArchiveHeader,
  CelestialDivider,
  DemoBoundary,
  ProvenancePlate
} from "@/components/archive/ArchivePrimitives";
import { NomosMark } from "@/components/brand/NomosMark";
import { DemoLauncher } from "@/components/jobs/DemoLauncher";
import { ImmersiveScrollBand } from "@/components/motion/ImmersiveScrollBand";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton, LiquidCard, LiquidSection } from "@/components/liquid";

const SdkResultPreview = dynamic(
  () =>
    import("@/components/platform/SdkResultPreview").then((m) => m.SdkResultPreview),
  { ssr: false, loading: () => <div className="liquid-glass liquid-glass--card min-h-[280px] animate-pulse" /> }
);

const OrbitalScene = dynamic(
  () => import("@/components/orbital/OrbitalScene"),
  {
    ssr: false,
    loading: () => (
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_45%,rgba(201,162,39,0.1),transparent_35%)]" />
    )
  }
);

const pipeline = [
  { step: "01", title: "Request", detail: "Describe the job, area, budget, and priority.", proof: "POST /v1/jobs" },
  { step: "02", title: "Score", detail: "Compare eligible compute targets across seven factors.", proof: "7 weighted factors" },
  { step: "03", title: "Route", detail: "Select a path and preserve why it won.", proof: "sha256 replay hash" },
  { step: "04", title: "Return", detail: "Deliver machine-readable results and artifacts.", proof: "GeoJSON + signed URLs" }
];

export default function HomePage() {
  return (
    <div className="relative pb-6">
      <LiquidSection className="relative overflow-hidden">
        <OrbitalScene className="pointer-events-none absolute inset-0 -top-16 h-[calc(100%+4rem)] w-full opacity-45" />
        <div className="page-shell relative">
          <div className="grid gap-8 py-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:py-12">
            <div>
              <FadeIn>
                <p className="chart-label flex items-center gap-2 text-silver">
                  <NomosMark size={20} />
                  Orbital compute orchestration
                </p>
              </FadeIn>
              <FadeIn delay={0.06}>
                <h1 className="display mt-4 text-[2.75rem] leading-[1.02] text-cream sm:text-6xl lg:text-[4.25rem]">
                  Order, for the
                  <br />
                  <span className="gold-shine">orbital age.</span>
                </h1>
              </FadeIn>
              <FadeIn delay={0.12}>
                <p className="prose-compact mt-4 max-w-md text-silver">
                  Submit a satellite-data AI job. Nomos compares orbital and cloud
                  compute candidates, selects a route, and shows exactly why.
                </p>
              </FadeIn>
              <FadeIn delay={0.18}>
                <div className="mt-5 flex flex-wrap items-center gap-3">
                  <LiquidButton href="/#demo" variant="primary">
                    Run live demo
                  </LiquidButton>
                  <LiquidButton href="/network" variant="ghost">
                    Network console →
                  </LiquidButton>
                </div>
              </FadeIn>
            </div>
            <FadeIn className="flex justify-center lg:justify-end" delay={0.16} y={12}>
              <DemoLauncher />
            </FadeIn>
          </div>

          <DemoBoundary />

          <div className="mt-10 border-t border-gold/10 pt-10 lg:mt-12 lg:pt-12" id="sdk-output">
            <SdkResultPreview />
          </div>
        </div>
      </LiquidSection>

      <LiquidSection className="mt-8 page-shell">
        <ArchiveHeader
          description="One request becomes an explainable route and a machine-readable return. Each step leaves evidence you can inspect."
          eyebrow="How it works"
          index="PLATE 01"
          title="Request. Score. Route. Return."
        />
        <figure className="relative mt-4 min-h-[260px] overflow-hidden rounded-t-[22px] border border-b-0 border-gold/16 sm:min-h-[340px]">
          <Image
            alt="Celestial routing atlas with concentric orbital paths"
            className="object-cover object-center"
            fill
            sizes="(max-width: 1100px) 100vw, 1100px"
            src="/images/nomos-lithograph-hero.jpg"
          />
          <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(5,5,6,0.02),rgba(5,5,6,0.18)_50%,rgba(5,5,6,0.92))]" />
          <figcaption className="absolute inset-x-0 bottom-0 flex flex-wrap items-end justify-between gap-3 p-5 sm:p-6">
            <div>
              <p className="chart-label text-gold">Nomos routing atlas</p>
              <p className="mt-2 max-w-xl text-sm leading-6 text-cream/80">
                Many possible paths collapse into one selected route and one preserved
                explanation.
              </p>
            </div>
            <p className="metric-value text-[10px] text-silver">PLATE 01 · DECISION GEOMETRY</p>
          </figcaption>
        </figure>
        <LiquidCard className="!rounded-t-none !p-0">
          <div className="grid sm:grid-cols-4">
            {pipeline.map((item) => (
              <div
                className="border-b border-white/8 px-4 py-4 last:border-b-0 sm:border-b-0 sm:border-r sm:last:border-r-0"
                key={item.step}
              >
                <p className="metric-value text-[11px] text-gold">{item.step}</p>
                <p className="mt-1 text-sm font-medium text-cream">{item.title}</p>
                <p className="mt-2 text-xs leading-5 text-muted">{item.detail}</p>
                <p className="metric-value mt-2 text-[10px] text-silver">{item.proof}</p>
              </div>
            ))}
          </div>
        </LiquidCard>
      </LiquidSection>

      <ImmersiveScrollBand
        posterSrc="/images/control-room-tunnel.png"
        scrollHeight="130vh"
        videoSrc="/videos/video-immersive.optimized.mp4"
      >
        <FadeIn>
          <div className="max-w-lg">
            <LiquidCard>
              <p className="chart-label text-gold">The problem</p>
              <h2 className="display mt-3 text-2xl leading-tight text-cream sm:text-3xl">
                Satellites collect more than they can send home.
              </h2>
              <p className="prose-compact mt-4 text-muted">
                Every ground-station pass is minutes long. Nomos runs inference where
                it is fastest and downlinks only the answer.
              </p>
              <div className="mt-5 grid gap-2 sm:grid-cols-2">
                <ProvenancePlate
                  label="Physics"
                  tone="gold"
                  value="SGP4 contact windows"
                />
                <ProvenancePlate
                  label="Execution"
                  value="Simulated compute nodes"
                />
              </div>
            </LiquidCard>
          </div>
        </FadeIn>
      </ImmersiveScrollBand>

      <LiquidSection className="section-gap relative z-[2] page-shell pb-4">
        <CelestialDivider label="CONTROL PLANE" />
        <FadeIn>
          <div className="grid items-start gap-8 border-t border-gold/12 pt-8 lg:grid-cols-[0.95fr_1.05fr] lg:gap-12">
            <div>
              <p className="chart-label text-gold">For developers</p>
              <h2 className="display mt-2 text-2xl text-cream sm:text-3xl">
                A control plane, not a black box.
              </h2>
              <p className="prose-compact mt-3 max-w-md text-muted">
                Routing scores, lifecycle events, replayable decision hashes.
                Public and documented.
              </p>
              <p className="prose-compact mt-4 max-w-md text-silver">
                The Golden Record was meaning compressed for distance. Nomos
                applies the same discipline to orbital data: preserve the useful
                signal, make the route legible, keep a record of the decision.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <LiquidButton href="/docs" variant="outline">
                  API reference
                </LiquidButton>
                <LiquidButton href="/about" variant="ghost">
                  Read our story →
                </LiquidButton>
              </div>
            </div>
            <pre className="code-block !text-[12px]">
              {`$ curl -X POST https://api.nomosorbital.com/v1/jobs \\
    -H "Authorization: Bearer oc_demo_public" \\
    -H "Content-Type: application/json" \\
    -d '{ "job_type": "ship_detection", ... }'`}
            </pre>
          </div>
        </FadeIn>
      </LiquidSection>
    </div>
  );
}
