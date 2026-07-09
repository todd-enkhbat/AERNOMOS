import Image from "next/image";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { FadeIn } from "@/components/motion/primitives";

const pillars = [
  {
    label: "Nomos",
    title: "Order among the stars",
    body: [
      "Nomos (νόμος) is Greek for law, custom, and the ordering principle behind how things are arranged. In orbital infrastructure, the hard problem is not raw compute. It is scheduling under constraints: contact windows, downlink budgets, model compatibility, and auditability.",
      "Nomos Orbital is the control plane that imposes that order. One request enters the network. Every candidate node is scored. The winning route is deterministic, hashed, and replayable."
    ]
  },
  {
    label: "Golden Record",
    title: "Distilled signal across distance",
    body: [
      "In 1977, NASA bolted a gold-plated copper phonograph to Voyager. The Golden Record carried the Sounds of Earth: music, greetings, and instructions for playback, encoded so a distant civilization could reconstruct meaning from a single artifact.",
      "Our mark is that disc. Orbital AI faces the same constraint: bandwidth is scarce, passes are brief, and only the answer should cross the link. Nomos routes inference where it belongs and downlinks results, not raw noise."
    ]
  },
  {
    label: "Columbia",
    title: "Plasma lab roots",
    body: [
      "Nomos grew out of Columbia plasma physics research: high-energy plasmas, precision instrumentation, and the discipline of measuring what you cannot see directly. Tokamaks and satellite constellations both demand closed-loop control over hostile, noisy environments.",
      "That background shapes the product. Routing is physics-aware scheduling. Every job emits a signed event log the way a lab run emits a shot record. The console is a mission control surface, not a marketing shell."
    ]
  }
];

export function AboutContent({ compact = false }: { compact?: boolean }) {
  return (
    <>
      <div className={`grid gap-4 ${compact ? "lg:grid-cols-3" : "gap-5"}`}>
        {pillars.map((pillar, index) => (
          <FadeIn delay={index * 0.06} key={pillar.label}>
            <article className="glass glass-hover h-full p-5 sm:p-6">
              <p className="chart-label text-gold">{pillar.label}</p>
              <h3
                className={`display mt-2 leading-tight text-cream ${
                  compact ? "text-lg" : "text-xl sm:text-2xl"
                }`}
              >
                {pillar.title}
              </h3>
              <div className="prose-compact mt-3 text-muted">
                {pillar.body.map((paragraph) => (
                  <p key={paragraph.slice(0, 32)}>{paragraph}</p>
                ))}
              </div>
            </article>
          </FadeIn>
        ))}
      </div>

      {!compact ? (
        <FadeIn className="mt-5">
          <div className="glass overflow-hidden">
            <div className="grid lg:grid-cols-[0.95fr_1.05fr]">
              <div className="relative min-h-[240px] lg:min-h-[320px]">
                <Image
                  alt="NASA tape reels beside the Voyager Golden Record and spacecraft"
                  className="object-cover object-center"
                  fill
                  sizes="(max-width: 1024px) 100vw, 50vw"
                  src="/images/voyager-heritage.png"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent to-void/60 lg:bg-gradient-to-l lg:from-void/40 lg:to-transparent" />
              </div>
              <div className="flex flex-col justify-center p-5 sm:p-7">
                <div className="flex items-center gap-3">
                  <NomosMark size={36} />
                  <div>
                    <p className="text-sm font-semibold text-cream">Nomos Orbital</p>
                    <p className="chart-label text-muted-dark">est. among the stars</p>
                  </div>
                </div>
                <p className="prose-compact mt-4 text-muted">
                  We are building the orchestration layer for space-data AI: submit a
                  job once, route it across orbital and cloud compute, inspect every
                  score, and retrieve signed artifacts. The live demo on this site runs
                  against production infrastructure at api.nomosorbital.com.
                </p>
                <p className="prose-compact mt-3 text-muted">
                  The repo behind the product is AERNOMOS. The company you interact
                  with is Nomos Orbital. Same stack, same API, one name on the door.
                </p>
                <div className="mt-5 flex flex-wrap gap-3">
                  <Link
                    className="rounded-xl bg-gold px-4 py-2.5 text-sm font-semibold text-void transition hover:bg-gold-bright"
                    href="/#demo"
                  >
                    Run live demo
                  </Link>
                  <Link
                    className="rounded-xl border border-white/15 px-4 py-2.5 text-sm font-medium text-cream transition hover:border-white/25"
                    href="/docs"
                  >
                    API reference
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </FadeIn>
      ) : null}
    </>
  );
}
