"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import Link from "next/link";
import { useEffect, useRef } from "react";
import * as THREE from "three";

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

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

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
    const unsub = scrollYProgress.on("change", (v) => {
      progressRef.current = v;
    });

    const resize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
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
      unsub();
      window.removeEventListener("resize", resize);
      texture.dispose();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [scrollYProgress]);

  const p0 = useTransform(scrollYProgress, [0, 0.28, 0.32], [1, 1, 0]);
  const p1 = useTransform(scrollYProgress, [0.28, 0.35, 0.62, 0.66], [0, 1, 1, 0]);
  const p2 = useTransform(scrollYProgress, [0.62, 0.68, 0.95, 1], [0, 1, 1, 0]);
  const opacities = [p0, p1, p2];

  return (
    <section className="relative" ref={sectionRef} style={{ height: "240vh" }}>
      <div className="sticky top-0 grid h-screen items-center lg:grid-cols-[1fr_1fr]">
        <div className="relative flex h-full items-center justify-center">
          <div
            aria-hidden
            className="pointer-events-none absolute h-[380px] w-[380px] rounded-full bg-gold/12 blur-[90px]"
          />
          <div
            className="relative h-[min(380px,72vw)] w-[min(380px,72vw)]"
            ref={mountRef}
          />
        </div>

        <div className="relative hidden h-full items-center lg:flex">
          {pillars.map((pillar, index) => (
            <motion.article
              className="absolute inset-0 flex flex-col justify-center pr-8"
              key={pillar.label}
              style={{ opacity: opacities[index], pointerEvents: "none" }}
            >
              <p className="chart-label text-gold">{pillar.label}</p>
              <h3 className="display gold-shine mt-3 text-3xl leading-tight">
                {pillar.title}
              </h3>
              <p className="prose-compact mt-4 max-w-md text-muted">{pillar.body}</p>
            </motion.article>
          ))}
        </div>
      </div>

      <div className="page-shell space-y-16 pb-16 lg:hidden">
        {pillars.map((pillar) => (
          <article key={pillar.label}>
            <p className="chart-label text-gold">{pillar.label}</p>
            <h3 className="display mt-2 text-2xl text-cream">{pillar.title}</h3>
            <p className="prose-compact mt-3 text-muted">{pillar.body}</p>
          </article>
        ))}
        <Link className="btn-gold inline-flex" href="/about">
          Full story
        </Link>
      </div>
    </section>
  );
}
