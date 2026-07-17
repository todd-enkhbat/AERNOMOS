"use client";

import { AnimatePresence, motion, useReducedMotion, useScroll } from "framer-motion";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const SPUTNIK_URL = "/3d-models/sputnik_satellite.opt.glb";

const pillars = [
  {
    label: "Sputnik",
    title: "First signal from orbit",
    body: "The first artificial satellite proved a relay could survive above the atmosphere. Nomos treats every node in the mesh as a candidate with windows, scores, and constraints."
  },
  {
    label: "Fleet geometry",
    title: "One craft, one frame",
    body: "Scroll to tumble Sputnik through the routing volume. Ground stations, cloud fallback, and orbital compute share the same coordinate system you see in the console below."
  },
  {
    label: "Live mesh",
    title: "Into the registry",
    body: "SGP4 passes are precomputed from a pinned public TLE snapshot. The visual hands off to the reference registry, where real orbital geometry and simulated compute candidates remain clearly labeled."
  }
];

/** Scale first, then re-center — avoids Sketchfab's huge internal offsets drifting off-screen. */
function fitModel(group: THREE.Group, model: THREE.Object3D, targetSize: number) {
  group.add(model);
  model.updateMatrixWorld(true);

  const box = new THREE.Box3().setFromObject(model);
  if (box.isEmpty()) {
    return;
  }

  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 0.0001);
  const scale = targetSize / maxDim;
  group.scale.setScalar(scale);

  group.updateMatrixWorld(true);
  const fitted = new THREE.Box3().setFromObject(group);
  const center = fitted.getCenter(new THREE.Vector3());
  group.position.set(-center.x, -center.y, -center.z);
}

function prepareMaterials(root: THREE.Object3D) {
  root.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) {
      return;
    }
    child.frustumCulled = false;
    const materials = Array.isArray(child.material) ? child.material : [child.material];
    materials.forEach((material) => {
      material.side = THREE.DoubleSide;
      if ("map" in material && material.map instanceof THREE.Texture) {
        material.map.colorSpace = THREE.SRGBColorSpace;
      }
      if ("emissive" in material && material.emissive instanceof THREE.Color) {
        material.emissive.set("#1a1408");
        material.emissiveIntensity = 0.12;
      }
    });
  });
}

function disposeCraft(root: THREE.Object3D) {
  root.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) {
      return;
    }
    child.geometry?.dispose();
    const { material } = child;
    if (Array.isArray(material)) {
      material.forEach((entry) => entry.dispose());
    } else {
      material?.dispose();
    }
  });
}

export function SputnikScrollStory() {
  const sectionRef = useRef<HTMLElement>(null);
  const mountRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef(0);
  const reduced = useReducedMotion();
  const [activeIndex, setActiveIndex] = useState(0);
  const [ready, setReady] = useState(false);
  const [loadError, setLoadError] = useState(false);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

  useEffect(() => {
    const unsub = scrollYProgress.on("change", (value) => {
      progressRef.current = value;
      if (value < 0.34) {
        setActiveIndex(0);
      } else if (value < 0.67) {
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

    let disposed = false;
    let loadedModel: THREE.Object3D | null = null;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 200);
    camera.position.set(0, 0, 4.2);

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    } catch {
      setLoadError(true);
      setReady(true);
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);

    const craft = new THREE.Group();
    scene.add(craft);

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(1.55, 0.014, 8, 128),
      new THREE.MeshBasicMaterial({ color: 0xe3c05c, transparent: true, opacity: 0.42 })
    );
    ring.rotation.x = Math.PI / 2;
    scene.add(ring);

    scene.add(new THREE.AmbientLight(0xffffff, 0.85));
    scene.add(new THREE.HemisphereLight(0xfff4d6, 0x1a1814, 0.65));
    const key = new THREE.DirectionalLight(0xfff0c8, 1.85);
    key.position.set(3, 4, 5);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xc9c4bc, 0.75);
    fill.position.set(-4, -1, 3);
    scene.add(fill);

    const loader = new GLTFLoader();
    loader.load(
      SPUTNIK_URL,
      (gltf) => {
        if (disposed) {
          return;
        }
        const model = gltf.scene.clone(true);
        prepareMaterials(model);
        const anchor = new THREE.Group();
        fitModel(anchor, model, 3.1);
        anchor.rotation.x = 0.15;
        craft.add(anchor);
        loadedModel = model;
        setReady(true);
        setLoadError(false);
      },
      undefined,
      () => {
        if (!disposed) {
          setLoadError(true);
          setReady(true);
        }
      }
    );

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
      const p = progressRef.current;
      const drift = reduced ? 0 : performance.now() * 0.00007;

      craft.rotation.y = p * Math.PI * 2.4 + drift;
      craft.rotation.x = 0.12 + Math.sin(p * Math.PI) * 0.32;
      craft.rotation.z = Math.sin(p * Math.PI * 0.85) * 0.18;
      craft.position.y = Math.sin(p * Math.PI * 1.2) * 0.06;

      ring.rotation.z = craft.rotation.y * 0.85;
      ring.rotation.x = Math.PI / 2 + Math.sin(p * Math.PI) * 0.06;

      renderer.render(scene, camera);
      if (!reduced) {
        raf = requestAnimationFrame(tick);
      }
    };
    tick();

    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      if (loadedModel) {
        disposeCraft(loadedModel);
      }
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [reduced]);

  const pillar = pillars[activeIndex];

  return (
    <section className="scroll-story-stage relative isolate" ref={sectionRef}>
      <div className="scroll-story-stage__sticky z-0 grid items-center lg:grid-cols-[1fr_1fr]">
        <div className="relative flex h-full items-center justify-center py-10">
          <div
            aria-hidden
            className="pointer-events-none absolute h-[320px] w-[320px] rounded-full bg-gold/10 blur-[80px]"
          />
          <div
            className={`relative h-[min(360px,72vw)] w-[min(360px,72vw)] transition-opacity duration-700 ${
              ready ? "opacity-100" : "opacity-35"
            }`}
            ref={mountRef}
          />
          {loadError ? (
            <div className="absolute inset-[10%] overflow-hidden rounded-[28px] border border-gold/15 opacity-75">
              <Image
                alt="Orbital spacecraft above Earth"
                className="object-cover"
                fill
                sizes="320px"
                src="/images/network/orbital-nodes.png"
              />
              <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(5,5,6,0.2),rgba(5,5,6,0.72))]" />
            </div>
          ) : null}
        </div>

        <div className="relative hidden h-full min-h-[280px] items-center overflow-hidden lg:flex">
          <AnimatePresence mode="wait">
            <motion.article
              animate={{ opacity: 1, transform: "translateY(0px)" }}
              className="absolute inset-0 flex flex-col justify-center pr-8"
              exit={{ opacity: 0, transform: "translateY(-16px)" }}
              initial={{ opacity: 0, transform: "translateY(16px)" }}
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
      </div>
    </section>
  );
}
