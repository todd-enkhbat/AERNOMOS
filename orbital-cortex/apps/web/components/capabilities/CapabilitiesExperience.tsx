"use client";

import { AnimatePresence, motion, useInView, useMotionValue, useSpring, useReducedMotion } from "framer-motion";
import { ArrowDown, ArrowRight, ArrowUpRight, Pause, Play } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState, type KeyboardEvent, type MouseEvent, type ReactNode } from "react";
import { useFinePointer } from "@/components/liquid/useFinePointer";
import styles from "./CapabilitiesExperience.module.css";

const asset = (name: string) => `/images/capabilities/${name}.${["cinematic-orbit", "exploded-instrument", "orbital-sculpture"].includes(name) ? "jpg" : "png"}`;
const layers = [
  { name: "Orbital", object: "orbital-satellite", subtitle: "Find the right observation.", description: "Search public satellite catalogs and calculate when orbital geometry supports the objective.", facts: ["Sentinel scenes via Microsoft Planetary Computer", "Contact opportunities from SGP4 orbital calculations"], boundary: "Commercial spacecraft tasking requires a provider integration.", source: "Public catalogs + orbital calculations", alt: "Conceptual gold-foil satellite with blue solar arrays" },
  { name: "Ground", object: "ground-antenna", subtitle: "Understand the handoff.", description: "Bring reference stations, communication windows, and delivery constraints into the same infrastructure decision.", facts: ["Cited station locations and provider references", "Mission-specific geometry and handoff constraints"], boundary: "Operational availability and pass reservations are not connected.", source: "Reference infrastructure + calculated geometry", alt: "Conceptual gold parabolic ground-station antenna" },
  { name: "Compute", object: "compute-module", subtitle: "Choose where the work belongs.", description: "Compare processing paths against timing, residency, and delivery requirements, with every assumption attached.", facts: ["Feasible, conditional, and rejected routes compared", "A real CPU fixture demo with measured output"], boundary: "Commercial onboard execution requires a provider integration.", source: "Route estimates + observed fixture execution", alt: "Conceptual blue and gold aerospace edge-computing module" }
] as const;
const proofs = [
  { title: "Search real catalogs", state: "REFERENCE", detail: "Sentinel imagery discovered through Microsoft Planetary Computer STAC.", source: "Provider-reported catalog records" },
  { title: "Calculate contact windows", state: "LIVE", detail: "SGP4 geometry from current or pinned orbital elements, with provenance attached.", source: "Calculated orbital geometry" },
  { title: "Compare execution paths", state: "LIVE", detail: "Feasible, conditional, and rejected routes, with constraints and estimates exposed.", source: "Estimated infrastructure routes" },
  { title: "Keep a traceable record", state: "LIVE", detail: "A private technical brief with sources, assumptions, alternatives, and explicit sharing.", source: "Session-bound request record" },
  { title: "Prove a processing step", state: "LIVE", detail: "Crop a fixture raster on the CPU worker and inspect the measured duration and output.", source: "Observed fixture execution" }
] as const;
const truths = [
  ["LIVE", "Working now", "Real data, calculations, or measured execution."],
  ["REFERENCE", "Source attached", "A cited public fact, with its origin visible."],
  ["SIMULATED", "Model disclosed", "Historical demo behavior, explicitly labeled."],
  ["PLANNED", "Integration needed", "Tasking, reservations, and commercial execution require provider access."]
] as const;

