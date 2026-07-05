import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppFrame } from "@/components/AppFrame";
import "./globals.css";

export const metadata: Metadata = {
  title: "Orbital Cortex",
  description: "Simulated orbital compute orchestration control plane."
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
