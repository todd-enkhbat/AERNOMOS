/**
 * Verified space-industry calendar for Nomos Orbital.
 * Source of truth: verified-space-industry-calendar.json
 * Presence recommendations are planning signals, not claims of confirmed Nomos attendance.
 */

import verified from "./verified-space-industry-calendar.json";

export type CalendarKind =
  | "conference"
  | "summit"
  | "forum"
  | "symposium"
  | "workshop"
  | "deadline";

export type PriorityLabel =
  | "Must attend"
  | "Must apply"
  | "High"
  | "High for European partnerships"
  | "High for hardware partnerships"
  | "High with planned meetings"
  | "Consider"
  | "Strong SmallSat add-on"
  | "Only with meetings or subsidized access"
  | "Monitor program";

export type PresenceStatus =
  | "tracking"
  | "considering"
  | "eligible"
  | "planned"
  | "passed";

export type ValidityStatus = "open" | "closing_soon" | "closed" | "upcoming";

export type CalendarEvent = {
  id: string;
  title: string;
  kind: CalendarKind;
  start: string;
  end?: string;
  focus: string;
  location: string;
  venue: string;
  region: string;
  category: string;
  priority: PriorityLabel;
  status: "Confirmed";
  presence: PresenceStatus;
  validity: ValidityStatus;
  eligibility: {
    summary: string;
    fits: string[];
    risks: string[];
    verdict: "strong_fit" | "possible" | "weak" | "needs_review";
  };
  research: {
    notes: string;
    checkedAt: string;
    sources: { label: string; href: string }[];
  };
  links: {
    label: string;
    href: string;
    primary?: boolean;
  }[];
  tags: string[];
  githubQuery?: string;
  url: string;
};

type VerifiedEvent = (typeof verified.events)[number];

const TODAY = new Date(2026, 6, 14);

