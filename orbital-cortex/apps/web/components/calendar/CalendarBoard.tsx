"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  MapPin,
  Search,
  X
} from "lucide-react";

import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import {
  CALENDAR_EVENTS,
  CALENDAR_META,
  KIND_LABEL,
  PRESENCE_LABEL,
  PRIORITY_FILTERS,
  VALIDITY_LABEL,
  VERDICT_LABEL,
  type CalendarEvent,
  type CalendarKind,
  type PresenceStatus,
  type ValidityStatus,
  eventOnDay,
  eventTouchesMonth,
  formatDay,
  matchesPriorityFilter
} from "@/lib/calendar-events";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/** Emil Kowalski: custom ease-out for enter/exit — starts fast, feels responsive. */
const EASE_OUT = [0.23, 1, 0.32, 1] as const;
const PANEL_TRANSITION = { duration: 0.18, ease: EASE_OUT };
const PRESS_TRANSITION = { duration: 0.12, ease: EASE_OUT };

const KIND_FILTERS: Array<CalendarKind | "all"> = [
  "all",
  "conference",
  "summit",
  "forum",
  "symposium",
  "workshop",
  "deadline"
];

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function startWeekday(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

function presenceTone(status: PresenceStatus) {
  switch (status) {
    case "planned":
      return "text-gold";
    case "considering":
      return "text-gold/80";
    case "passed":
      return "text-muted";
    default:
      return "text-cream/75";
  }
}

function validityTone(status: ValidityStatus) {
  switch (status) {
    case "closing_soon":
      return "text-vermilion";
    case "open":
      return "text-gold";
    case "closed":
      return "text-muted";
    default:
      return "text-cream/75";
  }
}

export function CalendarBoard() {
  const reduced = useReducedMotion();
  const today = new Date();
  const [cursor, setCursor] = useState({
    year: today.getFullYear(),
    month: today.getMonth()
  });
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState<CalendarKind | "all">("all");
  const [priority, setPriority] = useState<(typeof PRIORITY_FILTERS)[number]>("all");
  const [showClosed, setShowClosed] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedDay, setSelectedDay] = useState<number | null>(today.getDate());
  const [view, setView] = useState<"month" | "list">("month");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return CALENDAR_EVENTS.filter((event) => {
      if (kind !== "all" && event.kind !== kind) return false;
      if (!matchesPriorityFilter(event, priority)) return false;
      if (!showClosed && (event.validity === "closed" || event.presence === "passed")) {
        return false;
      }
      if (!q) return true;
      const haystack = [
        event.title,
        event.location,
        event.venue,
        event.region,
        event.category,
        event.priority,
        event.eligibility.summary,
        event.research.notes,
        ...event.tags,
        ...event.eligibility.fits,
        KIND_LABEL[event.kind],
        PRESENCE_LABEL[event.presence]
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    }).sort((a, b) => a.focus.localeCompare(b.focus));
  }, [kind, priority, query, showClosed]);

  const monthEvents = useMemo(
    () => filtered.filter((event) => eventTouchesMonth(event, cursor.year, cursor.month)),
    [filtered, cursor]
  );

  const selected =
    filtered.find((event) => event.id === selectedId) ??
    monthEvents[0] ??
    filtered[0] ??
    null;

  useEffect(() => {
    if (!selectedId && selected) {
      setSelectedId(selected.id);
    }
  }, [selected, selectedId]);

  const cells = useMemo(() => {
    const total = daysInMonth(cursor.year, cursor.month);
    const pad = startWeekday(cursor.year, cursor.month);
    const out: Array<{ day: number | null; events: CalendarEvent[] }> = [];
    for (let i = 0; i < pad; i += 1) out.push({ day: null, events: [] });
    for (let day = 1; day <= total; day += 1) {
      out.push({
        day,
        events: monthEvents.filter((event) =>
          eventOnDay(event, cursor.year, cursor.month, day)
        )
      });
    }
    return out;
  }, [cursor, monthEvents]);

  const monthLabel = new Date(cursor.year, cursor.month, 1).toLocaleDateString("en-US", {
    month: "long",
    year: "numeric"
  });

  function shiftMonth(delta: number) {
    setCursor((prev) => {
      const date = new Date(prev.year, prev.month + delta, 1);
      return { year: date.getFullYear(), month: date.getMonth() };
    });
    setSelectedDay(null);
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1.35fr_0.95fr]">
      <div className="space-y-4">
        <LiquidCard>
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="chart-label text-gold">Shared industry calendar</p>
                <h2 className="display mt-1 text-2xl text-cream">You may see us there</h2>
                <p className="prose-compact mt-2 max-w-xl text-muted">
                  {CALENDAR_META.count} confirmed events and deadlines · verified{" "}
                  {CALENDAR_META.verifiedAt}. Use it for your own map. Our presence is
                  possible, not claimed.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <LiquidButton href="/api/calendar/ics" variant="outline">
                  Add to calendar
                </LiquidButton>
                <LiquidButton href="/api/calendar/csv" variant="outline">
                  CSV
                </LiquidButton>
                <LiquidButton
                  onClick={() => setView("month")}
                  variant={view === "month" ? "primary" : "outline"}
                >
                  Month
                </LiquidButton>
                <LiquidButton
                  onClick={() => setView("list")}
                  variant={view === "list" ? "primary" : "outline"}
                >
                  List
                </LiquidButton>
              </div>
            </div>

            <div className="relative">
              <Search
                aria-hidden
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted"
              />
              <input
                aria-label="Search calendar"
                className="w-full rounded-xl border border-white/10 bg-void/40 py-2.5 pl-10 pr-3 text-sm text-cream outline-none ring-gold/40 placeholder:text-muted focus:ring-1"
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search places, programs, tags, eligibility…"
                value={query}
              />
            </div>

            <div className="flex flex-wrap gap-1.5">
              {KIND_FILTERS.map((item) => (
                <motion.button
                  className={`liquid-nav-pill rounded-lg px-3 py-1.5 text-[12px] ${
                    kind === item ? "liquid-nav-pill--active" : "text-muted"
                  }`}
                  key={item}
                  onClick={() => setKind(item)}
                  transition={PRESS_TRANSITION}
                  type="button"
                  whileTap={reduced ? undefined : { scale: 0.97 }}
                >
                  {item === "all" ? "All kinds" : KIND_LABEL[item]}
                </motion.button>
              ))}
            </div>

            <div className="flex flex-wrap gap-1.5">
              {PRIORITY_FILTERS.map((item) => (
                <motion.button
                  className={`liquid-nav-pill rounded-lg px-3 py-1.5 text-[12px] ${
                    priority === item ? "liquid-nav-pill--active" : "text-muted"
                  }`}
                  key={item}
                  onClick={() => setPriority(item)}
                  transition={PRESS_TRANSITION}
                  type="button"
                  whileTap={reduced ? undefined : { scale: 0.97 }}
                >
                  {item === "all" ? "All priorities" : item}
                </motion.button>
              ))}
              <motion.button
                className={`liquid-nav-pill ml-auto rounded-lg px-3 py-1.5 text-[12px] ${
                  showClosed ? "liquid-nav-pill--active" : "text-muted"
                }`}
                onClick={() => setShowClosed((v) => !v)}
                transition={PRESS_TRANSITION}
                type="button"
                whileTap={reduced ? undefined : { scale: 0.97 }}
              >
                {showClosed ? "Showing past" : "Hide past"}
              </motion.button>
            </div>
          </div>
        </LiquidCard>

        {view === "month" ? (
          <LiquidCard>
            <div className="mb-4 flex items-center justify-between gap-3">
              <motion.button
                aria-label="Previous month"
                className="rounded-lg border border-white/10 p-2 text-silver hover:border-gold/40 hover:text-cream"
                onClick={() => shiftMonth(-1)}
                transition={PRESS_TRANSITION}
                type="button"
                whileTap={reduced ? undefined : { scale: 0.97 }}
              >
                <ChevronLeft className="h-4 w-4" />
              </motion.button>
              <div className="text-center">
                <p className="chart-label text-muted-dark">Calendar</p>
                <p className="display text-xl text-cream">{monthLabel}</p>
              </div>
              <motion.button
                aria-label="Next month"
                className="rounded-lg border border-white/10 p-2 text-silver hover:border-gold/40 hover:text-cream"
                onClick={() => shiftMonth(1)}
                transition={PRESS_TRANSITION}
                type="button"
                whileTap={reduced ? undefined : { scale: 0.97 }}
              >
                <ChevronRight className="h-4 w-4" />
              </motion.button>
            </div>

            <div className="grid grid-cols-7 gap-1.5">
              {WEEKDAYS.map((day) => (
                <div
                  className="px-1 pb-1 text-center font-mono text-[10px] tracking-[0.14em] text-muted-dark"
                  key={day}
                >
                  {day}
                </div>
              ))}
              {cells.map((cell, index) => {
                if (cell.day === null) {
                  return <div className="min-h-[84px] rounded-lg bg-transparent" key={`pad-${index}`} />;
                }
                const isSelected = selectedDay === cell.day;
                const isToday =
                  cell.day === today.getDate() &&
                  cursor.month === today.getMonth() &&
                  cursor.year === today.getFullYear();
                return (
                  <motion.button
                    className={[
                      "min-h-[84px] rounded-lg border p-1.5 text-left",
                      isSelected
                        ? "border-gold/50 bg-gold/10"
                        : "border-white/8 bg-void/30 hover:border-white/20",
                      isToday ? "ring-1 ring-gold/40" : ""
                    ].join(" ")}
                    key={cell.day}
                    onClick={() => {
                      setSelectedDay(cell.day);
                      if (cell.events[0]) setSelectedId(cell.events[0].id);
                    }}
                    style={{ transformOrigin: "center" }}
                    transition={PRESS_TRANSITION}
                    type="button"
                    whileTap={reduced ? undefined : { scale: 0.97 }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[11px] text-silver">{cell.day}</span>
                      {cell.events.length > 0 ? (
                        <span className="font-mono text-[9px] text-gold">{cell.events.length}</span>
                      ) : null}
                    </div>
                    <div className="mt-1 space-y-1">
                      {cell.events.slice(0, 2).map((event) => (
                        <div
                          className="truncate rounded px-1 py-0.5 text-[10px] leading-tight text-cream/90"
                          key={event.id}
                          style={{
                            background:
                              event.kind === "deadline"
                                ? "rgba(168, 77, 53, 0.22)"
                                : event.priority.startsWith("Must")
                                  ? "rgba(201, 162, 39, 0.2)"
                                  : "rgba(236, 234, 228, 0.06)"
                          }}
                          title={event.title}
                        >
                          {event.title}
                        </div>
                      ))}
                      {cell.events.length > 2 ? (
                        <p className="px-1 text-[9px] text-muted">+{cell.events.length - 2}</p>
                      ) : null}
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </LiquidCard>
        ) : (
          <LiquidCard>
            <ul className="divide-y divide-white/8">
              {filtered.map((event) => (
                <li key={event.id}>
                  <motion.button
                    className={[
                      "flex w-full flex-col gap-1 py-3 text-left hover:bg-white/[0.03] sm:flex-row sm:items-center sm:justify-between",
                      selected?.id === event.id ? "bg-gold/5" : ""
                    ].join(" ")}
                    onClick={() => setSelectedId(event.id)}
                    style={{ transformOrigin: "left center" }}
                    transition={PRESS_TRANSITION}
                    type="button"
                    whileTap={reduced ? undefined : { scale: 0.99 }}
                  >
                    <div>
                      <p className="chart-label text-muted-dark">{KIND_LABEL[event.kind]}</p>
                      <p className="mt-1 text-sm text-cream">{event.title}</p>
                      <p className="mt-1 flex items-center gap-1 text-xs text-muted">
                        <MapPin className="h-3 w-3" />
                        {event.location}
                      </p>
                      <p className="mt-1 text-[11px] text-gold/90">{event.priority}</p>
                    </div>
                    <div className="text-left sm:text-right">
                      <p className="font-mono text-[11px] text-silver">{formatDay(event.focus)}</p>
                      <p className={`mt-1 text-xs ${presenceTone(event.presence)}`}>
                        {PRESENCE_LABEL[event.presence]}
                      </p>
                    </div>
                  </motion.button>
                </li>
              ))}
              {filtered.length === 0 ? (
                <li className="py-8 text-center text-sm text-muted">No matches for this filter.</li>
              ) : null}
            </ul>
          </LiquidCard>
        )}
      </div>

      <div className="space-y-4 xl:sticky xl:top-24 xl:self-start">
        <AnimatePresence mode="wait">
          {selected ? (
            <motion.div
              animate={reduced ? undefined : { opacity: 1, y: 0, scale: 1 }}
              exit={reduced ? undefined : { opacity: 0, y: 4, scale: 0.98 }}
              initial={reduced ? undefined : { opacity: 0, y: 6, scale: 0.97 }}
              key={selected.id}
              style={{ transformOrigin: "top center" }}
              transition={PANEL_TRANSITION}
            >
              <LiquidCard>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="chart-label text-gold">{KIND_LABEL[selected.kind]}</p>
                    <h3 className="display mt-1 text-2xl leading-tight text-cream">
                      {selected.title}
                    </h3>
                  </div>
                  <CalendarDays className="mt-1 h-5 w-5 shrink-0 text-gold/50" />
                </div>

                <div className="mt-5 flex flex-wrap justify-center gap-3 sm:gap-4">
                  <MetaDisk
                    label="Date"
                    value={formatDay(selected.focus)}
                  />
                  <MetaDisk label="Priority" value={selected.priority} tone="gold" />
                  <MetaDisk
                    label="Presence"
                    value={PRESENCE_LABEL[selected.presence]}
                    tone={selected.presence === "planned" ? "gold" : "neutral"}
                  />
                </div>

                <div className="mt-5 space-y-3 border-t border-white/8 pt-4">
                  <p className="text-sm leading-6 text-cream/80">
                    <span className="chart-label mr-2 text-gold">Venue</span>
                    {selected.venue} · {selected.location}
                  </p>
                  <p className="text-sm leading-6 text-cream/80">
                    <span className="chart-label mr-2 text-gold">Category</span>
                    {selected.category}
                  </p>
                  <p className="text-sm leading-6 text-cream/80">
                    <span className="chart-label mr-2 text-gold">Validity</span>
                    <span className={validityTone(selected.validity)}>
                      {VALIDITY_LABEL[selected.validity]}
                    </span>
                  </p>
                </div>

                <div className="mt-5">
                  <p className="chart-label text-gold">Eligibility</p>
                  <p className="mt-2 text-sm leading-6 text-cream/80">
                    {selected.eligibility.summary}
                  </p>
                  <p className="mt-3 font-mono text-[11px] tracking-[0.12em] text-gold">
                    {VERDICT_LABEL[selected.eligibility.verdict]}
                  </p>
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <SignalDisk
                      items={selected.eligibility.fits}
                      title="Fits"
                      tone="gold"
                    />
                    <SignalDisk
                      items={selected.eligibility.risks}
                      title="Risks"
                      tone="vermilion"
                    />
                  </div>
                </div>

                <div className="mt-5">
                  <p className="chart-label text-gold">Research notes</p>
                  <p className="mt-2 text-sm leading-6 text-cream/80">{selected.research.notes}</p>
                  <p className="mt-2 font-mono text-[10px] text-muted">
                    Checked {selected.research.checkedAt}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selected.research.sources.map((source) => (
                      <motion.a
                        className="inline-flex items-center gap-1 rounded-lg border border-gold/20 px-2.5 py-1.5 text-[12px] text-cream/85 hover:border-gold/50 hover:text-cream"
                        href={source.href}
                        key={source.href}
                        rel="noreferrer"
                        target="_blank"
                        transition={PRESS_TRANSITION}
                        whileTap={reduced ? undefined : { scale: 0.97 }}
                      >
                        {source.label}
                        <ExternalLink className="h-3 w-3" />
                      </motion.a>
                    ))}
                  </div>
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  {selected.links.map((link) => (
                    <LiquidButton
                      href={link.href}
                      key={link.href}
                      variant={link.primary ? "primary" : "outline"}
                    >
                      {link.label}
                    </LiquidButton>
                  ))}
                </div>

                <div className="mt-4 flex flex-wrap gap-1.5">
                  {selected.tags.map((tag) => (
                    <span
                      className="rounded-md border border-gold/15 px-2 py-0.5 font-mono text-[10px] text-cream/55"
                      key={tag}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </LiquidCard>
            </motion.div>
          ) : null}
        </AnimatePresence>

        {selectedDay !== null && view === "month" ? (
          <LiquidCard inset>
            <div className="flex items-center justify-between">
              <p className="chart-label text-muted-dark">
                Day focus · {cursor.month + 1}/{selectedDay}/{cursor.year}
              </p>
              <button
                aria-label="Clear day focus"
                className="text-muted 	ransition-colors hover:text-cream"
                onClick={() => setSelectedDay(null)}
                type="button"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <ul className="mt-3 space-y-2">
              {monthEvents
                .filter((event) =>
                  eventOnDay(event, cursor.year, cursor.month, selectedDay)
                )
                .map((event) => (
                  <li key={event.id}>
                    <motion.button
                      className="w-full rounded-lg border border-white/10 px-3 py-2 text-left text-sm text-silver hover:border-gold/40 hover:text-cream"
                      onClick={() => setSelectedId(event.id)}
                      style={{ transformOrigin: "left center" }}
                      transition={PRESS_TRANSITION}
                      type="button"
                      whileTap={reduced ? undefined : { scale: 0.97 }}
                    >
                      {event.title}
                    </motion.button>
                  </li>
                ))}
            </ul>
          </LiquidCard>
        ) : null}
      </div>
    </div>
  );
}

function MetaDisk({
  label,
  value,
  tone = "neutral"
}: {
  label: string;
  value: string;
  tone?: "gold" | "neutral";
}) {
  return (
    <div
      className="flex h-[6.75rem] w-[6.75rem] flex-col items-center justify-center rounded-full px-2 text-center"
      style={{
        background:
          "radial-gradient(circle at 32% 28%, rgba(236,234,228,0.07), rgba(5,5,6,0.9) 68%)",
        boxShadow:
          tone === "gold"
            ? "inset 0 0 0 1px rgba(201,162,39,0.45)"
            : "inset 0 0 0 1px rgba(236,234,228,0.14)"
      }}
    >
      <p className="chart-label text-[0.58rem] text-cream/45">{label}</p>
      <p
        className={`mt-1 text-[11px] leading-snug ${
          tone === "gold" ? "text-gold" : "text-cream/90"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function SignalDisk({
  title,
  items,
  tone
}: {
  title: string;
  items: string[];
  tone: "gold" | "vermilion";
}) {
  return (
    <div
      className="rounded-full border px-5 py-5 text-center"
      style={{
        borderColor:
          tone === "gold" ? "rgba(201,162,39,0.28)" : "rgba(168,77,53,0.35)",
        background:
          "radial-gradient(circle at 50% 20%, rgba(236,234,228,0.05), rgba(5,5,6,0.75) 70%)"
      }}
    >
      <p className={`chart-label ${tone === "gold" ? "text-gold" : "text-vermilion"}`}>
        {title}
      </p>
      <p className="mt-2 text-xs leading-5 text-cream/75">{items.join(" · ")}</p>
    </div>
  );
}
