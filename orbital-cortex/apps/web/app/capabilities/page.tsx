import type { Metadata } from "next";

import { CapabilitiesExperience } from "@/components/capabilities/CapabilitiesExperience";

export const metadata: Metadata = {
  title: "Capabilities",
  description:
    "One request across the space stack. See what Nomos can do today, how every claim is classified, and where provider integrations expand execution."
};

export default function CapabilitiesPage() {
  return <CapabilitiesExperience />;
}