function parseDay(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function regionFromCity(city: string): string {
  if (/Netherlands|France|Germany|Türkiye|Poland|Europe/i.test(city)) {
    return "Europe";
  }
  if (/Online/i.test(city)) return "Online";
  return "North America";
}

function daysUntil(iso: string): number {
  const target = parseDay(iso);
  const ms = target.getTime() - TODAY.getTime();
  return Math.ceil(ms / (1000 * 60 * 60 * 24));
}

function validityFor(event: VerifiedEvent): ValidityStatus {
  const end = parseDay(event.end);
  if (end < TODAY) return "closed";
  const until = daysUntil(event.start);
  if (event.kind === "deadline" && until <= 30 && until >= 0) return "closing_soon";
  if (until <= 21 && until >= 0) return "open";
  return "upcoming";
}

function presenceFor(priority: string, validity: ValidityStatus): PresenceStatus {
  if (validity === "closed") return "passed";
  if (priority.startsWith("Must")) return "planned";
  if (priority.startsWith("High") || priority.includes("Strong")) return "considering";
  if (priority.startsWith("Consider")) return "considering";
  if (priority.includes("Only with") || priority.startsWith("Monitor")) return "tracking";
  return "tracking";
}

function verdictFor(priority: string): CalendarEvent["eligibility"]["verdict"] {
  if (priority.startsWith("Must") || priority.includes("Strong")) return "strong_fit";
  if (priority.startsWith("High")) return "strong_fit";
  if (priority.startsWith("Consider")) return "possible";
  if (priority.includes("Only with") || priority.startsWith("Monitor")) return "possible";
  return "needs_review";
}

function githubQueryFor(event: VerifiedEvent): string {
  if (event.kind === "deadline") return "satellite conference speaking space software";
  if (/SmallSat|small sat|rideshare|payload/i.test(event.title + event.category)) {
    return "small satellite onboard processing";
  }
  if (/Security|Investor|Defense|Mil/i.test(event.title + event.category)) {
    return "national security space software";
  }
  if (/Europe|ESA|IAC|Paris|Bremen|Poznań|Netherlands/i.test(event.city + event.title)) {
    return "european space industry software";
  }
  return "orbital compute satellite AI";
}

function toCalendarEvent(event: VerifiedEvent): CalendarEvent {
  const validity = validityFor(event);
  const priority = event.priority as PriorityLabel;
  const presence = presenceFor(priority, validity);
  const verdict = verdictFor(priority);

  return {
    id: event.id,
    title: event.title,
    kind: event.kind as CalendarKind,
    start: event.start,
    end: event.end === event.start ? undefined : event.end,
    focus: event.kind === "deadline" ? event.start : event.start,
    location: event.city,
    venue: event.venue,
    region: regionFromCity(event.city),
    category: event.category,
    priority,
    status: "Confirmed",
    presence,
    validity,
    eligibility: {
      summary: `${priority}. ${event.category}. Official status: ${event.status}.`,
      fits: [
        priority,
        event.category,
        event.kind === "deadline"
          ? "Action window for content or speaking"
          : "Verified public organizer page and dates"
      ],
      risks: [
        event.kind === "workshop" && /clearance/i.test(event.notes)
          ? "Clearance and citizenship restrictions may apply"
          : "Travel and registration cost",
        "Always re-check the official URL before booking or applying"
      ],
      verdict
    },
    research: {
      notes: event.notes,
      checkedAt: verified.meta.verifiedAt,
      sources: [{ label: "Official page", href: event.url }]
    },
    links: [
      {
        label: event.kind === "deadline" ? "Open submission" : "Official event page",
        href: event.url,
        primary: true
      }
    ],
    tags: [
      event.kind,
      event.priority.split(" ")[0].toLowerCase(),
      ...event.category
        .split(/[/,]/)
        .map((part) => part.trim().toLowerCase())
        .filter(Boolean)
        .slice(0, 3)
    ],
    githubQuery: githubQueryFor(event),
    url: event.url
  };
}

export const CALENDAR_META = verified.meta;

export const CALENDAR_EVENTS: CalendarEvent[] = verified.events
  .map(toCalendarEvent)
  .sort((a, b) => a.focus.localeCompare(b.focus));

export const KIND_LABEL: Record<CalendarKind, string> = {
  conference: "Conference",
  summit: "Summit",
  forum: "Forum",
  symposium: "Symposium",
  workshop: "Workshop",
  deadline: "Deadline"
};

export const PRESENCE_LABEL: Record<PresenceStatus, string> = {
  tracking: "Tracking",
  considering: "Considering presence",
  eligible: "Eligible to apply",
  planned: "Priority target",
  passed: "Window passed"
};

export const VALIDITY_LABEL: Record<ValidityStatus, string> = {
  open: "Open now",
  closing_soon: "Closing soon",
  closed: "Closed",
  upcoming: "Upcoming"
};

export const VERDICT_LABEL: Record<CalendarEvent["eligibility"]["verdict"], string> = {
  strong_fit: "Strong fit",
  possible: "Possible fit",
  weak: "Weak fit",
  needs_review: "Needs review"
};

export const PRIORITY_FILTERS = [
  "all",
  "Must attend",
  "Must apply",
  "High",
  "Consider",
  "Monitor"
] as const;

export function parseDayIso(iso: string): Date {
  return parseDay(iso);
}

export function formatDay(iso: string): string {
  return parseDay(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric"
  });
}

export function eventTouchesMonth(event: CalendarEvent, year: number, month: number): boolean {
  const start = parseDay(event.start);
  const end = parseDay(event.end ?? event.focus);
  const monthStart = new Date(year, month, 1);
  const monthEnd = new Date(year, month + 1, 0);
  return start <= monthEnd && end >= monthStart;
}

export function eventOnDay(
  event: CalendarEvent,
  year: number,
  month: number,
  day: number
): boolean {
  const cursor = new Date(year, month, day);
  const start = parseDay(event.start);
  const end = parseDay(event.end ?? event.focus);
  return cursor >= start && cursor <= end;
}

export function matchesPriorityFilter(event: CalendarEvent, filter: string): boolean {
  if (filter === "all") return true;
  if (filter === "High") return event.priority.startsWith("High");
  if (filter === "Consider") return event.priority.startsWith("Consider");
  if (filter === "Monitor") {
    return (
      event.priority.startsWith("Monitor") ||
      event.priority.includes("Only with") ||
      event.priority.includes("add-on")
    );
  }
  return event.priority.startsWith(filter);
}
