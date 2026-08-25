import Image from "next/image";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { LiquidCard } from "@/components/liquid/LiquidCard";

const productLinks = [
  { href: "/plan", label: "Run a request" },
  { href: "/examples", label: "Example requests" },
  { href: "/missions", label: "Missions" },
  { href: "/network", label: "Network" },
  { href: "/dashboard", label: "Network control" },
  { href: "/capabilities", label: "Capabilities" },
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
    <footer className="atlas-footer relative mt-8 overflow-hidden md:mt-10">
      <div className="atlas-footer__bridge" aria-hidden />
      <div className="atlas-footer__bg" aria-hidden>
        <Image
          alt=""
          className="atlas-footer__bg-img object-cover object-center"
          fill
          sizes="100vw"
          src="/images/celestial-circuit-atlas.jpg"
          unoptimized
        />
      </div>

      <div className="atlas-footer__shell relative z-[1] py-10 md:py-12">
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
                Nomos Orbital is building the intelligence layer for space
                infrastructure: one request, routed across orbital, ground, and
                cloud systems, with every decision explained.
              </p>
              <div className="mt-5 space-y-2">
                <a
                  className="metric-value block text-sm text-parchment-muted transition-colors hover:text-parchment-ink"
                  href="https://api.nomosorbital.com"
                >
                  api.nomosorbital.com
                </a>
                <p className="max-w-sm text-xs leading-5 text-parchment-muted">
                  Early-access demo: production API, real orbital data and
                  calculations. Provider execution stays simulated or planned until
                  integrations exist.
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
          <p className="metric-value text-[11px] text-cream/70">
            © {new Date().getFullYear()} Nomos Orbital
          </p>
          <Link
            className="text-[11px] text-cream/70 transition-colors hover:text-cream"
            href="/plan"
          >
            Run a request
          </Link>
        </div>
      </div>
    </footer>
  );
}
