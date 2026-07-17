import type { Metadata, Viewport } from "next";
import { Fraunces, IBM_Plex_Mono, Inter_Tight } from "next/font/google";
import type { ReactNode } from "react";

import { DemoEnvironmentBanner } from "@/components/layout/DemoEnvironmentBanner";
import { SiteFooter } from "@/components/layout/SiteFooter";
import { SiteHeader } from "@/components/layout/SiteHeader";
import "./globals.css";

const serif = Fraunces({
  subsets: ["latin"],
  style: ["normal", "italic"],
  weight: ["300", "400", "500"],
  variable: "--font-serif"
});

const sans = Inter_Tight({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-sans"
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono"
});

export const metadata: Metadata = {
  title: {
    default: "Nomos Orbital | Orchestration for orbital compute",
    template: "%s · Nomos Orbital"
  },
  description:
    "Submit a space-data AI job, compare simulated compute candidates with real orbital math, and inspect every routing decision.",
  icons: {
    icon: [{ url: "/images/nomos-golden-record.png", type: "image/png" }],
    apple: [{ url: "/images/nomos-golden-record.png", type: "image/png" }]
  },
  openGraph: {
    title: "Nomos Orbital",
    description:
      "Orbital compute orchestration. Production API, deterministic routing, and an open simulated execution demo.",
    siteName: "Nomos Orbital",
    type: "website"
  }
};

export const viewport: Viewport = {
  themeColor: "#050506"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${serif.variable} ${sans.variable} ${mono.variable}`}>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <div className="starfield" aria-hidden />
        <div className="relative z-10 flex min-h-screen flex-col">
          <DemoEnvironmentBanner />
          <SiteHeader />
          <main className="flex-1" id="main-content">
            {children}
          </main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
