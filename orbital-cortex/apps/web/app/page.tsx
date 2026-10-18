import Image from "next/image";
import Link from "next/link";
import { ArrowDown, ArrowRight } from "lucide-react";

import { NomosMark } from "@/components/brand/NomosMark";
import { HomeNarrative } from "@/components/home/HomeNarrative";
import { LiquidButton } from "@/components/liquid";
import { FadeIn } from "@/components/motion/primitives";
import { ArchiveImage } from "@/components/visual/ArchiveImage";

import styles from "./HomePage.module.css";

const proofPoints = [
  {
    label: "Describe",
    value: "Outcome and constraints",
    status: "LIVE"
  },
  {
    label: "Resolve",
    value: "Source-backed infrastructure path",
    status: "LIVE"
  },
  {
    label: "Audit",
    value: "Evidence, assumptions, rejected routes",
    status: "LIVE"
  }
];

const networkLayers = [
  {
    index: "01",
    name: "Orbital",
    detail: "Spacecraft, sensors, onboard resources, and orbital opportunities."
  },
  {
    index: "02",
    name: "Connectivity",
    detail: "Ground networks, relay paths, contact windows, and handoff constraints."
  },
  {
    index: "03",
    name: "Compute",
    detail: "Onboard, edge, and cloud environments with policy and latency constraints."
  },
  {
    index: "04",
    name: "Control",
    detail: "Routing, policy, provenance, and the execution record above the providers."
  }
];

export default function HomePage() {
  return (
    <div className={styles.page}>
      <section className={styles.hero} aria-labelledby="home-title">
        <Image
          alt="International Space Station solar arrays above Earth"
          className={styles.heroImage}
          fill
          priority
          sizes="100vw"
          src="/images/archive/irosa-hardware.jpg"
        />
        <div className={styles.heroScrim} aria-hidden />
        <div className={styles.heroGrain} aria-hidden />

        <div className={`page-shell ${styles.heroInner}`}>
          <div className={styles.heroCopy}>
            <FadeIn when="mount">
              <p className={styles.eyebrow}>
                <NomosMark size={18} />
                Orbital infrastructure control plane
              </p>
            </FadeIn>
            <FadeIn delay={0.06} when="mount">
              <h1 id="home-title">The control plane for space infrastructure.</h1>
            </FadeIn>
            <FadeIn delay={0.12} when="mount">
              <p className={styles.heroLead}>
                Orbital Cortex turns heterogeneous satellites, ground networks,
                relays, and compute into one programmable interface. Today it
                resolves and audits infrastructure routes; provider integrations
                progressively turn those routes into execution.
              </p>
            </FadeIn>
            <FadeIn delay={0.18} when="mount">
              <div className={styles.heroActions}>
                <LiquidButton href="/orbital-cortex" variant="primary">
                  Explore Orbital Cortex
                </LiquidButton>
                <LiquidButton href="/network" variant="ghost">
                  Open the network
                </LiquidButton>
              </div>
            </FadeIn>
          </div>

          <FadeIn className={styles.proofRail} delay={0.22} when="mount">
            {proofPoints.map((point) => (
              <div className={styles.proofPoint} key={point.label}>
                <span className={styles.proofStatus}>{point.status}</span>
                <strong>{point.value}</strong>
                <span>{point.label}</span>
              </div>
            ))}
          </FadeIn>
        </div>

        <a className={styles.scrollCue} href="#challenge">
          Understand the problem <ArrowDown aria-hidden size={14} />
        </a>
      </section>

      <section className={styles.challenge} id="challenge">
        <div className={`page-shell ${styles.challengeGrid}`}>
          <FadeIn className={styles.challengeStatement} viewportMargin="0px" y={6}>
            <p className={styles.sectionLabel}>The challenge</p>
            <h2>Space infrastructure is becoming powerful faster than it is becoming interoperable.</h2>
          </FadeIn>
          <ArchiveImage
            alt="Children gathered around a terrestrial globe"
            caption="EARTH / THE SHARED OBJECT"
            className={styles.challengeImage}
            objectPosition="center 42%"
            src="/images/archive/children-with-globe.gif"
            tone="gold"
            unoptimized
          />
          <FadeIn className={styles.challengeDetail} delay={0.05} viewportMargin="0px" y={6}>
            <p>
              A single workload can span a spacecraft, a communications path,
              compute, storage, policy, and delivery. Every provider exposes a
              different interface, commercial model, and operating constraint.
            </p>
            <p>
              Nomos sits above that fragmentation. Orbital Cortex resolves the
              workload against the available stack, records why a route was chosen,
              and creates the control surface that provider adapters can execute.
            </p>
          </FadeIn>
        </div>
      </section>

      <section className={styles.solution} aria-labelledby="solution-title">
        <Image
          alt="A network of orbital infrastructure around Earth"
          className={styles.solutionImage}
          fill
          sizes="100vw"
          src="/images/orbital-circuit-portal-hero.jpg"
        />
        <div className={styles.solutionScrim} aria-hidden />
        <div className={`page-shell ${styles.solutionInner}`}>
          <FadeIn className={styles.solutionCopy} viewportMargin="0px" y={6}>
            <p className={styles.sectionLabel}>Orbital Cortex</p>
            <h2 id="solution-title">Independent infrastructure. One control plane.</h2>
            <p>
              Providers keep their own spacecraft, networks, and compute. Nomos
              supplies the common job model, capability graph, routing logic, policy,
              and audit layer above them.
            </p>
          </FadeIn>

          <div className={styles.layerList}>
            {networkLayers.map((layer, index) => {
              return (
                <FadeIn delay={index * 0.04} key={layer.name} viewportMargin="0px" y={6}>
                  <article className={styles.layerRow}>
                    <span className={styles.layerIndex}>{layer.index}</span>
                    <div>
                      <h3>{layer.name}</h3>
                      <p>{layer.detail}</p>
                    </div>
                  </article>
                </FadeIn>
              );
            })}
          </div>

          <Link className={styles.networkLink} href="/network">
            Open the infrastructure atlas <ArrowRight aria-hidden size={16} />
          </Link>
        </div>
      </section>

      <HomeNarrative />
    </div>
  );
}
