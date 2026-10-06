import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  Check,
  CloudCog,
  FileCheck2,
  MapPinned,
  Orbit,
  ServerCog
} from "lucide-react";

import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton } from "@/components/liquid";

import styles from "./HomeNarrative.module.css";

const requestFields = [
  { index: "01", label: "Objective", value: "Monitor ship activity" },
  { index: "02", label: "Area", value: "New York Harbor" },
  { index: "03", label: "Data", value: "Recent Sentinel-1 imagery" },
  { index: "04", label: "Constraint", value: "U.S. data residency" }
];

const reasoningSteps = [
  {
    status: "REAL DATA",
    title: "Find usable data",
    detail: "Search public satellite catalogs for scenes that cover the objective."
  },
  {
    status: "CALCULATED",
    title: "Calculate windows",
    detail: "Evaluate orbital geometry and communication opportunities."
  },
  {
    status: "RANKED",
    title: "Compare paths",
    detail: "Test feasible routes across ground, edge, cloud, and onboard patterns."
  },
  {
    status: "SOURCED",
    title: "Explain the decision",
    detail: "Attach sources, assumptions, rejected options, and missing integrations."
  }
];

const planSteps = [
  { label: "Use an existing Sentinel scene", status: "PROVIDER REPORTED" },
  { label: "Transfer through an allowed region", status: "ESTIMATED" },
  { label: "Process in customer-controlled compute", status: "CONDITIONAL" },
  { label: "Return a shareable mission brief", status: "LIVE" }
];

const liveCapabilities = [
  "Search real public satellite catalogs",
  "Calculate orbital and contact geometry",
  "Compare feasible infrastructure patterns",
  "Explain recommendations and rejected paths",
  "Export and privately share a mission brief"
];

const integrationCapabilities = [
  "Task a commercial spacecraft",
  "Reserve a ground-station pass",
  "Run a workload onboard a provider satellite",
  "Read private provider capacity or telemetry",
  "Guarantee live commercial pricing"
];

