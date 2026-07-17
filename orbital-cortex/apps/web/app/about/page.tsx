import dynamic from "next/dynamic";
import Image from "next/image";

import { DemoBoundary } from "@/components/archive/ArchivePrimitives";
import { AboutContent } from "@/components/about/AboutContent";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { LiquidSection } from "@/components/liquid/LiquidSection";

const AboutScrollStory = dynamic(
  () =>
    import("@/components/about/AboutScrollStory").then((module) => module.AboutScrollStory),
  { ssr: false }
);

export default function AboutPage() {
  return (
    <div className="pb-6">
      <div className="relative overflow-hidden">
        <div className="absolute inset-0">
          <Image
            alt=""
            aria-hidden
            className="object-cover object-center opacity-30"
            fill
            priority
            sizes="100vw"
            src="/images/voyager-heritage.png"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-void/50 via-void/90 to-void" />
        </div>
        <LiquidSection className="relative py-12 md:py-16" orbs={false}>
          <div className="page-shell">
            <FadeIn>
              <p className="chart-label text-gold">About</p>
              <h1 className="display mt-2 max-w-2xl text-3xl leading-tight text-cream md:text-5xl">
                We make orbital decisions legible.
              </h1>
              <p className="prose-compact mt-3 max-w-xl text-silver">
                Nomos is the orchestration layer above satellites, ground stations,
                and cloud compute. Submit one job, compare every eligible route, and
                preserve why the winner was chosen.
              </p>
              <div className="mt-6">
                <LiquidButton href="/#demo" variant="primary">
                  Run live demo
                </LiquidButton>
              </div>
            </FadeIn>
          </div>
        </LiquidSection>
      </div>

      <div className="page-shell mt-6">
        <DemoBoundary />
      </div>

      <section className="mt-12">
        <div className="page-shell">
          <p className="chart-label text-gold">The Golden Record lineage</p>
          <h2 className="display mt-2 max-w-2xl text-3xl text-cream">
            Scroll to turn the record.
          </h2>
          <p className="prose-compact mt-3 max-w-2xl text-muted">
            The original spinning record belongs here, with the story of Nomos,
            Voyager, and why scarce bandwidth demands distilled signal.
          </p>
        </div>
        <AboutScrollStory />
      </section>

      <LiquidSection className="section-gap page-shell">
        <AboutContent />
      </LiquidSection>

      <LiquidSection className="section-gap page-shell">
        <LiquidCard className="relative overflow-hidden">
          <div className="absolute right-5 top-5 font-mono text-[10px] tracking-[0.16em] text-vermilion">
            ESSAY 01
          </div>
          <p className="chart-label text-gold">The long mission</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream">
            The Final Symposium
          </h2>
          <p className="prose-compact mt-4 max-w-2xl text-silver">
            A founder-authored inquiry into entropy, memory, human corrigibility,
            and why intelligence should remain legible as it moves farther from Earth.
            It is a philosophical foundation, not a product roadmap.
          </p>
          <div className="mt-5">
            <LiquidButton href="/about/final-symposium" variant="outline">
              Read the essay
            </LiquidButton>
          </div>
        </LiquidCard>
      </LiquidSection>

      <LiquidSection className="section-gap page-shell">
        <LiquidCard>
          <p className="chart-label text-gold">Field register</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream">Calendar</h2>
          <p className="prose-compact mt-4 max-w-2xl text-silver">
            Potential presence, application windows, eligibility research, and live
            GitHub search for adjacent open-source work. Presence is potential until
            marked planned.
          </p>
          <div className="mt-5">
            <LiquidButton href="/calendar" variant="outline">
              Open calendar
            </LiquidButton>
          </div>
        </LiquidCard>
      </LiquidSection>
    </div>
  );
}
