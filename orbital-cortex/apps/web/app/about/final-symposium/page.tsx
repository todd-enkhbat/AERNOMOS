import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

import {
  ArchiveHeader,
  CelestialDivider,
  ProvenancePlate
} from "@/components/archive/ArchivePrimitives";
import { LiquidCard } from "@/components/liquid/LiquidCard";

export const metadata: Metadata = {
  title: "The Final Symposium",
  description:
    "A founder-authored inquiry into entropy, memory, human corrigibility, and the long mission behind Nomos Orbital."
};

const foundations = [
  {
    index: "I",
    title: "Human flourishing",
    body:
      "Technology earns its place by expanding human agency, understanding, and the capacity to create. Intelligence is valuable not as spectacle, but because it lets people choose and pursue meaning with greater freedom."
  },
  {
    index: "II",
    title: "Information continuity",
    body:
      "Civilizations are memory systems. Oral tradition, books, laboratories, and networks each delay forgetting. None defeats impermanence. The honest task is to preserve what matters long enough for another mind to receive, question, and improve it."
  },
  {
    index: "III",
    title: "Space and time",
    body:
      "Moving knowledge beyond Earth is not an escape from the human condition. It is an extension of responsibility. Systems operating across distance should remain legible, corrigible, and accountable to the people whose missions they serve."
  }
];

export default function FinalSymposiumPage() {
  return (
    <article className="pb-12">
      <header className="relative min-h-[72dvh] overflow-hidden">
        <Image
          alt="Engraved celestial atlas showing orbital paths converging on a distant gathering"
          className="object-cover"
          fill
          priority
          sizes="100vw"
          src="/images/final-symposium-atlas.jpg"
          unoptimized
        />
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(5,5,6,0.18),rgba(5,5,6,0.7)_52%,#050506_96%)]" />
        <div className="page-shell relative flex min-h-[72dvh] items-end pb-12 pt-28">
          <div className="max-w-3xl">
            <p className="chart-label text-gold">Founder essay · Philosophical foundation</p>
            <h1 className="display mt-4 text-4xl leading-[1.02] text-cream sm:text-6xl">
              The Final Symposium
            </h1>
            <p className="prose-compact mt-5 max-w-2xl text-silver">
              A chosen founding myth for a universe shaped by entropy. What should
              intelligence preserve, how should it correct itself, and what stories
              would we hope to carry to the farthest gathering?
            </p>
          </div>
        </div>
      </header>

      <div className="page-shell">
        <div className="mt-6 grid gap-3 md:grid-cols-2">
          <ProvenancePlate
            detail="This essay describes a long-horizon intellectual lineage."
            label="Register"
            tone="cobalt"
            value="Philosophy, not product roadmap"
          />
          <ProvenancePlate
            detail="Nomos today is a deployed orchestration demo with simulated execution."
            label="Present work"
            tone="gold"
            value="Make orbital systems legible"
          />
        </div>

        <section className="mx-auto mt-16 max-w-3xl">
          <ArchiveHeader
            description="Institutions do not defeat impermanence. They delay forgetting."
            eyebrow="Prologue"
            index="ESSAY 01"
            title="A response to cosmic impermanence, not a solution to it."
          />
          <div className="prose-essay mt-8">
            <p>
              Every civilization builds vessels for memory. A story spoken beside a
              fire, a city charter, a scientific paper, a record fixed to a spacecraft:
              each asks the future to receive something the present considered worth
              carrying.
            </p>
            <p>
              The Final Symposium imagines the longest possible horizon. At the end
              of an immense journey, conscious beings arrive with the stories they
              managed to preserve. Some doors never open. Those that do reveal not
              immortality, but continuity: meaning transmitted far enough to be heard
              and revised by another mind.
            </p>
          </div>
        </section>

        <div className="my-16">
          <CelestialDivider label="THREE FOUNDATIONS" />
        </div>

        <section className="grid gap-4 lg:grid-cols-3">
          {foundations.map((foundation) => (
            <LiquidCard className="h-full" key={foundation.index}>
              <p className="font-mono text-xs tracking-[0.18em] text-vermilion">
                {foundation.index}
              </p>
              <h2 className="display mt-4 text-2xl text-cream">{foundation.title}</h2>
              <p className="prose-compact mt-4 text-muted">{foundation.body}</p>
            </LiquidCard>
          ))}
        </section>

        <section className="mx-auto mt-20 max-w-3xl">
          <ArchiveHeader
            eyebrow="Corrigibility"
            index="PRINCIPLE"
            title="Keep the means of setting judgment right constantly at hand."
          />
          <div className="prose-essay mt-8">
            <p>
              Human judgment has value because it can be corrected. A system worthy
              of trust should preserve the evidence needed to challenge its own
              conclusion. The route, the inputs, the rejected alternatives, and the
              governing configuration should remain visible.
            </p>
            <p>
              This principle joins the philosophical mission to the current product.
              Explainability is not decoration. It is the mechanism by which an
              institution stays revisable instead of hardening error into authority.
            </p>
          </div>
        </section>

        <section className="mt-20 overflow-hidden rounded-[20px] border border-gold/15 bg-[#e8e2d4] p-6 text-parchment-ink sm:p-10">
          <p className="chart-label text-parchment-muted">Near-term work</p>
          <h2 className="display mt-3 max-w-3xl text-3xl">
            The mission begins with a small, exact promise.
          </h2>
          <p className="mt-5 max-w-3xl font-serif text-lg leading-8 text-parchment-muted">
            Route a space-data job. Compare the candidates. Explain the decision.
            Preserve enough evidence to replay it. The Final Symposium is not a claim
            that this product solves mortality or cosmic entropy. It is a reason to
            build accountable infrastructure now.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              className="rounded-xl bg-[#1c1916] px-4 py-2.5 text-sm font-medium text-[#e8e2d4] 	ransition-colors hover:opacity-85"
              href="/about"
            >
              Back to About
            </Link>
            <Link
              className="rounded-xl border border-parchment-ink/25 px-4 py-2.5 text-sm font-medium 	ransition-colors hover:border-parchment-ink/50"
              href="/#demo"
            >
              Run the product demo
            </Link>
          </div>
        </section>
      </div>
    </article>
  );
}
