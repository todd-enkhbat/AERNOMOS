import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";

const columns = [
  {
    title: "Product",
    links: [
      { href: "/dashboard", label: "Dashboard" },
      { href: "/jobs", label: "Jobs" },
      { href: "/network", label: "Network" },
      { href: "/about", label: "About" }
    ]
  },
  {
    title: "Developers",
    links: [
      { href: "/docs", label: "API reference" },
      { href: "/docs", label: "Python SDK" },
      { href: "https://github.com", label: "GitHub" }
    ]
  }
];

export function SiteFooter() {
  return (
    <footer className="atlas-footer relative mt-10 overflow-hidden">
      <div className="atlas-footer__bg" aria-hidden />

      <div className="page-shell relative py-10 md:py-12">
        <div className="aave-glass grid gap-8 p-6 sm:p-8 md:grid-cols-[1.1fr_0.9fr]">
          <div>
            <p className="chart-label text-parchment-muted">Contact</p>
            <div className="mt-3 flex items-center gap-3">
              <NomosMark size={36} />
              <div>
                <p className="display text-xl text-parchment-ink">Nomos Orbital</p>
                <p className="chart-label mt-0.5 text-parchment-muted">est. among the stars</p>
              </div>
            </div>
            <p className="prose-compact mt-4 max-w-sm text-parchment-muted">
              Open control plane for space-data AI. Every job routed, every decision
              explained, every artifact signed.
            </p>
            <div className="mt-5 space-y-1.5">
              <a
                className="metric-value block text-sm text-parchment-ink/80 transition hover:text-parchment-ink"
                href="mailto:hello@nomosorbital.com"
              >
                hello@nomosorbital.com
              </a>
              <a
                className="metric-value block text-sm text-parchment-muted transition hover:text-parchment-ink"
                href="https://api.nomosorbital.com"
              >
                api.nomosorbital.com
              </a>
            </div>
          </div>

          <div className="flex gap-10 md:justify-end">
            {columns.map((column) => (
              <div key={column.title}>
                <p className="chart-label text-parchment-muted">{column.title}</p>
                <ul className="mt-3 space-y-2">
                  {column.links.map((link) => (
                    <li key={`${column.title}-${link.label}`}>
                      <Link
                        className="text-sm text-parchment-ink/75 transition hover:text-parchment-ink"
                        href={link.href}
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-2 px-1">
          <p className="metric-value text-[11px] text-parchment-muted">
            © {new Date().getFullYear()} Nomos Orbital
          </p>
          <Link
            className="text-[11px] text-parchment-muted transition hover:text-parchment-ink"
            href="/#demo"
          >
            Run live demo
          </Link>
        </div>
      </div>
    </footer>
  );
}
