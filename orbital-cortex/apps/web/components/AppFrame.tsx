"use client";

import {
  BookOpen,
  BriefcaseBusiness,
  Gauge,
  Network,
  Satellite
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/network", label: "Network", icon: Network },
  { href: "/docs", label: "Docs", icon: BookOpen }
];

export function AppFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 border-b border-[rgba(86,67,42,0.22)] bg-[#f5eddf]/90 backdrop-blur">
        <div className="page-shell flex min-h-[72px] items-center justify-between gap-4 py-3">
          <Link className="flex items-center gap-3" href="/">
            <Image
              alt="Nomos Orbital"
              className="h-10 w-10 rounded-lg object-cover"
              height={40}
              priority
              src="/images/nomos-logo.png"
              width={40}
            />
            <span className="min-w-0">
              <span className="block text-lg font-bold leading-tight text-[#17140f]">
                Nomos Orbital
              </span>
              <span className="block text-xs text-[#6f604c]">
                Orbital compute orchestration
              </span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                    active
                      ? "bg-[#17140f] text-[#fffaf0]"
                      : "text-[#4f4436] hover:bg-[#eadcc8]"
                  }`}
                  href={item.href}
                  key={item.href}
                >
                  <Icon size={16} strokeWidth={1.8} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <Link
            className="hidden items-center gap-2 rounded-lg border border-[rgba(86,67,42,0.22)] px-3 py-2 text-sm text-[#17140f] transition hover:bg-[#eadcc8] sm:flex"
            href="/network"
          >
            <Satellite size={16} strokeWidth={1.8} />
            Network
          </Link>
        </div>

        <nav className="page-shell flex gap-2 overflow-x-auto pb-3 md:hidden">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                  active ? "bg-[#17140f] text-[#fffaf0]" : "bg-[#eadcc8] text-[#4f4436]"
                }`}
                href={item.href}
                key={item.href}
              >
                <Icon size={16} strokeWidth={1.8} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>

      <main>{children}</main>
    </div>
  );
}
