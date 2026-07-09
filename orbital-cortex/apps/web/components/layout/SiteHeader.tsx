"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NomosMark } from "@/components/brand/NomosMark";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/network", label: "Network" },
  { href: "/docs", label: "Docs" }
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50">
      <div className="page-shell pt-4">
        <div className="glass-strong flex min-h-[60px] items-center justify-between gap-4 rounded-2xl px-4 sm:px-5">
          <Link className="group flex items-center gap-3" href="/">
            <NomosMark size={34} spinning />
            <span className="min-w-0 leading-tight">
              <span className="block text-[15px] font-semibold tracking-wide text-cream">
                Nomos Orbital
              </span>
              <span className="chart-label hidden text-muted sm:block">
                Orbital compute orchestration
              </span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  className={`rounded-lg px-3.5 py-2 text-sm transition-colors ${
                    active
                      ? "bg-cream/10 text-cream"
                      : "text-muted hover:bg-cream/5 hover:text-cream"
                  }`}
                  href={item.href}
                  key={item.href}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <Link
            className="hidden items-center gap-2 rounded-lg bg-gold px-4 py-2 text-sm font-semibold text-void transition hover:bg-gold-bright sm:inline-flex"
            href="/#demo"
          >
            Run live demo
          </Link>
        </div>

        <nav className="mt-2 flex gap-1 overflow-x-auto pb-1 md:hidden">
          {navItems.map((item) => {
            const active =
              pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                className={`glass shrink-0 rounded-lg px-3.5 py-2 text-sm ${
                  active ? "text-gold" : "text-muted"
                }`}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