export function HomeNarrative() {
  return (
    <>
      <section className={styles.narrative} aria-labelledby="product-story-title">
        <div className={`page-shell ${styles.shell}`}>
          <FadeIn viewportMargin="0px" y={6}>
            <div className={styles.storyHeader}>
              <div>
                <p className="chart-label text-gold">The product</p>
                <h2 className={styles.storyTitle} id="product-story-title">
                  One request in. A mission brief out.
                </h2>
              </div>
              <p className={styles.storySummary}>
                Nomos accepts the objective and constraints, evaluates real public
                data plus represented infrastructure, and returns a ranked plan with
                the reasoning attached.
              </p>
            </div>
          </FadeIn>

          <div className={styles.inputBeat}>
            <FadeIn className={styles.beatCopy} viewportMargin="0px" y={6}>
              <p className={styles.beatIndex}>Describe</p>
              <h3>Say what you need.</h3>
              <p>
                Name the outcome, place, timing, and operational limits. You do not
                have to choose a satellite, antenna, or compute region first.
              </p>
              <Link className={styles.textLink} href="/plan">
                Build a request <ArrowRight aria-hidden size={15} />
              </Link>
            </FadeIn>

            <FadeIn delay={0.05} viewportMargin="0px" y={6}>
              <div className={styles.requestSpecimen}>
                <div className={styles.specimenHeader}>
                  <span>Reference request</span>
                  <span>Private workspace</span>
                </div>
                <div className={styles.requestTitle}>
                  <span className={styles.requestMark}>
                    <MapPinned aria-hidden size={19} strokeWidth={1.4} />
                  </span>
                  <div>
                    <small>MISSION OBJECTIVE</small>
                    <strong>Harbor activity assessment</strong>
                  </div>
                </div>
                <div className={styles.requestGrid}>
                  {requestFields.map((field) => (
                    <div className={styles.requestField} key={field.index}>
                      <span>{field.index}</span>
                      <small>{field.label}</small>
                      <strong>{field.value}</strong>
                    </div>
                  ))}
                </div>
                <div className={styles.requestFooter}>
                  <span>No provider selection required</span>
                  <span>Objective ready for evaluation</span>
                </div>
              </div>
            </FadeIn>
          </div>

          <FadeIn viewportMargin="0px" y={6}>
            <div className={styles.reasoningStage}>
              <Image
                alt=""
                className={styles.reasoningImage}
                fill
                sizes="(max-width: 820px) 100vw, 1180px"
                src="/images/archive/earth-atmosphere-observation.gif"
                unoptimized
              />
              <div aria-hidden className={styles.reasoningScrim} />
              <div className={styles.reasoningHeading}>
                <p className={styles.beatIndex}>Resolve</p>
                <h3>Nomos works out the path.</h3>
                <p>
                  The engine separates hard constraints from preferences, then
                  compares ways to fulfill the request.
                </p>
              </div>
              <ol className={styles.reasoningGrid}>
                {reasoningSteps.map((step, index) => (
                    <li className={styles.reasoningCard} key={step.title}>
                      <div className={styles.reasoningCardTop}>
                        <span className={styles.reasoningIndex}>0{index + 1}</span>
                        <span className={styles.reasoningStatus}>{step.status}</span>
                      </div>
                      <h4>{step.title}</h4>
                      <p>{step.detail}</p>
                    </li>
                ))}
              </ol>
            </div>
          </FadeIn>
        </div>
      </section>

      <section className={styles.resultSection} aria-labelledby="mission-brief-title">
        <Image
          alt=""
          className={styles.resultImage}
          fill
          sizes="100vw"
          src="/images/archive/irosa-hardware.jpg"
        />
        <div aria-hidden className={styles.resultScrim} />
        <div className={`page-shell ${styles.resultGrid}`}>
          <FadeIn viewportMargin="0px" y={6}>
            <div className={styles.planSpecimen}>
              <div className={styles.planHeader}>
                <div>
                  <span>Recommended plan</span>
                  <small>REFERENCE MISSION BRIEF</small>
                </div>
                <span className={styles.planStatus}>CONDITIONAL</span>
              </div>
              <div className={styles.planRoute}>
                <div>
                  <Orbit aria-hidden size={18} strokeWidth={1.35} />
                  <span>Existing imagery</span>
                </div>
                <ArrowRight aria-hidden size={16} />
                <div>
                  <ServerCog aria-hidden size={18} strokeWidth={1.35} />
                  <span>Allowed compute</span>
                </div>
                <ArrowRight aria-hidden size={16} />
                <div>
                  <FileCheck2 aria-hidden size={18} strokeWidth={1.35} />
                  <span>Mission brief</span>
                </div>
              </div>
              <div className={styles.planWhy}>
                <small>WHY THIS PATH</small>
                <p>
                  Relevant imagery already exists, the route avoids a new tasking
                  dependency, and processing stays inside the requested region.
                </p>
              </div>
              <ol className={styles.planSteps}>
                {planSteps.map((step, index) => (
                  <li key={step.label}>
                    <span className={styles.planStepIndex}>0{index + 1}</span>
                    <span className={styles.planStepLabel}>{step.label}</span>
                    <span className={styles.planStepStatus}>{step.status}</span>
                  </li>
                ))}
              </ol>
              <div className={styles.planEvidence}>
                <span>Sources attached</span>
                <span>Assumptions exposed</span>
                <span>Missing integrations named</span>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={0.05} viewportMargin="0px" y={6}>
            <div className={styles.resultCopy}>
              <p className={styles.beatIndex}>Recommend</p>
              <h2 id="mission-brief-title">Receive one technical plan.</h2>
              <p className={styles.resultLead}>
                Nomos returns the route it recommends, the alternatives it rejects,
                and the evidence behind the decision. The output is a shareable
                technical brief, not an opaque score.
              </p>
              <ul>
                <li>
                  <Check aria-hidden size={15} /> Recommendation and alternatives
                </li>
                <li>
                  <Check aria-hidden size={15} /> Timeline, geography, and constraints
                </li>
                <li>
                  <Check aria-hidden size={15} /> Sources and calculation methods
                </li>
                <li>
                  <Check aria-hidden size={15} /> Missing provider access called out
                </li>
              </ul>
              <Link className={styles.resultLink} href="/examples">
                Open an example mission <ArrowRight aria-hidden size={15} />
              </Link>
            </div>
          </FadeIn>
        </div>
      </section>

      <section className={styles.maturitySection} aria-labelledby="maturity-title">
        <div className="page-shell">
          <FadeIn viewportMargin="0px" y={6}>
            <div className={styles.maturityHeader}>
              <div>
                <p className="chart-label text-gold">Product maturity</p>
                <h2 id="maturity-title">Useful now. Honest about what comes next.</h2>
              </div>
              <p>
                The intelligence layer works today. Provider integrations turn its
                recommendations into live tasking, reservation, and execution.
              </p>
            </div>
          </FadeIn>
          <div className={styles.maturityGrid}>
            <FadeIn viewportMargin="0px" y={6}>
              <article className={styles.capabilityPanel}>
                <div className={styles.capabilityTitle}>
                  <span className={styles.capabilityIndex}>I</span>
                  <div>
                    <small>AVAILABLE NOW</small>
                    <h3>Plan and explain</h3>
                  </div>
                </div>
                <ul>
                  {liveCapabilities.map((item) => (
                    <li key={item}>
                      <Check aria-hidden size={14} /> {item}
                    </li>
                  ))}
                </ul>
              </article>
            </FadeIn>
            <FadeIn delay={0.04} viewportMargin="0px" y={6}>
              <article className={`${styles.capabilityPanel} ${styles.capabilityPanelQuiet}`}>
                <div className={styles.capabilityTitle}>
                  <span className={styles.capabilityIndex}>II</span>
                  <div>
                    <small>REQUIRES INTEGRATION</small>
                    <h3>Coordinate and execute</h3>
                  </div>
                </div>
                <ul>
                  {integrationCapabilities.map((item) => (
                    <li key={item}>
                      <span aria-hidden className={styles.futureMarker} /> {item}
                    </li>
                  ))}
                </ul>
              </article>
            </FadeIn>
          </div>
          <FadeIn delay={0.06} viewportMargin="0px" y={6}>
            <div className={styles.truthRail}>
              <span><b>LIVE</b> working product</span>
              <span><b>REFERENCE</b> cited public fact</span>
              <span><b>SIMULATED</b> modeled behavior</span>
              <span><b>PLANNED</b> provider integration needed</span>
              <Link href="/capabilities">Full capability map <ArrowRight aria-hidden size={13} /></Link>
            </div>
          </FadeIn>
        </div>
      </section>

      <section className={styles.finalCta} aria-labelledby="final-cta-title">
        <Image
          alt=""
          className={styles.finalImage}
          fill
          sizes="100vw"
          src="/images/celestial-circuit-atlas.jpg"
        />
        <div aria-hidden className={styles.finalScrim} />
        <div className={`page-shell ${styles.finalContent}`}>
          <FadeIn viewportMargin="0px" y={6}>
            <p className="chart-label text-gold-bright">One interface</p>
            <h2 id="final-cta-title">One request. The whole space stack.</h2>
            <p className={styles.finalLead}>
              Describe the outcome. See the route, evidence, assumptions, and
              missing integrations before your team starts coordinating providers.
            </p>
            <div className={styles.finalActions}>
              <LiquidButton href="/plan" variant="primary">Run a request</LiquidButton>
              <LiquidButton href="/examples" variant="ghost">View an example</LiquidButton>
            </div>
            <div className={styles.finalLinks}>
              <Link href="/network"><Orbit aria-hidden size={14} /> Network</Link>
              <Link href="/docs"><CloudCog aria-hidden size={14} /> API reference</Link>
              <Link href="/capabilities"><FileCheck2 aria-hidden size={14} /> Capability map</Link>
            </div>
          </FadeIn>
        </div>
      </section>
    </>
  );
}
