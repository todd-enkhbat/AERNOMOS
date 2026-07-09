import type { Metadata, Viewport } from "next";
import { Fraunces, IBM_Plex_Mono, Inter } from "next/font/google";
import type { ReactNode } from "react";

import { SiteFooter } from "@/components/layout/SiteFooter";
import { SiteHeader } from "@/components/layout/SiteHeader";
import "./globals.css";

const serif = Fraunces({
  subsets: ["latin"],
  style: ["normal", "italic"],
  weight: ["300", "400", "500"],
  variable: "--font-serif"
});

const sans = Inter({
  subsets: ["latin"],
  variable: "--font-sans"
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono"
});

export const metadata: Metadata = {
  title: {
    default: "Nomos Orbital — Orchestration for orbital compute",
    template: "%s · Nomos Orbital"
  },
  description:
    "Submit a space-data AI job, watch it route across orbital and cloud compute, and inspect every decision. A live control plane demo — open to anyone.",
  openGraph: {
    title: "Nomos Orbital",
    description:
      "Orchestration for orbital compute. Submit a live job, watch it route across satellites and clouds.",
    siteName: "Nomos Orbital",
    type: "website"
  }
};

export const viewport: Viewport = {
  themeColor: "#0a0a0b"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${serif.variable} ${sans.variable} ${mono.variable}`}>
        <div className="starfield" aria-hidden />
        <div className="relative z-10 flex min-h-screen flex-col">
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
