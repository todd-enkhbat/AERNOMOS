"use client";

import {
  AnimatePresence,
  motion,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
  useTransform
} from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { NomosMark } from "@/components/brand/NomosMark";
import { LiquidButton } from "@/components/liquid";

import styles from "./CapabilitiesExperience.module.css";

type MarketingState = "LIVE" | "REFERENCE" | "SIMULATED" | "PLANNED";

const requestSignals = [
  ["01", "OBJECTIVE", "Usable imagery"],
  ["02", "AREA", "New York Harbor"],
  ["03", "DEADLINE", "Before 14:00 UTC"],
  ["04", "ORBIT", "Geometry evaluated"],
  ["05", "CATALOG", "Scenes discovered"],
  ["06", "CONTACT", "Windows calculated"],
  ["07", "GROUND", "Handoff compared"],
  ["08", "COMPUTE", "Residency checked"],
  ["09", "CONSTRAINTS", "Hard limits applied"],
  ["10", "ROUTE", "Recommendation resolved"]
] as const;

const loopStates = [
  {
    index: "01",
    label: "UNDERSTAND",
    title: "Interpret the outcome.",
    detail: "Objective, area, timing, and constraints enter one request surface."
  },
  {
    index: "02",
    label: "OBSERVE",
    title: "Read the environment.",
    detail: "Public catalogs, orbital geometry, contact opportunities, and represented infrastructure come into view."
  },
  {
    index: "03",
    label: "DETERMINE",
    title: "Eliminate impossible paths.",
    detail: "Feasible, conditional, and rejected routes remain visibly distinct."
  },
  {
    index: "04",
    label: "ROUTE",
    title: "Return one explained path.",
    detail: "The recommendation carries its sources, assumptions, and missing integrations."
  }
] as const;

const evidenceStages = [
  {
    index: "01",
    title: "Search catalogs",
    state: "REFERENCE" as MarketingState,
    truth: "PROVIDER_REPORTED",
    detail: "Discover real Sentinel scenes through Microsoft Planetary Computer STAC."
  },
  {
    index: "02",
    title: "Calculate contacts",
    state: "LIVE" as MarketingState,
    truth: "CALCULATED",
    detail: "Calculate SGP4 contact opportunities from current or pinned CelesTrak TLEs."
  },
  {
    index: "03",
    title: "Compare routes",
    state: "LIVE" as MarketingState,
    truth: "ESTIMATED",
    detail: "Rank feasible, conditional, and rejected infrastructure patterns."
  },
  {
    index: "04",
    title: "Explain the plan",
    state: "LIVE" as MarketingState,
    truth: "SOURCED",
    detail: "Return a technical brief with evidence, assumptions, and alternatives attached."
  },
  {
    index: "05",
    title: "Keep it private",
    state: "LIVE" as MarketingState,
    truth: "SESSION_BOUND",
    detail: "Visitor missions stay private to an HttpOnly browser session unless explicitly shared."
  },
  {
    index: "06",
    title: "Run a CPU demo",
    state: "LIVE" as MarketingState,
    truth: "OBSERVED",
    detail: "Mission owners can crop a fixture raster and record measured worker duration and output bytes."
  }
] as const;

const truthStates: Array<{
  state: MarketingState;
  title: string;
  detail: string;
}> = [
  { state: "LIVE", title: "Working product", detail: "Runs now on real data or measured execution." },
  { state: "REFERENCE", title: "Cited public fact", detail: "Represented from a named public source." },
  { state: "SIMULATED", title: "Modeled behavior", detail: "Explored only in the labeled historical demo." },
  { state: "PLANNED", title: "Integration required", detail: "The architecture anticipates it. Access is not connected." }
];

const futureNodes = [
  "Satellite tasking",
  "Station reservation",
  "Onboard execution",
  "Private telemetry",
  "Commercial pricing",
  "Multi-provider execution"
] as const;

function useSceneStep<T extends HTMLElement>(count: number) {
  const ref = useRef<T>(null);
  const [active, setActive] = useState(0);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"]
  });

  useMotionValueEvent(scrollYProgress, "change", (value) => {
    const next = Math.min(count - 1, Math.floor(value * count));
    setActive((current) => (current === next ? current : next));
  });

  return { ref, active, progress: scrollYProgress };
}

function TechnicalLabel({ children }: { children: ReactNode }) {
  return <span className={styles.technicalLabel}>{children}</span>;
}

function StateLabel({ state }: { state: MarketingState }) {
  return <span className={`${styles.stateLabel} ${styles[`state${state}`]}`}>{state}</span>;
}

