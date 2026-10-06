"use client";

import { useReducedMotion, useScroll } from "framer-motion";
import { useRef } from "react";
import { GoldenRecord } from "./GoldenRecord";
import styles from "./AboutScrollStory.module.css";

const pillars = [
  {
    label: "Nomos",
    title: "Order among the stars",
    body: "Nomos (νόμος) is Greek for law and the ordering principle behind how things are arranged. Orbital infrastructure is a planning problem under contact windows, data availability, policy limits, and processing constraints. Nomos is the intelligence layer that makes those facts legible together."
  },
  {
    label: "Golden Record",
    title: "Distilled signal across distance",
    body: "In 1977 NASA bolted a gold phonograph to Voyager. The Golden Record carried the Sounds of Earth so a distant listener could reconstruct meaning from one artifact. Our mark is that disc. Bandwidth is scarce. Only the answer should cross the link."
  },
  {
    label: "Verification",
    title: "A decision with memory",
    body: "A mission brief should preserve why a path was selected: the public facts, calculation methods, assumptions, rejected alternatives, and missing integrations. Nomos returns that evidence with the recommendation so the decision can be inspected instead of merely trusted."
  }
];

export function AboutScrollStory() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start center", "end center"]
  });

  return (
    <div className={`page-shell ${styles.story}`} ref={sectionRef}>
      <div className={styles.recordColumn}>
        <figure className={styles.record}>
          <GoldenRecord progress={scrollYProgress} reduced={Boolean(reduced)} />
          <figcaption>THE GOLDEN RECORD <span>VOYAGER / 1977</span></figcaption>
        </figure>
      </div>
      <div className={styles.chapters}>
        {pillars.map((pillar, index) => (
          <article className={styles.chapter} key={pillar.label}>
            <p className={styles.label}><span>0{index + 1}</span> {pillar.label}</p>
            <h3>{pillar.title}</h3>
            <p className={styles.body}>{pillar.body}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
