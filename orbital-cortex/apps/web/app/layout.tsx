import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import type { ReactNode } from "react";

import { DemoEnvironmentBanner } from "@/components/layout/DemoEnvironmentBanner";
import { MetalScrollRail } from "@/components/layout/MetalScrollRail";
import { SiteFooter } from "@/components/layout/SiteFooter";
import { SiteHeader } from "@/components/layout/SiteHeader";
import { SiteCadence } from "@/components/motion/SiteCadence";
import "./globals.css";

const serif = localFont({
  src: [
    {
      path: "./fonts/fraunces-latin-normal.woff2",
      style: "normal",
      weight: "300 900"
    },
    {
      path: "./fonts/fraunces-latin-italic.woff2",
      style: "italic",
      weight: "300 900"
    }
  ],
  variable: "--font-serif"
});

const sans = localFont({
  src: "./fonts/inter-tight-latin.woff2",
  weight: "100 900",
  variable: "--font-sans"
});

const mono = localFont({
  src: [
    {
      path: "./fonts/ibm-plex-mono-latin-400.woff2",
      weight: "400"
    },
    {
      path: "./fonts/ibm-plex-mono-latin-500.woff2",
      weight: "500"
    }
  ],
  variable: "--font-mono"
});

export const metadata: Metadata = {
  metadataBase: new URL("https://nomosorbital.com"),
  title: {
    default: "Nomos Orbital | Space Intelligence Infrastructure",
    template: "%s · Nomos Orbital"
  },
  description:
    "Nomos Orbital is building the intelligence and orchestration layer across satellites, ground infrastructure, and cloud compute. Express what you need; Nomos determines how the space stack can deliver it.",
  icons: {
    icon: [{ url: "/images/nomos-golden-record.png", type: "image/png" }],
    apple: [{ url: "/images/nomos-golden-record.png", type: "image/png" }]
  },
  openGraph: {
    title: "Nomos Orbital | The intelligence layer for space",
    description:
      "Turning fragmented space infrastructure into a programmable network. One request, routed across orbital, ground, and cloud systems, with every decision explained.",
    images: [
      {
        url: "/og.png",
        width: 1730,
        height: 909,
        alt: "Nomos Orbital. The intelligence layer for space."
      }
    ],
    siteName: "Nomos Orbital",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Nomos Orbital | The intelligence layer for space",
    description:
      "Turning fragmented space infrastructure into a programmable network.",
    images: ["/og.png"]
  }
};

export const viewport: Viewport = {
  themeColor: "#001045"
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
        <SiteCadence />
        <div className="relative z-10 flex min-h-screen flex-col">
          <DemoEnvironmentBanner />
          <SiteHeader />
          <main className="flex-1" id="main-content">
            {children}
          </main>
          <SiteFooter />
        </div>
        <MetalScrollRail />
      </body>
    </html>
  );
}