function HeroSystem() {
  const reduced = useReducedMotion();
  const pathTransition = (delay: number) =>
    reduced ? { duration: 0 } : { duration: 1.7, delay, ease: [0.22, 1, 0.36, 1] as const };

  return (
    <div className={styles.heroSystem} aria-label="A request entering Nomos and resolving across orbital, ground, and compute infrastructure">
      <svg aria-hidden viewBox="0 0 1200 620">
        <defs>
          <radialGradient id="cap-core" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#e3c05c" stopOpacity="0.27" />
            <stop offset="52%" stopColor="#002fa7" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#002fa7" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g className={styles.heroGeometry}>
          <circle cx="570" cy="310" r="204" />
          <circle cx="570" cy="310" r="146" />
          <ellipse cx="570" cy="310" rx="330" ry="112" transform="rotate(-12 570 310)" />
          <ellipse cx="570" cy="310" rx="270" ry="77" transform="rotate(28 570 310)" />
        </g>
        <circle cx="570" cy="310" fill="url(#cap-core)" r="235" />

        <motion.path
          animate={{ pathLength: 1, opacity: 1 }}
          className={styles.heroInputPath}
          d="M70 310 C190 310 280 310 410 310"
          initial={reduced ? false : { pathLength: 0, opacity: 0 }}
          transition={pathTransition(0.25)}
        />
        <motion.path
          animate={{ pathLength: 1, opacity: 0.32 }}
          className={styles.heroCandidate}
          d="M610 300 C705 180 800 128 916 128 C1000 128 1050 198 1124 310"
          initial={reduced ? false : { pathLength: 0, opacity: 0 }}
          transition={pathTransition(1.05)}
        />
        <motion.path
          animate={{ pathLength: 1, opacity: 0.2 }}
          className={styles.heroCandidate}
          d="M620 320 C740 338 820 348 930 338 C1010 330 1060 320 1124 310"
          initial={reduced ? false : { pathLength: 0, opacity: 0 }}
          transition={pathTransition(1.2)}
        />
        <motion.path
          animate={{ pathLength: 1, opacity: 0.16 }}
          className={styles.heroRejected}
          d="M610 330 C710 450 816 492 934 486 C1018 480 1070 392 1124 310"
          initial={reduced ? false : { pathLength: 0, opacity: 0 }}
          transition={pathTransition(1.35)}
        />
        <motion.path
          animate={{ pathLength: 1, opacity: 1 }}
          className={styles.heroSelected}
          d="M610 310 C710 238 802 205 916 214 C1010 222 1062 272 1124 310"
          initial={reduced ? false : { pathLength: 0, opacity: 0 }}
          transition={pathTransition(2.15)}
        />

        <g className={styles.heroNode} transform="translate(40 275)">
          <rect height="70" width="150" />
          <text x="18" y="28">INPUT / REQUEST</text>
          <text className={styles.svgSub} x="18" y="49">EXAMPLE / READY</text>
        </g>
        <g className={styles.heroCore} transform="translate(570 310)">
          <circle r="72" />
          <circle r="50" />
          <text textAnchor="middle" y="5">NOMOS</text>
          <text className={styles.svgSub} textAnchor="middle" y="27">INTELLIGENCE LAYER</text>
        </g>
        {[
          [916, 128, "ORBITAL", "CATALOG + GEOMETRY"],
          [930, 338, "GROUND", "CONTACT + HANDOFF"],
          [934, 486, "COMPUTE", "PROCESS + DELIVER"]
        ].map(([x, y, label, sub]) => (
          <g className={styles.heroNode} key={String(label)} transform={`translate(${Number(x) - 72} ${Number(y) - 34})`}>
            <rect height="68" width="144" />
            <text x="16" y="27">{label}</text>
            <text className={styles.svgSub} x="16" y="47">{sub}</text>
          </g>
        ))}
        <g className={`${styles.heroNode} ${styles.heroResult}`} transform="translate(1080 275)">
          <rect height="70" width="96" />
          <text x="14" y="28">RESULT</text>
          <text className={styles.svgSub} x="14" y="49">EXPLAINED</text>
        </g>
      </svg>
      <div className={styles.heroSystemMeta}>
        <TechnicalLabel>ROUTE / NOM-001</TechnicalLabel>
        <TechnicalLabel>3 CANDIDATES</TechnicalLabel>
        <TechnicalLabel>1 SELECTED</TechnicalLabel>
      </div>
    </div>
  );
}

function CapabilitiesHero() {
  return (
    <section className={styles.hero} aria-labelledby="capabilities-title">
      <div className={styles.sceneGrid} aria-hidden />
      <div className={`page-shell ${styles.heroInner}`}>
        <div className={styles.heroHeader}>
          <motion.div
            animate={{ opacity: 1, transform: "translateY(0px)" }}
            initial={{ opacity: 0, transform: "translateY(12px)" }}
            transition={{ duration: 0.8 }}
          >
            <p className={styles.eyebrow}><NomosMark size={18} /> Capabilities</p>
            <h1 id="capabilities-title">One request.<br />The whole space stack.</h1>
          </motion.div>
          <motion.p
            animate={{ opacity: 1 }}
            className={styles.heroLead}
            initial={{ opacity: 0 }}
            transition={{ delay: 0.45, duration: 0.8 }}
          >
            Nomos determines how a request should move across orbital, ground,
            and compute infrastructure.
          </motion.p>
        </div>
        <HeroSystem />
      </div>
    </section>
  );
}

