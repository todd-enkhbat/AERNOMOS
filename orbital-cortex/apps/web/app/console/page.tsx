import { NomosConsole } from "@/components/console/NomosConsole";

export const metadata = {
  title: "Console",
  description:
    "Plan a mission with Nomos in conversation. Request, missions, network and control on one surface: describe an outcome and Nomos determines how satellites, ground systems and cloud compute can deliver it."
};

export default function ConsolePage() {
  return <NomosConsole />;
}
