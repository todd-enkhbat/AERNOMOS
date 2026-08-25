import { PageHeader } from "@/components/PageHeader";
import { MissionPlanBuilder } from "@/components/plan/MissionPlanBuilder";

export const metadata = {
  title: "Run a request",
  description:
    "Describe an objective and Nomos evaluates orbital, data, ground, and compute paths across the infrastructure represented in the system. No account required."
};

export default function PlanPage() {
  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Nomos intelligence"
        title="What do you need from the network?"
        description="Describe an objective and Nomos evaluates available orbital, data, ground, and compute paths using the infrastructure currently represented in the system. Requests stay private to this browser session. No account required."
      />
      <MissionPlanBuilder />
    </div>
  );
}
