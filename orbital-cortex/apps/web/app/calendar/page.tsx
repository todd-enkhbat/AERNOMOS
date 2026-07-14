import type { Metadata } from "next";
import Link from "next/link";

import { ArchiveHeader } from "@/components/archive/ArchivePrimitives";
import { CalendarBoard } from "@/components/calendar/CalendarBoard";
import { CalendarInterestForm } from "@/components/calendar/CalendarInterestForm";
import { CalendarRegisterDisks } from "@/components/calendar/CalendarRegisterDisks";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidSection } from "@/components/liquid/LiquidSection";
import { CALENDAR_META } from "@/lib/calendar-events";

export const metadata: Metadata = {
  title: "Calendar",
  description:
    "A verified space-industry calendar you can use. You may see Nomos Orbital at these events. Register interest for business and operations meetings."
};

export default function CalendarPage() {
  return (
    <div className="pb-10">
      <LiquidSection className="page-shell pt-6 md:pt-10" orbs={false}>
        <FadeIn>
          <div className="max-w-4xl">
            <p className="chart-label text-gold">Calendar</p>
            <h1 className="display mt-4 text-4xl leading-[1.02] text-cream sm:text-6xl md:text-7xl">
              Use this calendar.
            </h1>
            <p className="prose-compact mt-5 max-w-2xl text-lg text-cream/75 sm:text-xl">
              A verified public register of industry gatherings. Export it, search it, and
              keep it. You may see Nomos Orbital there.
            </p>
            <div className="mt-7 flex flex-wrap gap-2">
              <LiquidButton href="#interest" variant="primary">
                Register interest
              </LiquidButton>
              <LiquidButton href="/api/calendar/ics" variant="outline">
                Add to your calendar
              </LiquidButton>
              <LiquidButton href="/api/calendar/csv" variant="outline">
                Download CSV
              </LiquidButton>
            </div>
            <p className="mt-4 font-mono text-[11px] tracking-[0.12em] text-muted">
              {CALENDAR_META.count} confirmed entries · verified {CALENDAR_META.verifiedAt}
            </p>
          </div>
        </FadeIn>
      </LiquidSection>

      <LiquidSection className="page-shell section-gap" orbs={false}>
        <CalendarBoard />
      </LiquidSection>

      <div className="page-shell section-gap">
        <ArchiveHeader
          description="How this register is built: presence labels, date validity, and ways to take the data with you."
          eyebrow="Field register"
          index="CAL"
          title="Research · validity · apply"
        />
        <CalendarRegisterDisks />
        <p className="mt-6 text-center text-xs text-muted">
          Full register JSON:{" "}
          <Link
            className="text-cream/80 underline-offset-2 hover:text-gold hover:underline"
            href="/calendar/verified_space_industry_calendar.json"
          >
            verified_space_industry_calendar.json
          </Link>
        </p>
      </div>

      <LiquidSection className="page-shell section-gap" orbs={false}>
        <CalendarInterestForm />
      </LiquidSection>
    </div>
  );
}
