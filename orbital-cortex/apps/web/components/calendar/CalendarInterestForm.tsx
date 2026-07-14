"use client";

import { FormEvent, useState, useTransition } from "react";
import { motion, useReducedMotion } from "framer-motion";

import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { CALENDAR_EVENTS } from "@/lib/calendar-events";

const EASE_OUT = [0.23, 1, 0.32, 1] as const;

const upcomingTitles = CALENDAR_EVENTS.filter((event) => event.validity !== "closed")
  .slice(0, 18)
  .map((event) => event.title);

type FormState = {
  name: string;
  email: string;
  organization: string;
  role: string;
  eventInterest: string;
  message: string;
};

const empty: FormState = {
  name: "",
  email: "",
  organization: "",
  role: "",
  eventInterest: "",
  message: ""
};

export function CalendarInterestForm() {
  const reduced = useReducedMotion();
  const [form, setForm] = useState<FormState>(empty);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [pending, startTransition] = useTransition();

  function onChange(
    key: keyof FormState,
    value: string
  ) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    startTransition(async () => {
      try {
        const res = await fetch("/api/calendar/interest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form)
        });
        const data = (await res.json()) as { error?: string };
        if (!res.ok) {
          setError(data.error ?? "Could not submit interest.");
          return;
        }
        setDone(true);
        setForm(empty);
      } catch {
        setError("Could not reach the server. Try again.");
      }
    });
  }

  return (
    <LiquidCard id="interest">
      <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <div>
          <p className="chart-label text-gold">Business & operations</p>
          <h2 className="display mt-2 text-3xl leading-tight text-cream sm:text-4xl">
            Register interest
          </h2>
          <p className="prose-compact mt-3 max-w-md text-muted">
            Tell us if you want to meet at one of these places, collaborate on operations,
            or follow Nomos as we appear across the industry calendar.
          </p>
        </div>

        {done ? (
          <motion.div
            animate={reduced ? undefined : { opacity: 1, y: 0, scale: 1 }}
            className="flex min-h-[18rem] flex-col justify-center rounded-full border border-gold/25 px-8 py-10 text-center"
            initial={reduced ? undefined : { opacity: 0, y: 8, scale: 0.97 }}
            style={{
              background:
                "radial-gradient(circle at 40% 30%, rgba(201,162,39,0.12), rgba(5,5,6,0.85) 70%)"
            }}
            transition={{ duration: 0.18, ease: EASE_OUT }}
          >
            <p className="chart-label text-gold">Received</p>
            <p className="display mt-3 text-2xl text-cream">Interest registered.</p>
            <p className="prose-compact mx-auto mt-3 max-w-sm text-muted">
              We will follow up if there is a fit for a meeting or operational conversation.
            </p>
            <div className="mt-6 flex justify-center">
              <LiquidButton onClick={() => setDone(false)} variant="outline">
                Submit another
              </LiquidButton>
            </div>
          </motion.div>
        ) : (
          <form className="space-y-3" onSubmit={onSubmit}>
            <Field
              label="Name"
              onChange={(value) => onChange("name", value)}
              required
              value={form.name}
            />
            <Field
              label="Work email"
              onChange={(value) => onChange("email", value)}
              required
              type="email"
              value={form.email}
            />
            <Field
              label="Organization"
              onChange={(value) => onChange("organization", value)}
              required
              value={form.organization}
            />
            <Field
              label="Role"
              onChange={(value) => onChange("role", value)}
              placeholder="Founder, BD, missions, operations…"
              value={form.role}
            />
            <label className="block">
              <span className="chart-label text-cream/50">Event of interest</span>
              <select
                className="mt-1.5 w-full rounded-xl border border-gold/15 bg-void/50 px-3 py-2.5 text-sm text-cream outline-none ring-gold/35 focus:ring-1"
                onChange={(e) => onChange("eventInterest", e.target.value)}
                value={form.eventInterest}
              >
                <option value="">Any / general interest</option>
                {upcomingTitles.map((title) => (
                  <option key={title} value={title}>
                    {title}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="chart-label text-cream/50">Message</span>
              <textarea
                className="mt-1.5 min-h-[96px] w-full rounded-xl border border-gold/15 bg-void/50 px-3 py-2.5 text-sm text-cream outline-none ring-gold/35 placeholder:text-muted focus:ring-1"
                onChange={(e) => onChange("message", e.target.value)}
                placeholder="Meeting ask, partnership note, or operational context…"
                value={form.message}
              />
            </label>
            {error ? <p className="text-xs text-vermilion">{error}</p> : null}
            <div className="pt-1">
              <LiquidButton disabled={pending} type="submit" variant="primary">
                {pending ? "Sending…" : "Register interest"}
              </LiquidButton>
            </div>
          </form>
        )}
      </div>
    </LiquidCard>
  );
}

function Field({
  label,
  value,
  onChange,
  required,
  type = "text",
  placeholder
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="chart-label text-cream/50">{label}</span>
      <input
        className="mt-1.5 w-full rounded-xl border border-gold/15 bg-void/50 px-3 py-2.5 text-sm text-cream outline-none ring-gold/35 placeholder:text-muted focus:ring-1"
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        type={type}
        value={value}
      />
    </label>
  );
}
