import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";

const columns = [
  {
    title: "Product",
    links: [
      { href: "/dashboard", label: "Dashboard" },
      { href: "/jobs", label: "Jobs" },
      { href: "/network", label: "Network" }
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
    <footer className="relative mt-24 border-t border-line">
      <div className="page-shell flex flex-col gap-10 py-14 md:flex-row md:items-start md:justify-between">
        <div className="max-w-sm">
          <div className="flex items-center gap-3">
            <NomosMark size={40} tone="cream" />
            <div>
              <p className="text-base font-semibold text-cream">Nomos Orbital</p>
              <p className="chart-label mt-0.5 text-muted">est. among the stars</p>
            </div>
          </div>
          <p className="mt-5 text-sm leading-6 text-muted">
            An open control plane for space-data AI. Every job routed, every
            decision explained, every artifact signed. This is a live public
            demo — no account required.
          </p>
        </div>

        <div className="flex gap-16">
          {columns.map((column) => (
            <div key={column.title}>
              <p className="chart-label text-muted">{column.title}</p>
              <ul className="mt-4 space-y-2.5">
                {column.links.map((link) => (
                  <li key={`${column.title}-${link.label}`}>
                    <Link
                      className="text-sm text-cream/70 transition hover:text-gold"
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

      <div className="border-t border-line">
        <div className="page-shell flex flex-wrap items-center justify-between gap-3 py-5">
          <p className="metric-value text-xs text-muted-dark">
            © {new Date().getFullYear()} Nomos Orbital — live demo, shared queue
          </p>
          <p className="metric-value text-xs text-muted-dark">
            api.nomosorbital.com
          </p>
        </div>
      </div>
    </footer>
  );
}
