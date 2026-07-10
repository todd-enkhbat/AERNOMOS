"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { LiquidCard } from "./LiquidCard";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/network", label: "Network" },
  { href: "/about", label: "About" },
  { href: "/docs", label: "Docs" }
];

export function LiquidNavPill() {
  const pathname = usePathname();

  return (
    <LiquidCard className="!rounded-2xl !p-0">
      <div className="flex min-h-[52px] items-center justify-between gap-3 px-3.5 sm:px-4">
        <nav className="hidden items-center gap-0.5 md:flex">
          {navItems.map((item) => {
            const active =
              pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                className={[
                  "liquid-nav-pill rounded-lg px-3 py-1.5 text-[13px] transition-colors",
                  active ? "liquid-nav-pill--active" : "text-muted hover:text-cream"
                ].join(" ")}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </LiquidCard>
  );
}
