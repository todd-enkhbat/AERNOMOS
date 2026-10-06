"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { usePathname } from "next/navigation";
import { useEffect } from "react";

/**
 * Gives every route the same scroll grammar without forcing product controls into
 * marketing-style sticky scenes. Capabilities keeps its purpose-built pinned
 * sequence; other routes receive reversible section states and a scroll-linked
 * orbital field. Content remains fully visible when JavaScript or motion is off.
 */
export function SiteCadence() {
  const pathname = usePathname();
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll();
  const fieldTransform = useTransform(scrollYProgress, (value) =>
    reduced
      ? "translate3d(0, 0, 0) rotate(0deg)"
      : `translate3d(0, ${Math.round(value * -72)}px, 0) rotate(${(
          value * 5
        ).toFixed(2)}deg)`
  );

  useEffect(() => {
    const root = document.getElementById("main-content");
    if (!root || reduced || pathname === "/capabilities") {
      document.documentElement.classList.remove("site-cadence-ready");
      return;
    }

    const sections = Array.from(root.querySelectorAll<HTMLElement>("section")).filter(
      (section) =>
        !section.parentElement?.closest("section") &&
        section.dataset.cadence !== "off"
    );

    if (sections.length === 0) {
      document.documentElement.classList.remove("site-cadence-ready");
      return;
    }

    sections.forEach((section, index) => {
      section.dataset.siteCadenceSection = String(index + 1);
      const rect = section.getBoundingClientRect();
      section.dataset.siteCadenceState = rect.bottom < 0 ? "past" : "queued";
    });

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const section = entry.target as HTMLElement;
          if (entry.isIntersecting) {
            section.dataset.siteCadenceState = "active";
          } else {
            section.dataset.siteCadenceState =
              entry.boundingClientRect.bottom < 0 ? "past" : "queued";
          }
        }
      },
      {
        rootMargin: "-12% 0px -18% 0px",
        threshold: [0.06, 0.24, 0.55]
      }
    );

    sections.forEach((section) => observer.observe(section));
    document.documentElement.classList.add("site-cadence-ready");

    return () => {
      observer.disconnect();
      document.documentElement.classList.remove("site-cadence-ready");
      sections.forEach((section) => {
        delete section.dataset.siteCadenceSection;
        delete section.dataset.siteCadenceState;
      });
    };
  }, [pathname, reduced]);

  return (
    <motion.div
      aria-hidden
      className="site-cadence-field"
      style={reduced ? undefined : { transform: fieldTransform }}
    >
      <span />
      <span />
      <span />
    </motion.div>
  );
}
