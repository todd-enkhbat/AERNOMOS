import { NextResponse } from "next/server";

import { CALENDAR_EVENTS, CALENDAR_META } from "@/lib/calendar-events";

export const dynamic = "force-static";

function icsDate(iso: string, endExclusive = false): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d + (endExclusive ? 1 : 0)));
  const yyyy = date.getUTCFullYear();
  const mm = String(date.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(date.getUTCDate()).padStart(2, "0");
  return `${yyyy}${mm}${dd}`;
}

function escapeText(value: string): string {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/\n/g, "\\n")
    .replace(/,/g, "\\,")
    .replace(/;/g, "\\;");
}

export function GET() {
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Nomos Orbital//Verified Space Industry Calendar//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    `X-WR-CALNAME:${escapeText(CALENDAR_META.title)}`
  ];

  for (const event of CALENDAR_EVENTS) {
    const endIso = event.end ?? event.start;
    lines.push(
      "BEGIN:VEVENT",
      `UID:${event.id}@nomosorbital.com`,
      `DTSTAMP:${icsDate(CALENDAR_META.verifiedAt)}T120000Z`,
      `DTSTART;VALUE=DATE:${icsDate(event.start)}`,
      `DTEND;VALUE=DATE:${icsDate(endIso, true)}`,
      `SUMMARY:${escapeText(event.title)}`,
      `LOCATION:${escapeText(`${event.venue}, ${event.location}`)}`,
      `DESCRIPTION:${escapeText(
        `${event.priority}. ${event.category}. ${event.research.notes} ${event.url}`
      )}`,
      `URL:${event.url}`,
      "END:VEVENT"
    );
  }

  lines.push("END:VCALENDAR");
  const body = `${lines.join("\r\n")}\r\n`;

  return new NextResponse(body, {
    headers: {
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition":
        'attachment; filename="verified_space_industry_calendar.ics"'
    }
  });
}
