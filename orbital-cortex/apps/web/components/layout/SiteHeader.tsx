"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NomosMark } from "@/components/brand/NomosMark";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { useLiquidMouse } from "@/components/liquid/useLiquidMouse";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/plan", label: "Plan" },
  { href: "/missions", label: "Missions" },
  { href: "/network", label: "Network" },
  { href: "/calendar", label: "Calendar" },
  { href: "/about", label: "About" },
  { href: "/docs", label: "Docs" }
];

export function SiteHeader() {
  const pathname = usePathname();
  const { ref, onMouseMove, onMouseLeave } = useLiquidMouse<HTMLDivElement>();

  return (
    <header className="sticky top-0 z-50">
      <div className="page-shell pt-3">
        <div
          className="liquid-glass liquid-glass--card !rounded-2xl !p-0"
          onMouseLeave={onMouseLeave}
          onMouseMove={onMouseMove}
          ref={ref}
        >
          <span aria-hidden className="liquid-glass__specular" data-liquid-specular />
          <div className="relative z-[1] flex min-h-[52px] items-center justify-between gap-3 px-3.5 sm:px-4">
            <Link className="group flex min-w-0 items-center gap-2.5" href="/">
              <NomosMark size={30} spinning />
              <span className="min-w-0 leading-none">
                <span className="block text-sm font-semibold tracking-wide text-cream">
                  Nomos Orbital
                </span>
                <span className="chart-label hidden text-muted-dark sm:block">
                  Mission planning for space data
                </span>
              </span>
            </Link>

            <nav className="hidden items-center gap-0.5 md:flex">
              {navItems.map((item) => {
                const active =
                  pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    aria-current={active ? "page" : undefined}
                    className={[
                      "liquid-nav-pill rounded-lg px-3 py-1.5 text-[13px]",
                      active ? "liquid-nav-pill--active" : "text-muted"
                    ].join(" ")}
                    href={item.href}
                    key={item.href}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <LiquidButton className="hidden sm:inline-flex" href="/plan" variant="primary">
              Build a plan
            </LiquidButton>
          </div>
        </div>

        <nav className="liquid-glass liquid-glass--card mt-1.5 flex gap-1 overflow-x-auto !rounded-xl !p-1.5 md:hidden">
          {navItems.map((item) => {
            const active =
              pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                aria-current={active ? "page" : undefined}
                className={`liquid-nav-pill shrink-0 rounded-lg px-3 py-1.5 text-[13px] ${
                  active ? "liquid-nav-pill--active" : "text-muted"
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
