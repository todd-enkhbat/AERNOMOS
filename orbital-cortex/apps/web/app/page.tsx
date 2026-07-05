import { ArrowRight, BookOpen, Gauge, Network, Orbit, Satellite } from "lucide-react";
import Link from "next/link";

const routeSteps = [
  {
    label: "Request",
    value: "SAR harbor scene"
  },
  {
    label: "Score",
    value: "6 compute nodes"
  },
  {
    label: "Select",
    value: "orbital route"
  },
  {
    label: "Return",
    value: "GeoJSON result"
  }
];

export default function HomePage() {
  return (
    <div className="pb-16">
      <section className="page-shell pt-6">
        <div className="hero-bg flex items-end">
          <div className="max-w-4xl px-6 pb-12 pt-28 sm:px-10 lg:px-14 lg:pb-16">
            <div className="mb-6 inline-flex items-center gap-2 rounded-lg border border-[#fffaf0]/20 bg-[#17140f]/40 px-3 py-2 text-sm text-[#f5eddf]">
              <Orbit size={16} strokeWidth={1.8} />
              Orbital compute orchestration
            </div>
            <h1 className="max-w-3xl text-5xl font-bold leading-[1.02] text-[#fffaf0] md:text-7xl">
              Orbital Cortex
            </h1>
            <p className="mt-6 max-w-2xl text-xl leading-8 text-[#f2e8d8] md:text-2xl">
              Submit a space-data AI job, compare orbital and cloud execution
              paths, then inspect the route, logs, scores, and simulated result.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link
                className="inline-flex items-center gap-2 rounded-lg bg-[#fffaf0] px-5 py-3 font-bold text-[#17140f] transition hover:bg-[#eadcc8]"
                href="/jobs"
              >
                Submit Job
                <ArrowRight size={18} strokeWidth={1.8} />
              </Link>
              <Link
                className="inline-flex items-center gap-2 rounded-lg border border-[#fffaf0]/30 bg-[#17140f]/40 px-5 py-3 font-bold text-[#fffaf0] transition hover:bg-[#17140f]/60"
                href="/network"
              >
                <Network size={18} strokeWidth={1.8} />
                View Network
              </Link>
              <Link
                className="inline-flex items-center gap-2 rounded-lg border border-[#fffaf0]/30 bg-[#17140f]/40 px-5 py-3 font-bold text-[#fffaf0] transition hover:bg-[#17140f]/60"
                href="/docs"
              >
                <BookOpen size={18} strokeWidth={1.8} />
                Read API Docs
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="page-shell mt-8 grid gap-4 md:grid-cols-4">
        {routeSteps.map((step, index) => (
          <div className="panel p-5" key={step.label}>
            <div className="flex items-center justify-between gap-4">
              <p className="text-sm font-bold uppercase text-[#a86f35]">
                {String(index + 1).padStart(2, "0")}
              </p>
              {index === 0 ? (
                <Satellite className="text-[#25495a]" size={18} strokeWidth={1.8} />
              ) : (
                <Gauge className="text-[#25495a]" size={18} strokeWidth={1.8} />
              )}
            </div>
            <h2 className="mt-5 text-2xl font-bold text-[#17140f]">{step.label}</h2>
            <p className="metric-value mt-2 text-sm text-[#6f604c]">{step.value}</p>
          </div>
        ))}
      </section>

      <section className="page-shell mt-8 grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="dark-panel p-7">
          <h2 className="text-3xl font-bold">Maritime demo scenario</h2>
          <p className="mt-4 max-w-3xl text-lg leading-8 text-[#d8cbb8]">
            The v0.1 control plane simulates SAR-based vessel detection over
            New York Harbor. It does not task a real satellite; it demonstrates
            the orchestration layer that would decide where compute should run.
          </p>
        </div>
        <div className="panel p-7">
          <p className="text-sm font-bold uppercase text-[#a86f35]">Demo posture</p>
          <h2 className="mt-3 text-2xl font-bold text-[#17140f]">Local and deterministic</h2>
          <p className="mt-3 leading-7 text-[#5d5244]">
            Every route, event, and result is generated from local seed data so
            the demo behaves the same way every time.
          </p>
        </div>
      </section>
    </div>
  );
}
