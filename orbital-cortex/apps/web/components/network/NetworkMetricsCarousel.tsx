"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { ChevronLeft, ChevronRight, Cloud, RadioTower, Satellite, Signal } from "lucide-react";
import Image from "next/image";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";

import { LiquidButton } from "@/components/liquid";

type Slide = {
  id: string;
  step: string;
  title: string;
  caption: string;
  image: string;
  imageAlt: string;
  imageScale?: number;
  objectPosition?: string;
  icon: LucideIcon;
};

const slides: Slide[] = [
  {
    id: "orbital",
    step: "01",
    title: "Orbital nodes",
    caption:
      "Simulated on-orbit compute candidates scored for model fit, contact windows, and downlink budget.",
    image: "/images/network/orbital-nodes.png",
    imageAlt: "Hubble Space Telescope in the shuttle cargo bay above Earth",
    imageScale: 1.08,
    objectPosition: "center center",
    icon: Satellite
  },
  {
    id: "ground",
    step: "02",
    title: "Ground stations",
    caption:
      "Public reference locations used for SGP4 visibility calculations. Nomos does not operate or book these sites.",
    image: "/images/network/ground-stations.png",
    imageAlt: "Satellite dish farm on a hillside ground station",
    icon: RadioTower
  },
  {
    id: "cloud",
    step: "03",
    title: "Cloud nodes",
    caption:
      "Simulated terrestrial fallback when a pass is missed or policy prefers a cloud route. The same decision audit applies.",
    image: "/images/network/cloud-nodes.png",
    imageAlt: "Twin satellites in low Earth orbit above the cloud layer",
    icon: Cloud
  },
  {
    id: "jobs",
    step: "04",
    title: "Active jobs",
    caption:
      "Shared public demo jobs currently queued or running through the production API and worker.",
    image: "/images/network/active-jobs.png",
    imageAlt: "Multiplexed signal map of active routing jobs",
    icon: Signal
  }
];

const TICK_COUNT = 40;

type NetworkMetricsCarouselProps = {
  orbitalCount: number;
  groundStationCount: number;
  cloudCount: number;
  activeJobs: number;
};

function valueForSlide(id: string, props: NetworkMetricsCarouselProps): string {
  switch (id) {
    case "orbital":
      return String(props.orbitalCount);
    case "ground":
      return String(props.groundStationCount);
    case "cloud":
      return String(props.cloudCount);
    case "jobs":
      return String(props.activeJobs);
    default:
      return "n/a";
  }
}

