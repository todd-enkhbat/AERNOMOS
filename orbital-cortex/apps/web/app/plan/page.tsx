import { PageHeader } from "@/components/PageHeader";
import { MissionPlanBuilder } from "@/components/plan/MissionPlanBuilder";

export const metadata = {
  title: "Build a mission plan · Nomos Orbital",
  description:
    "Create a private mission plan with an area of interest, timing, and constraints. No account required."
};

export default function PlanPage() {
  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Mission planner"
        title="Build a mission plan"
        description="Five short steps. Your plan stays private to this browser session — no account creation required."
      />
      <MissionPlanBuilder />
    </div>
  );
}
