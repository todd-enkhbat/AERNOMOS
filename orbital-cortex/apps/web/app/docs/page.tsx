import { BookOpen, Code2, FileJson, Package } from "lucide-react";

import { API_BASE_URL } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";

const curlExample = (baseUrl: string) => `curl -X POST ${baseUrl}/v1/jobs \\
  -H "Authorization: Bearer oc_test_123" \\
  -H "Content-Type: application/json" \\
  -d '{
    "job_type": "ship_detection",
    "area_of_interest": {
      "type": "bbox",
      "coordinates": [-74.3, 40.3, -73.5, 41.0]
    },
    "sensor": "SAR",
    "priority": "fastest",
    "compute_preference": "orbital_if_available",
    "max_cost_usd": 500
  }'`;

const sdkExample = `from orbitalcortex import Client

client = Client(api_key="oc_test_123", base_url="${API_BASE_URL}")

job = client.jobs.create(
    job_type="ship_detection",
    area_of_interest={
        "type": "bbox",
        "coordinates": [-74.3, 40.3, -73.5, 41.0],
    },
    sensor="SAR",
    priority="fastest",
    compute_preference="orbital_if_available",
    max_cost_usd=500,
)

print(job)`;

const endpoints = [
  ["POST", "/v1/jobs", "Create a job and routing decision"],
  ["GET", "/v1/jobs", "List jobs"],
  ["GET", "/v1/jobs/{job_id}", "Read job detail"],
  ["GET", "/v1/jobs/{job_id}/events", "Read lifecycle events"],
  ["GET", "/v1/jobs/{job_id}/scene", "Read scene metadata"],
  ["GET", "/v1/jobs/{job_id}/routing", "Read route scores"],
  ["POST", "/v1/jobs/{job_id}/replay", "Replay routing for audit hash"],
  ["GET", "/v1/jobs/{job_id}/result", "Read result manifest and artifact URLs"],
  ["GET", "/v1/jobs/{job_id}/detections", "Read detections GeoJSON"],
  ["GET", "/v1/nodes", "Read compute nodes and ground stations"],
  ["GET", "/v1/ground-stations", "List ground stations"],
  ["GET", "/v1/satellites", "List satellites with pinned TLEs"],
  ["GET", "/v1/contact-windows", "List SGP4 contact windows"],
  ["POST", "/v1/simulate/run/{job_id}", "Advance simulation manually"]
];

export default function DocsPage() {
  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Docs"
        title="API and SDK reference"
        description="The Nomos Orbital web app and Python SDK share the same FastAPI contract."
      />

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="panel p-6">
          <div className="flex items-center gap-3">
            <BookOpen className="text-[#25495a]" size={20} strokeWidth={1.8} />
            <h2 className="text-2xl font-bold text-[#17140f]">Endpoints</h2>
          </div>
          <p className="mt-3 text-sm text-[#6f604c]">
            Base URL: <span className="metric-value">{API_BASE_URL}</span>
          </p>
          <div className="mt-6 space-y-3">
            {endpoints.map(([method, path, summary]) => (
              <div
                className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-4"
                key={`${method}-${path}`}
              >
                <div className="flex flex-wrap items-center gap-3">
                  <span className="metric-value rounded-lg bg-[#17140f] px-2.5 py-1 text-xs font-bold text-[#fffaf0]">
                    {method}
                  </span>
                  <span className="metric-value text-sm font-bold text-[#25495a]">
                    {path}
                  </span>
                </div>
                <p className="mt-2 text-sm text-[#6f604c]">{summary}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <section className="dark-panel p-6">
            <div className="mb-4 flex items-center gap-3">
              <Code2 className="text-[#e0b16f]" size={20} strokeWidth={1.8} />
              <h2 className="text-2xl font-bold">Create job</h2>
            </div>
            <pre className="code-block border-[#fffaf0]/10 bg-[#0f0d0a]">
              {curlExample(API_BASE_URL)}
            </pre>
          </section>

          <section className="panel p-6">
            <div className="mb-4 flex items-center gap-3">
              <Package className="text-[#25495a]" size={20} strokeWidth={1.8} />
              <h2 className="text-2xl font-bold text-[#17140f]">Python SDK</h2>
            </div>
            <pre className="code-block">{sdkExample}</pre>
          </section>
        </div>
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        {[
          ["Job lifecycle", "queued -> routing -> executing -> downlinking -> complete"],
          ["Default use case", "SAR ship detection over New York Harbor"],
          ["Result shape", "GeoJSON detections and signed artifact URLs"]
        ].map(([title, detail]) => (
          <div className="panel p-5" key={title}>
            <FileJson className="text-[#25495a]" size={20} strokeWidth={1.8} />
            <h3 className="mt-4 text-xl font-bold text-[#17140f]">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-[#6f604c]">{detail}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
