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

      <section className="glass mb-6 p-5 sm:p-6">
        <p className="chart-label text-gold">Quickstart</p>
        <h2 className="display mt-2 text-xl text-cream sm:text-2xl">
          One request, end to end.
        </h2>
        <p className="prose-compact mt-3 max-w-2xl text-muted">
          Submit a job, poll its status, then fetch the routing scores,
          lifecycle events, and GeoJSON result. The demo credential{" "}
          <code className="metric-value rounded bg-white/6 px-1.5 py-0.5 text-[13px] text-gold-bright">
            oc_demo_public
          </code>{" "}
          works for everyone. Creation is rate-limited per IP.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="glass p-5">
          <h2 className="text-base font-semibold text-cream">Endpoints</h2>
          <p className="mt-1.5 text-sm text-muted">
            Base URL: <span className="metric-value text-silver">{API_BASE_URL}</span>
          </p>
          <div className="mt-4 space-y-2">
            {endpoints.map(([method, path, summary]) => (
              <div
                className="rounded-xl border border-white/10 bg-white/3 p-3.5"
                key={`${method}-${path}`}
              >
                <div className="flex flex-wrap items-center gap-2.5">
                  <span
                    className={`metric-value rounded-md px-2 py-0.5 text-[11px] font-semibold ${
                      method === "POST"
                        ? "bg-gold/15 text-gold-bright"
                        : "bg-white/8 text-silver"
                    }`}
                  >
                    {method}
                  </span>
                  <span className="metric-value text-sm text-cream/90">{path}</span>
                </div>
                <p className="mt-1.5 text-sm leading-snug text-muted">{summary}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <section className="glass p-5">
            <h2 className="text-base font-semibold text-cream">Create job</h2>
            <pre className="code-block mt-3">{curlExample(API_BASE_URL)}</pre>
          </section>

          <section className="glass p-5">
            <h2 className="text-base font-semibold text-cream">Python SDK</h2>
            <pre className="code-block mt-3">{sdkExample}</pre>
          </section>
        </div>
      </section>

      <section className="mt-5 grid gap-3 md:grid-cols-3">
        {[
          ["Job lifecycle", "queued → routing → executing → downlinking → complete"],
          ["Default use case", "SAR ship detection over New York Harbor"],
          ["Result shape", "GeoJSON detections and signed artifact URLs"]
        ].map(([title, detail]) => (
          <div className="glass glass-hover p-4" key={title}>
            <h3 className="text-sm font-semibold text-cream">{title}</h3>
            <p className="metric-value mt-2 text-[11px] leading-snug text-muted">{detail}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
