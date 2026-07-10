"use client";

import { AnimatePresence, motion, useReducedMotion, useScroll } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

import { LiquidButton } from "@/components/liquid/LiquidButton";

const pillars = [
  {
    label: "Nomos",
    title: "Order among the stars",
    body: "Nomos (νόμος) is Greek for law and the ordering principle behind how things are arranged. Orbital infrastructure is a scheduling problem under contact windows, downlink budgets, and audit constraints. Nomos Orbital is the control plane that imposes that order."
  },
  {
    label: "Golden Record",
    title: "Distilled signal across distance",
    body: "In 1977 NASA bolted a gold phonograph to Voyager. The Golden Record carried the Sounds of Earth so a distant listener could reconstruct meaning from one artifact. Our mark is that disc. Bandwidth is scarce. Only the answer should cross the link."
  },
  {
    label: "Columbia",
    title: "Plasma lab roots",
    body: "Nomos grew out of Columbia plasma physics research: high-energy plasmas, precision instrumentation, and measuring what you cannot see directly. Routing is physics-aware scheduling. Every job emits a signed event log like a lab shot record."
  }
];

export function AboutScrollStory() {
  const sectionRef = useRef<HTMLElement>(null);
  const mountRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef(0);
  const reduced = useReducedMotion();
  const [activeIndex, setActiveIndex] = useState(0);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

  useEffect(() => {
    const unsub = scrollYProgress.on("change", (v) => {
      progressRef.current = v;
      if (v < 0.34) {
        setActiveIndex(0);
      } else if (v < 0.67) {
        setActiveIndex(1);
      } else {
        setActiveIndex(2);
      }
    });
    return unsub;
  }, [scrollYProgress]);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) {
      return;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.z = 3.4;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);

    const texture = new THREE.TextureLoader().load("/images/nomos-golden-record.png");
    texture.colorSpace = THREE.SRGBColorSpace;

    const disc = new THREE.Mesh(
      new THREE.CylinderGeometry(1.15, 1.15, 0.06, 128),
      new THREE.MeshStandardMaterial({
        map: texture,
        metalness: 0.92,
        roughness: 0.2,
        emissive: new THREE.Color("#3d3010"),
        emissiveIntensity: 0.18
      })
    );
    disc.rotation.x = Math.PI / 2;
    scene.add(disc);

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(1.34, 0.014, 8, 128),
      new THREE.MeshBasicMaterial({ color: 0xe3c05c, transparent: true, opacity: 0.45 })
    );
    ring.rotation.x = Math.PI / 2;
    scene.add(ring);

    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const key = new THREE.DirectionalLight(0xfff0c8, 1.5);
    key.position.set(2, 2, 4);
    scene.add(key);

    let raf = 0;

    const resize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      if (w === 0 || h === 0) {
        return;
      }
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    resize();
    window.addEventListener("resize", resize);

    const tick = () => {
      raf = requestAnimationFrame(tick);
      const p = progressRef.current;
      disc.rotation.z = p * Math.PI * 2.6 + performance.now() * 0.00006;
      disc.rotation.y = Math.sin(p * Math.PI) * 0.4;
      ring.rotation.z = disc.rotation.z;
      renderer.render(scene, camera);
    };
    tick();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      texture.dispose();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, []);

  const pillar = pillars[activeIndex];

  return (
    <section className="relative isolate" ref={sectionRef} style={{ height: "180vh" }}>
      <div className="sticky top-0 z-0 grid h-[min(100vh,900px)] items-center lg:grid-cols-[1fr_1fr]">
        <div className="relative flex h-full items-center justify-center py-10">
          <div
            aria-hidden
            className="pointer-events-none absolute h-[320px] w-[320px] rounded-full bg-gold/10 blur-[80px]"
          />
          <div
            className="relative h-[min(340px,68vw)] w-[min(340px,68vw)]"
            ref={mountRef}
          />
        </div>

        <div className="relative hidden h-full min-h-[280px] items-center overflow-hidden lg:flex">
          <AnimatePresence mode="wait">
            <motion.article
              animate={{ opacity: 1, y: 0 }}
              className="absolute inset-0 flex flex-col justify-center pr-8"
              exit={{ opacity: 0, y: -16 }}
              initial={{ opacity: 0, y: 16 }}
              key={pillar.label}
              transition={
                reduced
                  ? { duration: 0 }
                  : { type: "spring", stiffness: 320, damping: 32 }
              }
            >
              <p className="chart-label text-gold">{pillar.label}</p>
              <h3 className="display gold-shine mt-3 text-3xl leading-tight">
                {pillar.title}
              </h3>
              <p className="prose-compact mt-4 max-w-md text-silver">{pillar.body}</p>
            </motion.article>
          </AnimatePresence>
        </div>
      </div>

      <div className="page-shell space-y-12 pb-12 lg:hidden">
        {pillars.map((item) => (
          <article key={item.label}>
            <p className="chart-label text-gold">{item.label}</p>
            <h3 className="display mt-2 text-2xl text-cream">{item.title}</h3>
            <p className="prose-compact mt-3 text-muted">{item.body}</p>
          </article>
        ))}
        <LiquidButton href="/about" variant="outline">
          Full story
        </LiquidButton>
      </div>
    </section>
  );
}