function GoldLink({ children, href = "/console" }: { children: ReactNode; href?: string }) {
  return <Link className={styles.goldButton} href={href}><span>{children}</span><ArrowUpRight size={18} strokeWidth={1.5} aria-hidden /></Link>;
}
function Status({ children }: { children: string }) {
  return <span className={styles.status} data-state={children}>{children}</span>;
}
function HardwareStage() {
  const [selected, setSelected] = useState(0);
  const [paused, setPaused] = useState(false);
  const [visible, setVisible] = useState(true);
  const preference = useReducedMotion();
  const [reduced, setReduced] = useState(false);
  const finePointer = useFinePointer();
  const stage = useRef<HTMLDivElement>(null);
  const buttons = useRef<Array<HTMLButtonElement | null>>([]);
  const inView = useInView(stage, { margin: "100px" });
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useSpring(y, { stiffness: 100, damping: 24 });
  const rotateY = useSpring(x, { stiffness: 100, damping: 24 });
  useEffect(() => { setReduced(Boolean(preference)); }, [preference]);
  useEffect(() => {
    const update = () => setVisible(!document.hidden);
    update(); document.addEventListener("visibilitychange", update);
    return () => document.removeEventListener("visibilitychange", update);
  }, []);
  const reset = () => { x.set(0); y.set(0); };
  const tilt = (event: MouseEvent<HTMLDivElement>) => {
    if (!finePointer || reduced || paused) return;
    const box = event.currentTarget.getBoundingClientRect();
    x.set(((event.clientX - box.left) / box.width - .5) * 7);
    y.set(-((event.clientY - box.top) / box.height - .5) * 5);
  };
  const choose = (index: number) => { setSelected(index); reset(); };
  const onKey = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    const next = event.key === "ArrowRight" ? (index + 1) % 3 : event.key === "ArrowLeft" ? (index + 2) % 3 : event.key === "Home" ? 0 : event.key === "End" ? 2 : -1;
    if (next < 0) return;
    event.preventDefault(); choose(next); buttons.current[next]?.focus();
  };
  const layer = layers[selected];
  return (
    <section className={styles.hardwareSection} aria-labelledby="hardware-title">
      <div className={`page-shell ${styles.sectionIntro}`}>
        <p className={styles.eyebrow}>Different infrastructure. One interface.</p>
        <h2 id="hardware-title">The whole stack.<br /><span>Within reach.</span></h2>
        <p>Explore the layers Nomos reasons across. The hardware stays heterogeneous. The request stays yours.</p>
      </div>
      <div className={`page-shell ${styles.stage}`} ref={stage} data-paused={paused || !visible || !inView || reduced}>
        <div className={styles.stageToolbar}>
          <div className={styles.tabs} role="tablist" aria-label="Infrastructure layer">
            {layers.map((item, index) => <button key={item.name} ref={node => { buttons.current[index] = node; }} id={`layer-tab-${index}`} role="tab" aria-selected={selected === index} aria-controls="hardware-panel" tabIndex={selected === index ? 0 : -1} onKeyDown={event => onKey(event, index)} onClick={() => choose(index)}>{item.name}<span aria-hidden>0{index + 1}</span></button>)}
          </div>
          <button className={styles.pause} onClick={() => { setPaused(value => !value); reset(); }} aria-label={paused ? "Resume illustration motion" : "Pause illustration motion"} aria-pressed={paused} type="button">{paused ? <Play size={14} aria-hidden /> : <Pause size={14} aria-hidden />}<span>{paused ? "Resume" : "Pause motion"}</span></button>
        </div>
        <div className={styles.layerPanel} role="tabpanel" id="hardware-panel" aria-labelledby={`layer-tab-${selected}`}>
          <div className={styles.objectSpace} onMouseMove={tilt} onMouseLeave={reset}>
            <div className={styles.objectGlow} aria-hidden />
            <motion.div className={styles.tilt} style={reduced ? undefined : { rotateX, rotateY }}>
              <AnimatePresence mode="wait" initial={false}>
                <motion.div key={layer.object} className={styles.objectEntry} initial={{ opacity: 0, y: reduced ? 0 : 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: reduced ? 0 : -10 }} transition={{ duration: reduced ? .1 : .24, ease: [0.23, 1, .32, 1] }}>
                  <div className={styles.float}><Image src={asset(layer.object)} alt={layer.alt} width={1280} height={1280} sizes="(max-width: 760px) 90vw, 50vw" className={styles.hardwareImage} /></div>
                </motion.div>
              </AnimatePresence>
            </motion.div>
          </div>
          <div className={styles.layerCopy}>
            <p className={styles.layerNumber}>0{selected + 1} / {layer.name}</p>
            <h3>{layer.subtitle}</h3>
            <p>{layer.description}</p>
            <ul>{layer.facts.map(fact => <li key={fact}><ArrowRight size={15} aria-hidden />{fact}</li>)}</ul>
            <div className={styles.layerBoundary}><Status>PLANNED</Status><p>{layer.boundary}</p></div>
            <small>{layer.source}</small>
          </div>
        </div>
        <p className={styles.artCaption}>Conceptual hardware illustration. No live connection or provider availability is implied.</p>
      </div>
    </section>
  );
}

