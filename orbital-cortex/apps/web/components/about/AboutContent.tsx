import { NomosMark } from "@/components/brand/NomosMark";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { FadeIn } from "@/components/motion/primitives";
import { ArchiveImage } from "@/components/visual/ArchiveImage";

import styles from "./AboutContent.module.css";

const chapters = [
  {
    label: "01 / NOMOS",
    title: "Order among independent systems.",
    image: "/images/archive/voyager-record-team.jpg",
    alt: "Three members of the Voyager record team holding the record components",
    caption: "VOYAGER RECORD TEAM / 1977",
    body:
      "Nomos (νόμος) is the ordering principle behind how things are arranged. Space infrastructure has no single operator: public catalogs, orbital geometry, ground access, compute environments, and mission constraints all live in different systems. Nomos makes them reason together without pretending they are one provider."
  },
  {
    label: "02 / SIGNAL",
    title: "Distill the answer before it crosses the link.",
    image: "/images/archive/golden-record-display.jpg",
    alt: "The Sounds of Earth golden phonograph record",
    caption: "THE SOUNDS OF EARTH / NASA ARCHIVE",
    body:
      "Voyager’s Golden Record carried a legible artifact across enormous distance. That discipline matters in orbit, where bandwidth is scarce and contact windows are brief. Nomos determines what matters, where processing belongs, and what evidence must travel with the result."
  },
  {
    label: "03 / VERIFICATION",
    title: "A decision you can inspect.",
    image: "/images/archive/golden-record-lab.jpg",
    alternateImage: "/images/archive/golden-record-handling.jpg",
    alt: "A technician inspecting a reflective Voyager Golden Record in a laboratory",
    alternateAlt: "A technician handling a gold phonograph record with white gloves",
    caption: "GOLDEN RECORD LAB / JULY 1977",
    alternateCaption: "GOLDEN RECORD HANDLING / NASA ARCHIVE",
    body:
      "A credible plan states the public facts it used, the geometry it calculated, the assumptions it made, and the integrations it does not have. Nomos makes that evidence part of the mission brief, so a human can challenge the route before anyone acts on it."
  }
];

export function AboutContent() {
  return (
    <section className={styles.story} aria-labelledby="about-system-title">
      <FadeIn className={styles.intro} viewportMargin="0px" y={6}>
        <p className="chart-label text-gold">The operating idea</p>
        <h2 id="about-system-title">A control layer with memory.</h2>
        <p>
          Nomos is not another satellite company. It is the reasoning surface above
          the orbital, ground, and compute systems that already exist.
        </p>
      </FadeIn>

      <div className={styles.chapters}>
        {chapters.map((chapter, index) => (
          <article className={styles.chapter} key={chapter.label}>
            <ArchiveImage
              alt={chapter.alt}
              alternateAlt={chapter.alternateAlt}
              alternateCaption={chapter.alternateCaption}
              alternateSrc={chapter.alternateImage}
              caption={chapter.caption}
              className={styles.chapterImage}
              objectPosition={index === 0 ? "center 34%" : "center"}
              sizes="(max-width: 900px) 100vw, 58vw"
              src={chapter.image}
              tone={index === 1 ? "gold" : "neutral"}
            />
            <FadeIn className={styles.chapterCopy} viewportMargin="0px" y={6}>
              <p className={styles.index}>{chapter.label}</p>
              <h3>{chapter.title}</h3>
              <p className={styles.body}>{chapter.body}</p>
            </FadeIn>
          </article>
        ))}
      </div>

      <FadeIn className={styles.closing} viewportMargin="0px" y={6}>
        <div className={styles.brandLine}>
          <NomosMark size={40} />
          <div>
            <strong>Nomos Orbital</strong>
            <span>EST. AMONG THE STARS</span>
          </div>
        </div>
        <p>
          Today the product searches public catalogs, calculates orbital and contact
          geometry, compares feasible infrastructure patterns, and returns a
          source-backed technical brief. Live provider execution arrives through
          integrations and is never claimed early.
        </p>
        <div className={styles.actions}>
          <LiquidButton href="/plan" variant="primary">Build a mission plan</LiquidButton>
          <LiquidButton href="/docs" variant="outline">Read the API reference</LiquidButton>
        </div>
      </FadeIn>
    </section>
  );
}
