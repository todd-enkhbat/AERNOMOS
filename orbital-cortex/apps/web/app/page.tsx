import { ArrowRight, BookOpen, Gauge, Network, Orbit, Satellite } from "lucide-react";
import Link from "next/link";

const routeSteps = [
  {
    label: "Ingest",
    value: "SAR AOI"
  },
  {
    label: "Route",
    value: "sim_leo_02"
  },
  {
    label: "Downlink",
    value: "svalbard_gs"
  },
  {
    label: "Fallback",
    value: "aws_us_east_gpu"
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
              Run AI jobs across satellites, orbital compute, ground stations,
              and cloud from one API.
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
    </div>
  );
}