export function NetworkMetricsCarousel(props: NetworkMetricsCarouselProps) {
  const reduced = useReducedMotion();
  const [active, setActive] = useState(0);
  const [offset, setOffset] = useState(0);
  const viewportRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const slideRefs = useRef<(HTMLElement | null)[]>([]);
  const total = slides.length;

  const recenter = useCallback(() => {
    const viewport = viewportRef.current;
    const slide = slideRefs.current[active];
    if (!viewport || !slide) {
      return;
    }
    const center = slide.offsetLeft + slide.offsetWidth / 2;
    setOffset(viewport.clientWidth / 2 - center);
  }, [active]);

  useLayoutEffect(() => {
    recenter();
    const id = requestAnimationFrame(() => recenter());
    return () => cancelAnimationFrame(id);
  }, [recenter]);

  useEffect(() => {
    const onResize = () => recenter();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [recenter]);

  const go = useCallback(
    (dir: -1 | 1) => {
      setActive((index) => Math.max(0, Math.min(total - 1, index + dir)));
    },
    [total]
  );

  const markerIndex = Math.round((active / (total - 1)) * (TICK_COUNT - 1));

  return (
    <div className="mt-8">
      <h2 className="display max-w-3xl text-2xl leading-tight text-cream md:text-[2rem]">
        Four inputs the router can explain
      </h2>

      <div className="relative mt-6 overflow-hidden" ref={viewportRef}>
        <motion.div
          animate={{ transform: `translateX(${offset}px)` }}
          className="flex items-end gap-3 md:gap-4"
          ref={trackRef}
          transition={
            reduced ? { duration: 0 } : { type: "spring", stiffness: 280, damping: 32 }
          }
        >
          {slides.map((slide, index) => {
            const isActive = index === active;
            const Icon = slide.icon;
            const value = valueForSlide(slide.id, props);

            return (
              <motion.article
                animate={{
                  opacity: isActive ? 1 : 0.38,
                  transform: isActive ? "scale(1)" : "scale(0.84)"
                }}
                aria-current={isActive ? "true" : undefined}
                aria-label={`Show ${slide.title}`}
                className={[
                  "relative shrink-0 origin-center cursor-pointer overflow-hidden rounded-[18px] border bg-[#050506] transition-shadow duration-200",
                  isActive
                    ? "z-20 border-gold/35 shadow-[0_24px_80px_rgba(0,0,0,0.55)]"
                    : "z-10 border-white/8"
                ].join(" ")}
                key={slide.id}
                onClick={() => setActive(index)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    setActive(index);
                  } else if (event.key === "ArrowLeft") {
                    go(-1);
                  } else if (event.key === "ArrowRight") {
                    go(1);
                  }
                }}
                ref={(node) => {
                  slideRefs.current[index] = node;
                }}
                style={{
                  width: "min(78vw, 680px)",
                  height: "min(48vh, 440px)"
                }}
                role="button"
                tabIndex={0}
                transition={
                  reduced
                    ? { duration: 0 }
                    : { type: "spring", stiffness: 280, damping: 32 }
                }
              >
                <Image
                  alt={slide.imageAlt}
                  className="object-cover"
                  fill
                  onLoad={recenter}
                  priority={index <= 1}
                  sizes={isActive ? "(max-width: 860px) 78vw, 860px" : "(max-width: 300px) 34vw, 300px"}
                  src={slide.image}
                  style={{
                    objectPosition: slide.objectPosition ?? "center",
                    transform: `scale(${slide.imageScale ?? 1.04})`
                  }}
                />
                <div
                  className={[
                    "absolute inset-0",
                    isActive
                      ? "bg-gradient-to-t from-black/80 via-black/20 to-black/5"
                      : "bg-black/45"
                  ].join(" ")}
                />

                <div
                  className={[
                    "absolute bottom-0 left-0 right-0 p-4 transition-opacity duration-200 md:p-5",
                    isActive ? "max-w-lg" : "max-w-[90%]"
                  ].join(" ")}
                >
                  <div className="liquid-glass liquid-glass--card !rounded-xl !p-3.5 !shadow-none md:!p-4">
                    <div className="flex items-start gap-3">
                      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-gold/25 bg-gold/10 text-gold">
                        <Icon size={17} strokeWidth={1.8} />
                      </span>
                      <div className="min-w-0">
                        <p className="chart-label text-gold">{slide.step}</p>
                        <p
                          className={[
                            "mt-1 font-medium uppercase tracking-[0.12em] text-cream",
                            isActive ? "text-sm md:text-base" : "text-[11px]"
                          ].join(" ")}
                        >
                          {slide.title}
                        </p>
                        {isActive ? (
                          <>
                            <p className="metric-value mt-2 text-3xl text-gold-bright md:text-4xl">
                              {value}
                            </p>
                            <p className="prose-compact mt-2 text-xs text-muted md:text-sm">
                              {slide.caption}
                            </p>
                          </>
                        ) : (
                          <p className="metric-value mt-1.5 text-lg text-cream/80">{value}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.article>
            );
          })}
        </motion.div>
      </div>

      <div className="mt-6 grid items-end gap-4 md:grid-cols-[1fr_auto_auto]">
        <p className="chart-label max-w-xs text-[10px] leading-relaxed text-muted-dark md:text-[11px]">
          REFERENCE ROUTING REGISTRY
          <br />
          ORBITAL · GROUND · CLOUD · JOBS
        </p>

        <div
          aria-label={`Section ${active + 1} of ${total}`}
          className="flex flex-col items-center gap-2 justify-self-center"
          role="status"
        >
          <div className="flex items-end gap-[2px]">
            {Array.from({ length: TICK_COUNT }).map((_, index) => {
              const isMarker = index === markerIndex;
              if (isMarker) {
                return <span className="mb-0.5 h-3 w-2.5 shrink-0 bg-gold" key={index} />;
              }
              return (
                <span
                  className="w-px shrink-0 bg-cream/20"
                  key={index}
                  style={{ height: index % 5 === 0 ? 14 : 8 }}
                />
              );
            })}
          </div>
          <p className="chart-label text-[10px] text-muted">
            {active + 1} of {total}
          </p>
        </div>

        <div className="flex items-center gap-2 justify-self-end">
          <LiquidButton
            aria-label="Previous section"
            className="!px-3 !py-3"
            disabled={active === 0}
            onClick={() => go(-1)}
            variant="outline"
          >
            <ChevronLeft size={18} strokeWidth={1.8} />
          </LiquidButton>
          <LiquidButton
            aria-label="Next section"
            className="!px-3 !py-3"
            disabled={active === total - 1}
            onClick={() => go(1)}
            variant="outline"
          >
            <ChevronRight size={18} strokeWidth={1.8} />
          </LiquidButton>
        </div>
      </div>
    </div>
  );
}
