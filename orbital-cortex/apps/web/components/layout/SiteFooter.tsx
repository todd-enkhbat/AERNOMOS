import { OrbitalField } from "@/components/visual/OrbitalField";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";

import styles from "./SiteFooter.module.css";

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
      <p className="chart-label text-gold-bright">{title}</p>
      <ul className="mt-3 space-y-2">
        {links.map((link) => (
          <li key={link.label}>
            <Link
              className="text-sm text-cream/70 transition-colors hover:text-cream"
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
    <footer className="atlas-footer relative overflow-hidden">
      <OrbitalField variant="footer" />
      <div className={`page-shell ${styles.signal}`} aria-hidden>
        <span>One request.</span>
        <span>The whole space stack.</span>
      </div>

      <div className="atlas-footer__shell relative z-[1] py-10 md:py-12">
        <div className="atlas-footer__card">
          <div className="atlas-footer__grid">
            <div className="atlas-footer__brand">
              <p className="chart-label text-gold-bright">Contact</p>
              <div className="mt-3 flex items-center gap-3">
                <NomosMark size={36} />
                <div>
                  <p className="text-xl font-medium tracking-[-0.025em] text-cream">Nomos Orbital</p>
                  <p className="chart-label mt-0.5 text-muted-dark">est. among the stars</p>
                </div>
              </div>
              <p className="prose-compact mt-4 max-w-sm text-cream/70">
                Nomos Orbital is building the intelligence layer for space
                infrastructure: one request, routed across orbital, ground, and
                cloud systems, with every decision explained.
              </p>
              <div className="mt-5 space-y-2">
                <a
                  className="metric-value block text-sm text-cream/70 transition-colors hover:text-cream"
                  href="https://api.nomosorbital.com"
                >
                  api.nomosorbital.com
                </a>
                <p className="max-w-sm text-xs leading-5 text-muted">
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
        </div>

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
