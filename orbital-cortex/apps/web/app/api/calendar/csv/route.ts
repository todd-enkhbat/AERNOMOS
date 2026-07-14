import { NextResponse } from "next/server";

import { CALENDAR_EVENTS } from "@/lib/calendar-events";

export const dynamic = "force-static";

function csvEscape(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replace(/"/g, '""')}"`;
  return value;
}

export function GET() {
  const header = [
    "title",
    "start",
    "end",
    "city",
    "venue",
    "category",
    "priority",
    "status",
    "kind",
    "url",
    "notes"
  ];

  const rows = CALENDAR_EVENTS.map((event) =>
    [
      event.title,
      event.start,
      event.end ?? event.start,
      event.location,
      event.venue,
      event.category,
      event.priority,
      event.status,
      event.kind,
      event.url,
      event.research.notes
    ]
      .map(csvEscape)
      .join(",")
  );

  const body = `${[header.join(","), ...rows].join("\n")}\n`;

  return new NextResponse(body, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition":
        'attachment; filename="verified_space_industry_calendar.csv"'
    }
  });
}
