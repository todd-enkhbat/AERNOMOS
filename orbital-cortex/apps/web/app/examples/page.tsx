import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";

export const metadata = {
  title: "Example plans · Nomos Orbital",
  description:
    "Public example mission plans that show how Nomos recommends infrastructure routes with source-backed evidence."
};

export default function ExamplesPage() {
  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Examples"
        title="Example mission plans"
        description="A curated library of public example plans is coming. Until then, build your own private plan or browse any examples already published to the missions list."
        action={
          <LiquidButton href="/plan" variant="primary">
            Build a mission plan
          </LiquidButton>
        }
      />

      <LiquidCard>
        <p className="chart-label text-gold">Coming soon</p>
        <h2 className="mt-2 text-lg font-medium text-cream">
          Public example library
        </h2>
        <p className="prose-compact mt-3 max-w-2xl text-muted">
          Phase L will publish annotated example missions you can open without a
          session. Each example will show a recommended plan, source evidence,
          and the same capability boundaries as a live private mission.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <LiquidButton href="/missions" variant="outline">
            Browse missions
          </LiquidButton>
          <LiquidButton href="/plan" variant="ghost">
            Start from scratch →
          </LiquidButton>
        </div>
      </LiquidCard>
    </div>
  );
}
