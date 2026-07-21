import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { LiquidCard } from "@/components/liquid/LiquidCard";

const productLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/plan", label: "Build a plan" },
  { href: "/examples", label: "Example plans" },
  { href: "/missions", label: "Missions" },
  { href: "/network", label: "Network" },
  { href: "/about", label: "About" },
  { href: "/calendar", label: "Calendar" },
  { href: "/about/final-symposium", label: "Final Symposium" }
];

const developerLinks = [
  { href: "/docs", label: "API reference" },
  { href: "/docs#sdk", label: "Python SDK" },
  { href: "https://api.nomosorbital.com/docs", label: "OpenAPI" }
];

function FooterLinkList({
  title,
  links
}: {
  title: string;
  links: { href: string; label: string }[];
}) {
  return (
    <div>
      <p className="chart-label text-parchment-muted">{title}</p>
      <ul className="mt-3 space-y-2">
        {links.map((link) => (
          <li key={link.label}>
            <Link
              className="text-sm text-parchment-ink/75 transition-colors hover:text-parchment-ink"
              href={link.href}
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function SiteFooter() {
  return (
    <footer className="atlas-footer relative mt-16 overflow-hidden">
      <div className="atlas-footer__bridge" aria-hidden />
      <div className="atlas-footer__bg" aria-hidden />

      <div className="atlas-footer__shell relative py-10 md:py-12">
        <LiquidCard className="atlas-footer__card" interactive={false} tone="light">
          {/*
            Three equal columns on desktop so Product / Developers span to the
            right edge — no empty frosted dead zone beside the link lists.
          */}
          <div className="atlas-footer__grid">
            <div className="atlas-footer__brand">
              <p className="chart-label text-parchment-muted">Contact</p>
              <div className="mt-3 flex items-center gap-3">
                <NomosMark size={36} />
                <div>
                  <p className="display text-xl text-parchment-ink">Nomos Orbital</p>
                  <p className="chart-label mt-0.5 text-parchment-muted">est. among the stars</p>
                </div>
              </div>
              <p className="prose-compact mt-4 max-w-sm text-parchment-muted">
                Source-backed mission plans for space-data workloads. Real orbital
                and catalog data, labeled assumptions, no false execution claims.
              </p>
              <div className="mt-5 space-y-2">
                <a
                  className="metric-value block text-sm text-parchment-muted transition-colors hover:text-parchment-ink"
                  href="https://api.nomosorbital.com"
                >
                  api.nomosorbital.com
                </a>
                <p className="max-w-sm text-xs leading-5 text-parchment-muted">
                  Production API and real orbital math. Simulated compute execution
                  and offline reference results.
                </p>
              </div>
            </div>

            <nav aria-label="Footer" className="atlas-footer__nav">
              <FooterLinkList title="Product" links={productLinks} />
              <FooterLinkList title="Developers" links={developerLinks} />
            </nav>
          </div>
        </LiquidCard>

        <div className="atlas-footer__meta">
          <p className="metric-value text-[11px] text-parchment-muted">
            © {new Date().getFullYear()} Nomos Orbital
          </p>
          <Link
            className="text-[11px] text-parchment-muted transition-colors hover:text-parchment-ink"
            href="/plan"
          >
            Build a mission plan
          </Link>
        </div>
      </div>
    </footer>
  );
}
