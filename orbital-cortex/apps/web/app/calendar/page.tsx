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
    <div className="pb-6">
      <LiquidSection className="page-shell py-10 md:py-12" orbs={false}>
        <FadeIn when="mount" y={6}>
          <div className="max-w-3xl">
            <p className="chart-label text-gold">Calendar</p>
            <h1 className="display mt-3 text-3xl leading-[1.08] text-cream sm:text-4xl lg:text-5xl">
              Use this calendar.
            </h1>
            <p className="prose-compact mt-3 max-w-2xl text-cream/85">
              A verified public register of industry gatherings. Export it, search it, and
              keep it. You may see Nomos Orbital there.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
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

      <LiquidSection className="page-shell home-band" orbs={false}>
        <CalendarBoard />
      </LiquidSection>

      <div className="page-shell home-band">
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

      <LiquidSection className="page-shell home-band" orbs={false}>
        <CalendarInterestForm />
      </LiquidSection>
    </div>
  );
}
