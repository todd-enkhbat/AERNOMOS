"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NomosMark } from "@/components/brand/NomosMark";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/network", label: "Network" },
  { href: "/about", label: "About" },
  { href: "/docs", label: "Docs" }
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50">
      <div className="page-shell pt-3">
        <div className="aave-glass flex min-h-[52px] items-center justify-between gap-3 rounded-2xl px-3.5 sm:px-4">
          <Link className="group flex items-center gap-2.5" href="/">
            <NomosMark size={30} spinning />
            <span className="min-w-0 leading-none">
              <span className="block text-sm font-semibold tracking-wide text-cream">
                Nomos Orbital
              </span>
              <span className="chart-label hidden text-muted-dark sm:block">
                Orbital compute orchestration
              </span>
            </span>
          </Link>

          <nav className="hidden items-center gap-0.5 md:flex">
            {navItems.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  className={`rounded-lg px-3 py-1.5 text-[13px] transition-colors ${
                    active
                      ? "bg-white/10 text-cream"
                      : "text-muted hover:bg-white/5 hover:text-cream"
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
            className="btn-gold hidden items-center rounded-lg px-3.5 py-2 text-[13px] font-semibold sm:inline-flex"
            href="/#demo"
          >
            Run demo
          </Link>
        </div>

        <nav className="mt-1.5 flex gap-1 overflow-x-auto pb-1 md:hidden">
          {navItems.map((item) => {
            const active =
              pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                className={`glass shrink-0 rounded-lg px-3 py-1.5 text-[13px] ${
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
