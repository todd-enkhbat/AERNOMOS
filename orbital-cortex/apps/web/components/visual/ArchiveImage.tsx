"use client";

import { motion, useMotionValue, useReducedMotion, useScroll, useSpring, useTransform } from "framer-motion";
import Image from "next/image";
import { useRef, useState } from "react";

import { useFinePointer } from "@/components/liquid/useFinePointer";

import styles from "./ArchiveImage.module.css";

type ArchiveImageProps = {
  alt: string;
  alternateAlt?: string;
  alternateCaption?: string;
  alternateObjectPosition?: string;
  alternateSrc?: string;
  caption?: string;
  className?: string;
  objectPosition?: string;
  priority?: boolean;
  sizes?: string;
  src: string;
  tone?: "blue" | "gold" | "neutral";
  unoptimized?: boolean;
};

export function ArchiveImage({
  alt,
  alternateAlt,
  alternateCaption,
  alternateObjectPosition = "center",
  alternateSrc,
  caption,
  className = "",
  objectPosition = "center",
  priority = false,
  sizes = "(max-width: 800px) 100vw, 60vw",
  src,
  tone = "neutral",
  unoptimized = false
}: ArchiveImageProps) {
  const ref = useRef<HTMLElement>(null);
  const [showAlternate, setShowAlternate] = useState(false);
  const finePointer = useFinePointer();
  const reduced = useReducedMotion();
  const pointerX = useMotionValue(0);
  const pointerY = useMotionValue(0);
  const rotateX = useSpring(pointerY, { stiffness: 180, damping: 26, mass: 0.5 });
  const rotateY = useSpring(pointerX, { stiffness: 180, damping: 26, mass: 0.5 });
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const imageY = useTransform(scrollYProgress, [0, 1], reduced ? ["0%", "0%"] : ["-4%", "4%"]);

  return (
    <motion.figure
      className={`${styles.frame} ${styles[tone]} ${className}`}
      initial={reduced ? false : { clipPath: "inset(2.5% 0 2.5% 0)", opacity: 0.92 }}
      onPointerLeave={() => {
        pointerX.set(0);
        pointerY.set(0);
      }}
      onPointerMove={(event) => {
        if (reduced || !finePointer) return;
        const rect = event.currentTarget.getBoundingClientRect();
        pointerX.set(((event.clientX - rect.left) / rect.width - 0.5) * 1.1);
        pointerY.set(((event.clientY - rect.top) / rect.height - 0.5) * -1.1);
      }}
      ref={ref}
      transition={reduced ? { duration: 0 } : { duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
      viewport={{ amount: 0.15, once: true }}
      whileInView={{ clipPath: "inset(0 0 0% 0)", opacity: 1 }}
    >
      <motion.div
        className={styles.imagePlane}
        style={{ rotateX: reduced ? 0 : rotateX, rotateY: reduced ? 0 : rotateY, y: imageY }}
      >
        <Image
          alt={showAlternate ? "" : alt}
          className={styles.image}
          fill
          priority={priority}
          sizes={sizes}
          src={src}
          style={{ objectPosition }}
          unoptimized={unoptimized}
        />
        {alternateSrc ? (
          <Image
            alt={showAlternate ? alternateAlt ?? alt : ""}
            aria-hidden={!showAlternate}
            className={`${styles.image} ${styles.alternateImage} ${
              showAlternate ? styles.alternateImageVisible : ""
            }`}
            fill
            sizes={sizes}
            src={alternateSrc}
            style={{ objectPosition: alternateObjectPosition }}
          />
        ) : null}
      </motion.div>
      <span aria-hidden className={styles.tone} />
      <span aria-hidden className={styles.grain} />
      {alternateSrc ? (
        <motion.button
          aria-label={showAlternate ? "Show primary archive plate" : "Show alternate archive plate"}
          aria-pressed={showAlternate}
          className={styles.plateToggle}
          onClick={() => setShowAlternate((current) => !current)}
          type="button"
          whileTap={reduced ? undefined : { scale: 0.97 }}
        >
          Plate {showAlternate ? "02" : "01"} / 02
        </motion.button>
      ) : null}
      {caption ? (
        <figcaption>{showAlternate ? alternateCaption ?? caption : caption}</figcaption>
      ) : null}
    </motion.figure>
  );
}
