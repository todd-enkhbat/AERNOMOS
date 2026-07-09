import { API_BASE_URL } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";

const curlExample = (baseUrl: string) => `curl -X POST ${baseUrl}/v1/jobs \\
  -H "Authorization: Bearer oc_demo_public" \\
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

client = Client(api_key="oc_demo_public", base_url="${API_BASE_URL}")

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
        description="The Nomos Orbital console and Python SDK share the same FastAPI contract. Everything below runs against the live production API."
      />

      {/* light editorial intro */}
      <section className="editorial mb-8 px-8 py-10 sm:px-12">
        <p className="chart-label text-teal-deep">Quickstart</p>
        <h2 className="display mt-4 text-2xl text-ink sm:text-3xl">
          One request, end to end.
        </h2>
        <p className="mt-4 max-w-2xl text-[16px] leading-8 text-ink/75">
          Submit a job, poll its status, then fetch the routing scores,
          lifecycle events, and GeoJSON result. The demo credential{" "}
          <code className="rounded bg-ink/8 px-1.5 py-0.5 font-mono text-[14px] text-teal-deep">
            oc_demo_public
          </code>{" "}
          works for everyone — creation is rate-limited per IP.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="glass p-6">
          <h2 className="text-lg font-semibold text-cream">Endpoints</h2>
          <p className="mt-2 text-sm text-muted">
            Base URL: <span className="metric-value text-teal">{API_BASE_URL}</span>
          </p>
          <div className="mt-6 space-y-3">
            {endpoints.map(([method, path, summary]) => (
              <div
                className="rounded-xl border border-line bg-void/40 p-4"
                key={`${method}-${path}`}
              >
                <div className="flex flex-wrap items-center gap-3">
                  <span
                    className={`metric-value rounded-md px-2 py-0.5 text-xs font-semibold ${
                      method === "POST"
                        ? "bg-gold/15 text-gold-bright"
                        : "bg-teal/15 text-teal"
                    }`}
                  >
                    {method}
                  </span>
                  <span className="metric-value text-sm text-cream/90">{path}</span>
                </div>
                <p className="mt-2 text-sm text-muted">{summary}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <section className="glass p-6">
            <h2 className="text-lg font-semibold text-cream">Create job</h2>
            <pre className="code-block mt-4">{curlExample(API_BASE_URL)}</pre>
          </section>

          <section className="glass p-6">
            <h2 className="text-lg font-semibold text-cream">Python SDK</h2>
            <pre className="code-block mt-4">{sdkExample}</pre>
          </section>
        </div>
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        {[
          ["Job lifecycle", "queued → routing → executing → downlinking → complete"],
          ["Default use case", "SAR ship detection over New York Harbor"],
          ["Result shape", "GeoJSON detections and signed artifact URLs"]
        ].map(([title, detail]) => (
          <div className="glass glass-hover p-5" key={title}>
            <h3 className="font-semibold text-cream">{title}</h3>
            <p className="metric-value mt-3 text-xs leading-6 text-muted">{detail}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
