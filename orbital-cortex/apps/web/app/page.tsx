import dynamic from "next/dynamic";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { DemoLauncher } from "@/components/jobs/DemoLauncher";
import { ImmersiveScrollBand } from "@/components/motion/ImmersiveScrollBand";
import { FadeIn } from "@/components/motion/primitives";

const SideScrollDisk = dynamic(
  () => import("@/components/motion/SideScrollDisk").then((m) => m.SideScrollDisk),
  { ssr: false }
);

const AboutScrollStory = dynamic(
  () =>
    import("@/components/about/AboutScrollStory").then((m) => m.AboutScrollStory),
  { ssr: false }
);

const SdkResultPreview = dynamic(
  () =>
    import("@/components/platform/SdkResultPreview").then((m) => m.SdkResultPreview),
  { ssr: false, loading: () => <div className="aave-glass min-h-[280px] animate-pulse" /> }
);

const OrbitalScene = dynamic(
  () => import("@/components/orbital/OrbitalScene"),
  { ssr: false }
);

const pipeline = [
  { step: "01", title: "Request", detail: "POST /v1/jobs" },
  { step: "02", title: "Score", detail: "7 weighted factors" },
  { step: "03", title: "Route", detail: "sha256 replay hash" },
  { step: "04", title: "Return", detail: "GeoJSON + signed URLs" }
];

export default function HomePage() {
  return (
    <div className="relative pb-6">
      <SideScrollDisk />

      <section className="relative overflow-hidden">
        <OrbitalScene className="pointer-events-none absolute inset-0 -top-16 h-[calc(100%+4rem)] w-full opacity-45" />
        <div className="page-shell relative">
          <div className="grid min-h-[calc(100vh-110px)] items-center gap-8 py-10 lg:grid-cols-[1.05fr_0.95fr]">
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
                <p className="prose-compact mt-4 max-w-md text-muted">
                  Nomos routes space-data AI jobs across satellites and clouds,
                  scoring every node, explaining every decision, signing every
                  result.
                </p>
              </FadeIn>
              <FadeIn delay={0.18}>
                <div className="mt-5 flex flex-wrap items-center gap-3">
                  <Link className="btn-gold" href="/#demo">
                    Run live demo
                  </Link>
                  <Link
                    className="text-sm text-muted transition hover:text-gold-bright"
                    href="/network"
                  >
                    Network console →
                  </Link>
                </div>
              </FadeIn>
            </div>
            <FadeIn className="flex justify-center lg:justify-end" delay={0.16} y={12}>
              <DemoLauncher />
            </FadeIn>
          </div>
        </div>
      </section>

      <section className="section-gap page-shell">
        <SdkResultPreview />
      </section>

      <section className="section-gap page-shell">
        <p className="chart-label text-gold">Pipeline</p>
        <div className="aave-glass mt-4 grid sm:grid-cols-4">
          {pipeline.map((item) => (
            <div className="border-b border-white/8 px-4 py-4 last:border-b-0 sm:border-b-0 sm:border-r sm:last:border-r-0" key={item.step}>
              <p className="metric-value text-[11px] text-gold">{item.step}</p>
              <p className="mt-1 text-sm font-medium text-cream">{item.title}</p>
              <p className="metric-value mt-1 text-[11px] text-muted">{item.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <ImmersiveScrollBand
        imageAlt="Mission control corridor of displays"
        imageSrc="/images/control-room-tunnel.png"
        scrollHeight="130vh"
      >
        <FadeIn>
          <div className="aave-glass max-w-lg p-6 sm:p-7">
            <p className="chart-label text-gold">The problem</p>
            <h2 className="display mt-3 text-2xl leading-tight text-cream sm:text-3xl">
              Satellites collect more than they can send home.
            </h2>
            <p className="prose-compact mt-4 text-muted">
              Every ground-station pass is minutes long. Nomos runs inference where
              it is fastest and downlinks only the answer.
            </p>
          </div>
        </FadeIn>
      </ImmersiveScrollBand>

      <section className="section-gap" id="about">
        <div className="page-shell mb-1">
          <p className="chart-label text-gold">About</p>
          <h2 className="display mt-2 text-2xl text-cream sm:text-3xl">
            Nomos, the Golden Record, Columbia plasma lab.
          </h2>
        </div>
        <AboutScrollStory />
      </section>

      <section className="section-gap page-shell pb-4">
        <div className="grid gap-5 lg:grid-cols-2">
          <FadeIn>
            <div className="aave-glass h-full p-6">
              <p className="chart-label text-gold">For developers</p>
              <h2 className="display mt-2 text-xl text-cream">
                A control plane, not a black box.
              </h2>
              <p className="prose-compact mt-3 text-muted">
                Routing scores, lifecycle events, replayable decision hashes.
                Public and documented.
              </p>
              <Link className="btn-gold-outline mt-4 inline-flex" href="/docs">
                API reference
              </Link>
            </div>
          </FadeIn>
          <FadeIn delay={0.06}>
            <pre className="code-block h-full !text-[12px]">
              {`$ curl -X POST https://api.nomosorbital.com/v1/jobs \\
    -H "Authorization: Bearer oc_demo_public" \\
    -H "Content-Type: application/json" \\
    -d '{ "job_type": "ship_detection", ... }'`}
            </pre>
          </FadeIn>
        </div>
      </section>
    </div>
  );
}