function RequestComplexityScene() {
  const { ref, active, progress } = useSceneStep<HTMLElement>(requestSignals.length);
  const reduced = useReducedMotion();
  const effectiveActive = reduced ? requestSignals.length - 1 : active;
  const scale = useTransform(progress, [0, 1], [0.96, 1.02]);

  return (
    <section className={styles.requestScene} ref={ref}>
      <div className={styles.stickyStage}>
        <div className={styles.sceneGrid} aria-hidden />
        <div className={`page-shell ${styles.requestStageInner}`}>
          <div className={styles.requestTitleBlock}>
            <TechnicalLabel>REQUEST MODEL</TechnicalLabel>
            <h2>The request<br />stays simple.</h2>
            <p>Nomos absorbs the infrastructure complexity below the outcome.</p>
          </div>

          <motion.div className={styles.requestInstrument} style={reduced ? undefined : { scale }}>
            <div className={styles.requestCore}>
              <span>REQUEST / EXAMPLE</span>
              <strong>Find usable imagery of this area before 14:00 UTC.</strong>
              <small>No provider selection required</small>
            </div>
            <div className={styles.signalField}>
              {requestSignals.map(([index, label, value], signalIndex) => (
                <motion.div
                  animate={{
                    opacity: signalIndex <= effectiveActive ? 1 : 0.08,
                    transform: signalIndex <= effectiveActive ? "translateY(0px)" : "translateY(10px)"
                  }}
                  className={styles.signalRow}
                  initial={false}
                  key={label}
                  transition={{ duration: reduced ? 0 : 0.45 }}
                >
                  <span>{index}</span>
                  <b>{label}</b>
                  <em>{value}</em>
                </motion.div>
              ))}
            </div>
            <div className={styles.requestProgress}>
              <span style={{ transform: `scaleX(${(effectiveActive + 1) / requestSignals.length})` }} />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function IntelligenceDiagram({ active }: { active: number }) {
  const reduced = useReducedMotion();
  const transition = { duration: reduced ? 0 : 0.6, ease: "easeOut" as const };

  return (
    <div className={`${styles.intelligenceDiagram} ${styles[`loopStep${active}`]}`}>
      <svg aria-hidden viewBox="0 0 850 620">
        <g className={styles.loopGeometry}>
          <circle cx="424" cy="310" r="214" />
          <circle cx="424" cy="310" r="148" />
          <path d="M80 310 H770" />
          <path d="M424 42 V578" />
        </g>
        <motion.path
          animate={{ opacity: active >= 0 ? 1 : 0, pathLength: active >= 0 ? 1 : 0 }}
          className={styles.loopInput}
          d="M58 310 H328"
          initial={false}
          transition={transition}
        />
        <g className={styles.loopCore} transform="translate(424 310)">
          <circle r="66" />
          <text textAnchor="middle" y="4">NOMOS</text>
          <text className={styles.svgSub} textAnchor="middle" y="25">RESOLUTION FIELD</text>
        </g>
        {[
          [424, 74, "ORBITAL", "TLE / GEOMETRY"],
          [714, 218, "CATALOG", "STAC / COVERAGE"],
          [714, 434, "GROUND", "AOS / LOS"],
          [424, 548, "COMPUTE", "REGION / POLICY"]
        ].map(([x, y, label, sub], index) => (
          <motion.g
            animate={{ opacity: active >= 1 ? 1 : 0.08, transform: active >= 1 ? "scale(1)" : "scale(0.92)" }}
            className={styles.loopNode}
            initial={false}
            key={String(label)}
            style={{ transformBox: "fill-box", transformOrigin: "center" }}
            transition={{ ...transition, delay: index * 0.06 }}
            transform={`translate(${Number(x) - 64} ${Number(y) - 27})`}
          >
            <rect height="54" width="128" />
            <text x="12" y="22">{label}</text>
            <text className={styles.svgSub} x="12" y="39">{sub}</text>
          </motion.g>
        ))}
        {[
          ["M490 292 C574 200 642 184 708 218", "FEASIBLE", 576, 182, "feasible"],
          ["M490 318 C578 326 638 378 708 434", "CONDITIONAL", 585, 359, "conditional"],
          ["M414 376 C420 440 420 486 424 520", "REJECTED", 446, 467, "rejected"]
        ].map(([d, label, x, y, kind], index) => (
          <g className={`${styles.loopRoute} ${styles[`loopRoute${String(kind)}`]}`} key={String(label)}>
            <motion.path
              animate={{ opacity: active >= 2 ? (kind === "rejected" && active >= 3 ? 0.12 : 1) : 0, pathLength: active >= 2 ? 1 : 0 }}
              d={String(d)}
              initial={false}
              transition={{ ...transition, delay: index * 0.1 }}
            />
            <motion.text animate={{ opacity: active >= 2 ? 1 : 0 }} initial={false} x={Number(x)} y={Number(y)}>{label}</motion.text>
          </g>
        ))}
        <motion.path
          animate={{ opacity: active >= 3 ? 1 : 0, pathLength: active >= 3 ? 1 : 0 }}
          className={styles.loopSelected}
          d="M490 292 C574 200 642 184 708 218 C762 245 780 274 806 310"
          initial={false}
          transition={{ duration: reduced ? 0 : 1.1, ease: "easeOut" }}
        />
        <motion.g animate={{ opacity: active >= 3 ? 1 : 0.08 }} className={styles.loopResult} initial={false} transform="translate(776 283)">
          <rect height="54" width="68" />
          <text x="10" y="23">RESULT</text>
          <text className={styles.svgSub} x="10" y="40">SOURCED</text>
        </motion.g>
      </svg>
    </div>
  );
}

function IntelligenceLoopScene() {
  const { ref, active } = useSceneStep<HTMLElement>(loopStates.length);
  const reduced = useReducedMotion();
  const state = loopStates[active];

  return (
    <section className={styles.loopScene} ref={ref}>
      <div className={styles.stickyStage}>
        <div className={`page-shell ${styles.loopInner}`}>
          <div className={styles.loopCopy}>
            <TechnicalLabel>PLANNING LOOP</TechnicalLabel>
            {reduced ? (
              <div className={styles.reducedStateList}>
                {loopStates.map((item) => (
                  <article key={item.label}>
                    <p className={styles.stepIndex}>{item.index} / 04</p>
                    <h2>{item.label}</h2>
                    <h3>{item.title}</h3>
                    <p>{item.detail}</p>
                  </article>
                ))}
              </div>
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  animate={{ opacity: 1, transform: "translateY(0px)" }}
                  exit={{ opacity: 0, transform: "translateY(-12px)" }}
                  initial={{ opacity: 0, transform: "translateY(12px)" }}
                  key={state.label}
                  transition={{ duration: 0.42 }}
                >
                  <p className={styles.stepIndex}>{state.index} / 04</p>
                  <h2>{state.label}</h2>
                  <h3>{state.title}</h3>
                  <p>{state.detail}</p>
                </motion.div>
              </AnimatePresence>
            )}
            <div className={styles.stepRail}>
              {loopStates.map((item, index) => (
                <span className={index === active ? styles.stepActive : ""} key={item.label}>{item.index}</span>
              ))}
            </div>
          </div>
          <IntelligenceDiagram active={reduced ? loopStates.length - 1 : active} />
        </div>
      </div>
    </section>
  );
}

function SatelliteGlyph({ x, y }: { x: number; y: number }) {
  return (
    <g className={styles.traceSatellite} transform={`translate(${x} ${y}) rotate(12)`}>
      <path d="M-10 -7 H10 V7 H-10 Z" />
      <path d="M-36 -8 H-14 V8 H-36 Z M14 -8 H36 V8 H14 Z" />
      <path d="M-31 -8 V8 M-24 -8 V8 M-17 -8 V8 M19 -8 V8 M26 -8 V8 M33 -8 V8" />
      <path d="M0 -15 V-7 M-4 -15 H4 M10 0 H15" />
      <circle cx="0" cy="0" r="2.5" />
    </g>
  );
}

function GroundStationGlyph({ x, y }: { x: number; y: number }) {
  return (
    <g className={styles.traceStation} transform={`translate(${x} ${y})`}>
      <path d="M-12 8 H12 M0 8 V-2 M-8 -2 Q0 7 8 -2 M-6 -5 Q0 1 6 -5" />
      <circle cx="0" cy="-6" r="1.8" />
    </g>
  );
}

function EvidenceInstrument({ active, reduced }: { active: number; reduced: boolean }) {
  const transition = reduced
    ? { duration: 0 }
    : { duration: 0.72, ease: [0.22, 1, 0.36, 1] as const };
  const phase = (threshold: number) => ({
    animate: { opacity: active >= threshold ? 1 : 0 },
    initial: false,
    transition
  });
  const pipelineActive = [1, 3, 4, 5, 5, 6][active] ?? 6;

  return (
    <div
      aria-label="Mission analysis plate showing an SGP4 orbital trajectory, an observation window over an area of interest, route comparison, and traceable observed output"
      className={styles.evidenceInstrument}
      role="img"
    >
      <div className={styles.instrumentHeader}>
        <span>NOMOS / CAPABILITY TRACE</span>
        <span>MISSION / EXAMPLE</span>
      </div>
      <div className={styles.evidenceCanvas}>
        <svg aria-hidden className={styles.traceDesktop} viewBox="0 0 1000 620">
          <g className={styles.traceReferenceGrid}>
            <path d="M54 92 H946 M54 310 H946 M54 528 H946" />
            <path d="M170 52 V566 M500 52 V566 M830 52 V566" />
            <path d="M72 76 h18 M72 76 v18 M928 76 h-18 M928 76 v18 M72 544 h18 M72 544 v-18 M928 544 h-18 M928 544 v-18" />
          </g>

          <motion.g {...phase(0)}>
            <g className={styles.traceSource}>
              <text x="72" y="112">SOURCE / MPC STAC</text>
              <text x="72" y="132">METHOD / SGP4</text>
              <text x="72" y="152">ASSUMPTIONS / 03</text>
              <path d="M72 166 H196" />
              <text className={styles.traceMicro} x="72" y="184">CATALOG / PUBLIC FACTS</text>
            </g>
            <path className={styles.traceEarth} d="M-80 690 A650 650 0 0 1 1080 690" />
            <path className={styles.traceAtmosphere} d="M-104 672 A676 676 0 0 1 1104 672" />
            <g className={styles.traceEarthCoordinates}>
              <path d="M156 531 Q500 428 844 531" />
              <path d="M330 474 Q500 438 670 474" />
              <path d="M500 444 V620" />
            </g>
            <g className={styles.traceTarget}>
              <path d="M414 470 L468 451 L493 485 L438 507 Z" />
              <path d="M438 507 L468 451 M414 470 L493 485" />
              <circle cx="453" cy="479" r="3" />
              <path d="M410 490 H350 V515" />
              <text x="276" y="535">AOI / SCENE COVERAGE</text>
              <text className={styles.traceMicro} x="276" y="552">TARGET FOOTPRINT</text>
            </g>
          </motion.g>

          <path className={styles.traceOrbitGhost} d="M72 312 C180 240 274 176 360 150 Q520 90 684 168 C775 205 840 250 930 318" />
          <motion.path
            animate={{ opacity: active >= 1 ? 1 : 0, pathLength: active >= 1 ? 1 : 0 }}
            className={styles.traceOrbitPre}
            d="M72 312 C180 240 274 176 360 150"
            initial={false}
            transition={transition}
          />
          <motion.path
            animate={{ opacity: active >= 1 ? 1 : 0, pathLength: active >= 1 ? 1 : 0 }}
            className={styles.traceOrbitAccess}
            d="M360 150 Q520 90 684 168"
            initial={false}
            transition={transition}
          />
          <motion.path
            animate={{ opacity: active >= 1 ? 1 : 0, pathLength: active >= 1 ? 1 : 0 }}
            className={styles.traceOrbitPost}
            d="M684 168 C775 205 840 250 930 318"
            initial={false}
            transition={transition}
          />

          <motion.g {...phase(1)}>
            <text className={styles.traceOrbitLabel} x="474" y="72">ORBIT / SGP4 / SKYFIELD</text>
            <path className={styles.traceOrbitLeader} d="M522 80 V102" />
            <g className={styles.traceTick}>
              <path d="M350 137 L370 163 M673 153 L695 181" />
              <text x="316" y="128">AOS 13:42</text>
              <text x="690" y="145">LOS 13:49</text>
            </g>
            <SatelliteGlyph x={548} y={126} />
            <g className={styles.traceSatelliteLabel}>
              <path d="M566 118 H630 V98" />
              <text x="638" y="95">SPACECRAFT / PROPAGATED</text>
              <text className={styles.traceMicro} x="638" y="112">OBSERVATION POSITION</text>
            </g>
            <motion.g
              animate={{ opacity: 1 }}
              className={styles.traceAccess}
              initial={false}
              transition={transition}
            >
              <path d="M548 126 L414 470 M548 126 L493 485" />
              <path d="M548 126 L453 479" />
              <text x="490" y="286">ACCESS / LOS</text>
            </motion.g>
          </motion.g>

          <motion.g {...phase(2)}>
            <path className={styles.traceRoute} d="M548 126 Q720 225 762 452" />
            <GroundStationGlyph x={762} y={454} />
            <g className={styles.traceRouteLabel}>
              <path d="M770 448 H846" />
              <text x="854" y="444">ROUTE / CANDIDATE</text>
              <text className={styles.traceMicro} x="854" y="461">GROUND HANDOFF</text>
            </g>
            <g className={styles.traceRanking}>
              <path d="M650 355 H716" />
              <text x="624" y="382">01 FEASIBLE</text>
              <text x="624" y="402">02 CONDITIONAL</text>
              <text x="624" y="422">03 REJECTED</text>
            </g>
          </motion.g>

          <motion.g {...phase(3)} className={styles.traceBrief}>
            <path d="M842 292 H922 V350" />
            <text x="788" y="280">BRIEF / SOURCED</text>
            <text className={styles.traceMicro} x="788" y="298">ASSUMPTIONS ATTACHED</text>
          </motion.g>

          <motion.g {...phase(4)} className={styles.tracePrivate}>
            <path d="M106 436 H210 V468" />
            <text x="106" y="420">SESSION PRIVATE</text>
            <text className={styles.traceMicro} x="106" y="438">NOT ENUMERABLE</text>
          </motion.g>

          <motion.g {...phase(5)} className={styles.traceObserved}>
            <path d="M493 485 H842 V518" />
            <circle cx="493" cy="485" r="4" />
            <path d="M842 518 H932" />
            <text x="790" y="542">OBSERVED / OUTPUT</text>
            <text className={styles.traceMicro} x="790" y="560">FIXTURE CPU DEMO</text>
            <text className={styles.traceMicro} x="790" y="578">DURATION / OBSERVED</text>
            <text className={styles.traceMicro} x="790" y="596">OUTPUT / OBSERVED</text>
          </motion.g>

          <g className={styles.tracePipeline}>
            {[
              "AOI", "CATALOG", "ORBIT", "WINDOW", "ROUTE", "BRIEF", "OBSERVED"
            ].map((label, index) => (
              <g className={index <= pipelineActive ? styles.tracePipelineActive : ""} key={label} transform={`translate(${104 + index * 126} 590)`}>
                <path d="M0 0 H84" />
                <text x="0" y="20">{String(index + 1).padStart(2, "0")} {label}</text>
              </g>
            ))}
          </g>
        </svg>

        <svg aria-hidden className={styles.traceMobile} viewBox="0 0 430 650">
          <g className={styles.traceReferenceGrid}>
            <path d="M24 86 H406 M24 328 H406 M24 588 H406" />
            <path d="M58 46 V610 M215 46 V610 M372 46 V610" />
          </g>
          <motion.g {...phase(0)}>
            <g className={styles.traceSource}>
              <text x="32" y="70">SOURCE / MPC STAC</text>
              <text x="32" y="90">METHOD / SGP4</text>
              <text x="32" y="110">ASSUMPTIONS / 03</text>
            </g>
            <path className={styles.traceEarth} d="M-70 690 A365 365 0 0 1 500 690" />
            <path className={styles.traceAtmosphere} d="M-82 676 A380 380 0 0 1 512 676" />
            <g className={styles.traceTarget}>
              <path d="M169 455 L216 439 L236 469 L188 487 Z" />
              <path d="M188 487 L216 439 M169 455 L236 469" />
              <circle cx="202" cy="463" r="3" />
              <text x="128" y="515">AOI / SCENE COVERAGE</text>
            </g>
          </motion.g>
          <path className={styles.traceOrbitGhost} d="M24 286 Q204 86 406 282" />
          <motion.path animate={{ opacity: active >= 1 ? 1 : 0, pathLength: active >= 1 ? 1 : 0 }} className={styles.traceOrbitPre} d="M24 286 Q110 188 154 156" initial={false} transition={transition} />
          <motion.path animate={{ opacity: active >= 1 ? 1 : 0, pathLength: active >= 1 ? 1 : 0 }} className={styles.traceOrbitAccess} d="M154 156 Q225 100 302 160" initial={false} transition={transition} />
          <motion.path animate={{ opacity: active >= 1 ? 1 : 0, pathLength: active >= 1 ? 1 : 0 }} className={styles.traceOrbitPost} d="M302 160 Q360 206 406 282" initial={false} transition={transition} />
          <motion.g {...phase(1)}>
            <text className={styles.traceOrbitLabel} x="142" y="126">ORBIT / SGP4 / SKYFIELD</text>
            <g className={styles.traceTick}>
              <path d="M146 146 L162 166 M294 149 L310 171" />
              <text x="112" y="184">AOS 13:42</text>
              <text x="286" y="190">LOS 13:49</text>
            </g>
            <SatelliteGlyph x={236} y={130} />
            <g className={styles.traceAccess}>
              <path d="M236 130 L169 455 M236 130 L236 469 M236 130 L202 463" />
              <text x="244" y="300">ACCESS / LOS</text>
            </g>
          </motion.g>
          <motion.g {...phase(2)}>
            <path className={styles.traceRoute} d="M236 130 Q344 260 342 445" />
            <GroundStationGlyph x={342} y={447} />
            <g className={styles.traceRouteLabel}>
              <text x="254" y="478">ROUTE / CANDIDATE</text>
              <text className={styles.traceMicro} x="254" y="496">GROUND HANDOFF</text>
            </g>
            <g className={styles.traceRanking}>
              <text x="34" y="352">01 FEASIBLE</text>
              <text x="34" y="372">02 CONDITIONAL</text>
              <text x="34" y="392">03 REJECTED</text>
            </g>
          </motion.g>
          <motion.g {...phase(4)} className={styles.tracePrivate}>
            <text x="28" y="535">SESSION PRIVATE</text>
            <text className={styles.traceMicro} x="28" y="553">NOT ENUMERABLE</text>
          </motion.g>
          <motion.g {...phase(5)} className={styles.traceObserved}>
            <path d="M236 469 H396 V530" />
            <circle cx="236" cy="469" r="4" />
            <text x="224" y="535">OBSERVED / OUTPUT</text>
            <text className={styles.traceMicro} x="224" y="553">FIXTURE CPU DEMO</text>
            <text className={styles.traceMicro} x="224" y="571">DURATION + OUTPUT / OBSERVED</text>
          </motion.g>
          <g className={styles.tracePipeline}>
            {["AOI", "CAT", "ORBIT", "WIN", "ROUTE", "BRIEF", "OBS"].map((label, index) => (
              <g className={index <= pipelineActive ? styles.tracePipelineActive : ""} key={label} transform={`translate(${28 + (index % 4) * 98} ${610 + Math.floor(index / 4) * 24})`}>
                <text>{String(index + 1).padStart(2, "0")} {label}</text>
              </g>
            ))}
          </g>
        </svg>
      </div>
      <div className={styles.instrumentFooter}>
        <span>PUBLIC FACTS</span><span>CALCULATED GEOMETRY</span><span>TRACEABLE OUTPUT</span>
      </div>
    </div>
  );
}

function EvidenceScene() {
  const { ref, active } = useSceneStep<HTMLElement>(evidenceStages.length);
  const reduced = useReducedMotion();
  const stage = evidenceStages[active];

  return (
    <section className={styles.evidenceScene} id="product-evidence" ref={ref}>
      <div className={styles.stickyStage}>
        <div className={`page-shell ${styles.evidenceInner}`}>
          <div className={styles.evidenceTitle}>
            <TechnicalLabel>PRODUCT EVIDENCE</TechnicalLabel>
            <h2>Real capability.<br />Clear boundaries.</h2>
          </div>
          <EvidenceInstrument active={reduced ? evidenceStages.length - 1 : active} reduced={Boolean(reduced)} />
          <div className={styles.evidenceCopy}>
            {reduced ? (
              <div className={styles.reducedEvidenceList}>
                {evidenceStages.map((item) => (
                  <article key={item.title}>
                    <span className={styles.evidenceIndex}>{item.index} / 06</span>
                    <StateLabel state={item.state} />
                    <h3>{item.title}</h3>
                    <p>{item.detail}</p>
                    <small>TRUTH / {item.truth}</small>
                  </article>
                ))}
              </div>
            ) : (
              <AnimatePresence mode="wait">
                <motion.article
                  animate={{ opacity: 1, transform: "translateY(0px)" }}
                  exit={{ opacity: 0, transform: "translateY(-10px)" }}
                  initial={{ opacity: 0, transform: "translateY(10px)" }}
                  key={stage.title}
                  transition={{ duration: 0.38 }}
                >
                  <span className={styles.evidenceIndex}>{stage.index} / 06</span>
                  <StateLabel state={stage.state} />
                  <h3>{stage.title}</h3>
                  <p>{stage.detail}</p>
                  <small>TRUTH / {stage.truth}</small>
                </motion.article>
              </AnimatePresence>
            )}
            <div className={styles.evidenceRail}>
              {evidenceStages.map((item, index) => (
                <span className={index <= active ? styles.evidenceRailActive : ""} key={item.title} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function TruthScene() {
  return (
    <section className={styles.truthScene} aria-labelledby="truth-title">
      <div className={`page-shell ${styles.truthInner}`}>
        <div className={styles.truthHeading}>
          <TechnicalLabel>TRUTH STATUS</TechnicalLabel>
          <h2 id="truth-title">Every claim<br />has a state.</h2>
          <p>Every plan separates public references, Nomos calculations, estimates, simulations, and integrations that still require provider access.</p>
          <div className={styles.truthLegend}>
            {truthStates.map((item) => (
              <article key={item.state}>
                <StateLabel state={item.state} />
                <h3>{item.title}</h3>
                <p>{item.detail}</p>
              </article>
            ))}
          </div>
        </div>
        <div className={styles.truthRoute}>
          <div className={styles.truthRouteLine} aria-hidden />
          {[
            ["PUBLIC CATALOG", "REFERENCE", "PROVIDER_REPORTED"],
            ["ORBITAL GEOMETRY", "LIVE", "CALCULATED"],
            ["ROUTE COMPARISON", "LIVE", "ESTIMATED"],
            ["GROUND RESERVATION", "PLANNED", "UNAVAILABLE"]
          ].map(([title, state, truth], index) => (
            <div className={styles.truthRouteNode} key={title}>
              <span className={styles.truthNodeIndex}>0{index + 1}</span>
              <i className={styles[`truthDot${state}`]} />
              <strong>{title}</strong>
              <StateLabel state={state as MarketingState} />
              <small>{truth}</small>
            </div>
          ))}
          <div className={styles.truthBranch}>
            <span />
            <div>
              <StateLabel state="SIMULATED" />
              <strong>Historical execution model</strong>
              <small>Legacy demo results stay isolated from recommended plans.</small>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function BoundaryScene() {
  return (
    <section className={styles.boundaryScene} aria-labelledby="boundary-title">
      <Image
        alt=""
        aria-hidden
        className={styles.boundaryImage}
        fill
        sizes="100vw"
        src="/images/control-room-tunnel.png"
      />
      <div aria-hidden className={styles.boundaryShade} />
      <div className={styles.sceneGrid} aria-hidden />
      <div className={`page-shell ${styles.boundaryInner}`}>
        <div className={styles.boundaryHeading}>
          <TechnicalLabel>PROVIDER BOUNDARY</TechnicalLabel>
          <h2 id="boundary-title">The intelligence layer is live.<br /><span>Execution expands with the network.</span></h2>
        </div>
        <div className={styles.boundaryTopology}>
          <div className={styles.availableField}>
            <p>AVAILABLE NOW</p>
            {[
              "PUBLIC CATALOG SEARCH",
              "ORBITAL CALCULATION",
              "ROUTE COMPARISON",
              "MISSION BRIEF"
            ].map((item, index) => (
              <div className={styles.connectedNode} key={item}>
                <span>0{index + 1}</span><strong>{item}</strong><StateLabel state={index === 0 ? "REFERENCE" : "LIVE"} />
              </div>
            ))}
          </div>
          <div className={styles.integrationBoundary}>
            <span>PROVIDER INTEGRATION BOUNDARY</span>
          </div>
          <div className={styles.futureField}>
            <p>NOT CONNECTED</p>
            {futureNodes.map((item, index) => (
              <div className={styles.futureNode} key={item}>
                <span>{String(index + 5).padStart(2, "0")}</span><strong>{item}</strong><StateLabel state="PLANNED" />
              </div>
            ))}
          </div>
        </div>
        <p className={styles.boundaryNote}>Nomos recommends only what its evidence supports. Tasking, reservations, telemetry, and commercial access remain unavailable until a provider is connected.</p>
      </div>
    </section>
  );
}

function NetworkTopology({ density }: { density: number }) {
  const nodes = [
    [15, 18, "CATALOG", 0], [30, 12, "EPHEMERIS", 1], [48, 18, "SENSOR", 2], [67, 13, "ORBIT", 1], [84, 20, "WINDOW", 2],
    [12, 48, "STATION", 0], [28, 56, "DOWNLINK", 1], [47, 48, "HANDOFF", 0], [68, 55, "REGION", 1], [86, 47, "TRANSFER", 2],
    [18, 82, "CUSTOMER", 0], [36, 76, "EDGE", 2], [52, 84, "CLOUD", 1], [72, 78, "STORAGE", 1], [88, 84, "RETURN", 2]
  ] as const;

  return (
    <div className={styles.networkTopology}>
      <div className={styles.networkRequest}>
        <span>ONE REQUEST</span><strong>OBJECTIVE</strong><small>INTERFACE UNCHANGED</small>
      </div>
      <div className={styles.networkCore}><NomosMark size={34} /><span>NOMOS</span></div>
      {nodes.map(([x, y, label, level]) => (
        <motion.div
          animate={{ opacity: level <= density ? 1 : 0.06, transform: level <= density ? "scale(1)" : "scale(0.75)" }}
          className={styles.networkNode}
          initial={false}
          key={label}
          style={{ left: `${x}%`, top: `${y}%` }}
          transition={{ duration: 0.55 }}
        >
          <i /><span>{label}</span>
        </motion.div>
      ))}
      <svg aria-hidden viewBox="0 0 1000 600" preserveAspectRatio="none">
        {nodes.map(([x, y, label, level]) => (
          <motion.path
            animate={{ opacity: level <= density ? (level === 0 ? 0.62 : 0.3) : 0.02, pathLength: level <= density ? 1 : 0 }}
            d={`M500 300 C${500 + (x - 50) * 3} ${300 + (y - 50) * 1.2} ${x * 10} ${y * 6} ${x * 10} ${y * 6}`}
            initial={false}
            key={label}
            transition={{ duration: 0.8 }}
          />
        ))}
      </svg>
    </div>
  );
}

function NetworkEffectScene() {
  const { ref, active } = useSceneStep<HTMLElement>(3);
  const reduced = useReducedMotion();
  const effectiveActive = reduced ? 2 : active;
  const labels = ["A handful of represented resources.", "More providers. More possible paths.", "A dense, heterogeneous space stack."];

  return (
    <section className={styles.networkScene} ref={ref}>
      <div className={styles.stickyStage}>
        <div className={`page-shell ${styles.networkInner}`}>
          <div className={styles.networkHeading}>
            <TechnicalLabel>NETWORK SCALE</TechnicalLabel>
            <h2>As the network grows,<br />the request doesn&rsquo;t change.</h2>
            <AnimatePresence mode="wait">
              <motion.p animate={{ opacity: 1 }} exit={{ opacity: 0 }} initial={{ opacity: 0 }} key={labels[effectiveActive]}>{labels[effectiveActive]}</motion.p>
            </AnimatePresence>
          </div>
          <NetworkTopology density={effectiveActive} />
          <div className={styles.densityMeter}>
            <span>DENSITY</span>
            {[0, 1, 2].map((item) => <i className={item <= effectiveActive ? styles.densityActive : ""} key={item} />)}
            <strong>{["REPRESENTED", "EXPANDING", "HETEROGENEOUS"][effectiveActive]}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}

function EndScene() {
  return (
    <section className={styles.endScene} aria-labelledby="capabilities-end-title">
      <div className={styles.endOrbit} aria-hidden><span /><span /><span /></div>
      <div className={`page-shell ${styles.endInner}`}>
        <TechnicalLabel>ONE INTERFACE</TechnicalLabel>
        <h2 id="capabilities-end-title">One request.<br />The whole space stack.</h2>
        <p>Infrastructure can remain heterogeneous. Access to it should not.</p>
        <div className={styles.endActions}>
          <LiquidButton href="/plan" variant="primary">Run a request</LiquidButton>
          <LiquidButton href="/examples" variant="ghost">View example request</LiquidButton>
          <Link href="/docs">API reference <span aria-hidden>→</span></Link>
        </div>
      </div>
    </section>
  );
}

export function CapabilitiesExperience() {
  useEffect(() => {
    document.body.classList.add("capabilities-route");
    return () => document.body.classList.remove("capabilities-route");
  }, []);

  return (
    <div className={styles.page}>
      <CapabilitiesHero />
      <RequestComplexityScene />
      <IntelligenceLoopScene />
      <EvidenceScene />
      <TruthScene />
      <BoundaryScene />
      <NetworkEffectScene />
      <EndScene />
    </div>
  );
}
