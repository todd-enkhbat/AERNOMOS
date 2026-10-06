"use client";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { NomosMark } from "@/components/brand/NomosMark";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { useLiquidMouse } from "@/components/liquid/useLiquidMouse";

const navItems = [
  { href: "/plan", label: "Request" },
  { href: "/missions", label: "Missions" },
  { href: "/network", label: "Network" },
  { href: "/dashboard", label: "Control" },
  { href: "/capabilities", label: "Capabilities" },
  { href: "/about", label: "About" },
  { href: "/docs", label: "Docs" }
];

export function SiteHeader() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const { ref, onMouseMove, onMouseLeave } = useLiquidMouse<HTMLDivElement>();

  return (
    <header className="sticky top-0 z-50">
      <div className="page-shell pt-1.5 md:pt-2">
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
                  Space intelligence infrastructure
                </span>
              </span>
            </Link>

            <nav aria-label="Primary" className="hidden items-center gap-0.5 md:flex">
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

            <LiquidButton className="!hidden md:!inline-flex" href="/plan" variant="primary">
              Run a request
            </LiquidButton>
            <button
              aria-expanded={menuOpen}
              aria-label={menuOpen ? "Close navigation" : "Open navigation"}
              className="liquid-nav-pill grid h-10 w-10 place-items-center rounded-full text-cream md:hidden"
              onClick={() => setMenuOpen((open) => !open)}
              type="button"
            >
              {menuOpen ? <X aria-hidden size={18} /> : <Menu aria-hidden size={18} />}
            </button>
          </div>
        </div>

        {menuOpen ? (
          <nav
            aria-label="Primary mobile"
            className="liquid-glass liquid-glass--card mt-1.5 grid grid-cols-2 gap-1 !rounded-xl !p-1.5 md:hidden"
          >
            {navItems.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  aria-current={active ? "page" : undefined}
                  className={`liquid-nav-pill flex min-h-[40px] items-center justify-center rounded-lg px-2 py-2 text-center text-xs leading-tight ${
                    active ? "liquid-nav-pill--active" : "text-muted"
                  }`}
                  href={item.href}
                  key={item.href}
                  onClick={() => setMenuOpen(false)}
                >
                  {item.label}
                </Link>
              );
            })}
              <Link
                className="col-span-2 flex min-h-[42px] items-center justify-center rounded-lg bg-gold px-3 py-2 text-xs font-semibold text-klein-void"
                href="/plan"
                onClick={() => setMenuOpen(false)}
              >
                Build a mission plan
              </Link>
          </nav>
        ) : null}
      </div>
    </header>
  );
}
