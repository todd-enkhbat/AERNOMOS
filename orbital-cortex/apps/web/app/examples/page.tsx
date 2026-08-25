import { ExamplesLibrary } from "@/components/examples/ExamplesLibrary";

export const metadata = {
  title: "Example requests",
  description:
    "Curated public example requests routed through Nomos, with explicit real, calculated, estimated, simulated, and unavailable disclosures."
};

export default function ExamplesPage() {
  return <ExamplesLibrary />;
}