export function CapabilitiesExperience() {
  return (
    <div className={styles.page}>
      <section className={styles.hero} aria-labelledby="capabilities-title">
        <Image src={asset("cinematic-orbit")} alt="Conceptual gold spacecraft above the blue curve of Earth" fill priority sizes="100vw" className={styles.heroArt} />
        <div className={styles.heroShade} aria-hidden />
        <div className={`page-shell ${styles.heroInner}`}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Space infrastructure software</p>
            <h1 id="capabilities-title">One request.<br />The whole<br />space stack.</h1>
            <p className={styles.heroLead}>Intelligence across orbital, ground, and compute infrastructure.</p>
            <GoldLink>Run a request</GoldLink>
          </div>
          <div className={styles.heroFoot}><a href="#hardware-title">Explore the capabilities <ArrowDown size={15} aria-hidden /></a><span>Conceptual infrastructure illustration</span></div>
        </div>
      </section>

      <HardwareStage />

      <section className={styles.intelligenceSection} aria-labelledby="intelligence-title">
        <div className={styles.assemblyArt}><Image src={asset("exploded-instrument")} alt="Exploded conceptual spacecraft instrument with gold antenna, satellite bus, and computing layers" fill sizes="(max-width: 760px) 100vw, 65vw" /><div aria-hidden /></div>
        <div className={`page-shell ${styles.intelligenceInner}`}>
          <div className={styles.intelligenceCopy}>
            <p className={styles.eyebrow}>The Nomos layer</p>
            <h2 id="intelligence-title">Complexity below.<br /><span>Clarity above.</span></h2>
            <p>Tell the network what you need. Nomos compares the paths through it and makes the reasoning visible.</p>
            <ol className={styles.reasoning}>
              <li><span>01</span><div><h3>Understand the objective.</h3><p>Area, timing, data, processing, and delivery constraints enter one request.</p></div></li>
              <li><span>02</span><div><h3>Resolve the infrastructure.</h3><p>Public sources and calculated geometry inform the available routes.</p></div></li>
              <li><span>03</span><div><h3>Explain the recommendation.</h3><p>See alternatives, estimates, evidence, and the integrations still missing.</p></div></li>
            </ol>
            <Link className={styles.textLink} href="/examples">Open a source-backed example <ArrowUpRight size={17} aria-hidden /></Link>
          </div>
        </div>
        <p className={styles.assemblyCaption}>Conceptual exploded hardware study</p>
      </section>

      <section className={`page-shell ${styles.proofSection}`} aria-labelledby="proof-title">
        <div className={styles.proofHeader}><p className={styles.eyebrow}>The working software</p><h2 id="proof-title">The evidence<br /><span>comes with it.</span></h2><p>Real sources. Calculated geometry. A record your team can inspect.</p></div>
        <div className={styles.proofList}>{proofs.map((proof, index) => <article key={proof.title}><span className={styles.proofNumber}>0{index + 1}</span><div><h3>{proof.title}</h3><p>{proof.detail}</p><small>{proof.source}</small></div><Status>{proof.state}</Status></article>)}</div>
      </section>

      <section className={styles.truthSection} aria-labelledby="truth-title">
        <div className={`page-shell ${styles.truthInner}`}><div className={styles.truthHeading}><p className={styles.eyebrow}>Truth, by design</p><h2 id="truth-title">Every claim<br />has a state.</h2><p>Working software, public references, simulation, and future integrations remain distinguishable.</p></div>
          <div className={styles.truthList}>{truths.map(([state, title, detail]) => <article key={state}><Status>{state}</Status><div><h3>{title}</h3><p>{detail}</p></div></article>)}</div>
        </div>
      </section>

      <section className={styles.closing} aria-labelledby="capabilities-end-title">
        <Image src={asset("orbital-sculpture")} alt="Conceptual gold orbital instrument unifying Earth, a satellite, an antenna, and a compute core" fill sizes="100vw" className={styles.closingArt} />
        <div className={styles.closingShade} aria-hidden />
        <div className={`page-shell ${styles.closingInner}`}><div><p className={styles.eyebrow}>One interface</p><h2 id="capabilities-end-title">The infrastructure<br />can stay complex.<br /><span>Access shouldn’t.</span></h2><p>Start with a request. See the route, the evidence, and what it will take to execute.</p><GoldLink>Try Nomos</GoldLink><Link className={styles.textLink} href="/docs">Read the API reference <ArrowUpRight size={17} aria-hidden /></Link></div><span className={styles.artCaption}>Conceptual orbital instrument</span></div>
      </section>
    </div>
  );
}
