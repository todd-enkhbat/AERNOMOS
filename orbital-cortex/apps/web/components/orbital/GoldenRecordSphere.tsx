"use client";

import { useScroll, useTransform } from "framer-motion";
import { motion } from "framer-motion";
import { useEffect, useRef } from "react";
import * as THREE from "three";

type GoldenRecordSphereProps = {
  className?: string;
  /** Total scroll height of the parent section. */
  scrollHeight?: string;
};

/**
 * Voyager Golden Record as a lit 3D disc. Rotation and tilt follow scroll progress
 * through the parent section (sticky stage, VAST-style).
 */
export function GoldenRecordSphere({
  className = "",
  scrollHeight = "220vh"
}: GoldenRecordSphereProps) {
  const sectionRef = useRef<HTMLElement>(null);
  const mountRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

  const labelOpacity = useTransform(scrollYProgress, [0, 0.15, 0.85, 1], [0, 1, 1, 0]);
  const glowScale = useTransform(scrollYProgress, [0, 0.5, 1], [0.85, 1.08, 0.95]);

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

    const loader = new THREE.TextureLoader();
    const texture = loader.load("/images/nomos-golden-record.png");
    texture.colorSpace = THREE.SRGBColorSpace;

    const disc = new THREE.Mesh(
      new THREE.CylinderGeometry(1.15, 1.15, 0.06, 128),
      new THREE.MeshStandardMaterial({
        map: texture,
        metalness: 0.92,
        roughness: 0.22,
        emissive: new THREE.Color("#3d3010"),
        emissiveIntensity: 0.15
      })
    );
    disc.rotation.x = Math.PI / 2;
    scene.add(disc);

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(1.32, 0.012, 8, 128),
      new THREE.MeshBasicMaterial({ color: 0xc9a227, transparent: true, opacity: 0.55 })
    );
    ring.rotation.x = Math.PI / 2;
    scene.add(ring);

    const ambient = new THREE.AmbientLight(0xffffff, 0.35);
    const key = new THREE.DirectionalLight(0xfff0c8, 1.4);
    key.position.set(2, 2, 4);
    const rim = new THREE.DirectionalLight(0xe3c05c, 0.8);
    rim.position.set(-3, -1, -2);
    scene.add(ambient, key, rim);

    let raf = 0;
    let progress = 0;

    const unsub = scrollYProgress.on("change", (v) => {
      progress = v;
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
      disc.rotation.z = progress * Math.PI * 2.4 + performance.now() * 0.00008;
      disc.rotation.y = Math.sin(progress * Math.PI) * 0.35;
      disc.rotation.x = Math.PI / 2 + Math.cos(progress * Math.PI * 0.5) * 0.18;
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

  return (
    <section
      className={`relative ${className}`.trim()}
      ref={sectionRef}
      style={{ height: scrollHeight }}
    >
      <div className="sticky top-0 flex h-screen items-center justify-center overflow-hidden">
        <motion.div
          aria-hidden
          className="pointer-events-none absolute h-[420px] w-[420px] rounded-full bg-gold/10 blur-[80px]"
          style={{ scale: glowScale }}
        />
        <div className="relative h-[min(420px,70vw)] w-[min(420px,70vw)]" ref={mountRef} />
        <motion.p
          className="chart-label pointer-events-none absolute bottom-[18%] text-gold/70"
          style={{ opacity: labelOpacity }}
        >
          Drag scroll to spin the record
        </motion.p>
      </div>
    </section>
  );
}
