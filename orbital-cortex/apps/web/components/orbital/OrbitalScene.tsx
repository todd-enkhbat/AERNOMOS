"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

const GOLD = new THREE.Color("#c9a227");
const GOLD_BRIGHT = new THREE.Color("#e3c05c");
const CREAM = new THREE.Color("#f4efe6");
const SILVER = new THREE.Color("#b8b4ac");

type OrbitSpec = {
  radius: number;
  inclination: number;
  ascending: number;
  speed: number;
  phase: number;
  color: THREE.Color;
};

const ORBITS: OrbitSpec[] = [
  { radius: 1.55, inclination: 0.9, ascending: 0.2, speed: 0.22, phase: 0, color: GOLD },
  { radius: 1.78, inclination: 1.72, ascending: 1.4, speed: 0.17, phase: 2.1, color: SILVER },
  { radius: 2.02, inclination: 0.55, ascending: 2.6, speed: 0.13, phase: 4.2, color: GOLD_BRIGHT },
  { radius: 1.66, inclination: 1.15, ascending: 4.1, speed: 0.19, phase: 1.2, color: CREAM }
];

function orbitPoint(spec: OrbitSpec, t: number, target: THREE.Vector3) {
  const angle = spec.phase + t * spec.speed;
  const x = Math.cos(angle) * spec.radius;
  const y = Math.sin(angle) * spec.radius;
  target.set(x, y, 0);
  target.applyAxisAngle(new THREE.Vector3(1, 0, 0), spec.inclination);
  target.applyAxisAngle(new THREE.Vector3(0, 1, 0), spec.ascending);
  return target;
}

function buildGlobe(): THREE.Group {
  const globe = new THREE.Group();

  const latMaterial = new THREE.LineBasicMaterial({
    color: CREAM,
    transparent: true,
    opacity: 0.14
  });
  const lonMaterial = new THREE.LineBasicMaterial({
    color: CREAM,
    transparent: true,
    opacity: 0.1
  });

  const R = 1.18;

  for (let i = 1; i < 7; i += 1) {
    const phi = (i / 7) * Math.PI;
    const r = Math.sin(phi) * R;
    const y = Math.cos(phi) * R;
    const points: THREE.Vector3[] = [];
    for (let s = 0; s <= 72; s += 1) {
      const theta = (s / 72) * Math.PI * 2;
      points.push(new THREE.Vector3(Math.cos(theta) * r, y, Math.sin(theta) * r));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    globe.add(new THREE.Line(geo, i === 3 || i === 4 ? latMaterial : lonMaterial));
  }

  for (let i = 0; i < 10; i += 1) {
    const theta0 = (i / 10) * Math.PI * 2;
    const points: THREE.Vector3[] = [];
    for (let s = 0; s <= 72; s += 1) {
      const phi = (s / 72) * Math.PI;
      points.push(
        new THREE.Vector3(
          Math.sin(phi) * Math.cos(theta0) * R,
          Math.cos(phi) * R,
          Math.sin(phi) * Math.sin(theta0) * R
        )
      );
    }
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    globe.add(new THREE.Line(geo, lonMaterial));
  }

  // soft inner sphere to occlude back lines
  const occluder = new THREE.Mesh(
    new THREE.SphereGeometry(R * 0.985, 48, 48),
    new THREE.MeshBasicMaterial({ color: new THREE.Color("#0a0a0b"), transparent: true, opacity: 0.92 })
  );
  globe.add(occluder);

  // ground station pins
  const stationGeo = new THREE.SphereGeometry(0.022, 12, 12);
  const stationMat = new THREE.MeshBasicMaterial({ color: GOLD_BRIGHT });
  const stations = [
    { lat: 40.7, lon: -74.0 },
    { lat: 34.9, lon: -117.9 },
    { lat: 78.2, lon: 15.4 },
    { lat: -33.8, lon: 151.1 },
    { lat: 1.29, lon: 103.85 }
  ];
  for (const s of stations) {
    const phi = ((90 - s.lat) * Math.PI) / 180;
    const theta = ((s.lon + 180) * Math.PI) / 180;
    const mesh = new THREE.Mesh(stationGeo, stationMat);
    mesh.position.set(
      Math.sin(phi) * Math.cos(theta) * R,
      Math.cos(phi) * R,
      Math.sin(phi) * Math.sin(theta) * R
    );
    globe.add(mesh);
  }

  return globe;
}

function buildOrbitRing(spec: OrbitSpec): THREE.Line {
  const points: THREE.Vector3[] = [];
  for (let s = 0; s <= 128; s += 1) {
    const p = new THREE.Vector3();
    orbitPoint({ ...spec, speed: 0, phase: (s / 128) * Math.PI * 2 }, 0, p);
    points.push(p);
  }
  const geo = new THREE.BufferGeometry().setFromPoints(points);
  const mat = new THREE.LineBasicMaterial({
    color: spec.color,
    transparent: true,
    opacity: 0.28
  });
  return new THREE.Line(geo, mat);
}

export default function OrbitalScene({ className }: { className?: string }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      return;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 50);
    camera.position.set(0, 0.35, 4.6);

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.display = "block";

    const root = new THREE.Group();
    scene.add(root);

    const globe = buildGlobe();
    root.add(globe);

    const satMeshes: THREE.Mesh[] = [];
    const trailMats: THREE.LineBasicMaterial[] = [];
    for (const spec of ORBITS) {
      root.add(buildOrbitRing(spec));
      const sat = new THREE.Mesh(
        new THREE.SphereGeometry(0.035, 12, 12),
        new THREE.MeshBasicMaterial({ color: spec.color })
      );
      const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.075, 12, 12),
        new THREE.MeshBasicMaterial({ color: spec.color, transparent: true, opacity: 0.22 })
      );
      sat.add(glow);
      root.add(sat);
      satMeshes.push(sat);

      const trailMat = new THREE.LineBasicMaterial({
        color: spec.color,
        transparent: true,
        opacity: 0.5
      });
      trailMats.push(trailMat);
    }

    root.rotation.z = 0.14;

    let raf = 0;
    let mouseX = 0;
    let mouseY = 0;
    const target = new THREE.Vector3();

    const onMouse = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
      mouseY = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
    };
    window.addEventListener("mousemove", onMouse, { passive: true });

    const resize = () => {
      const { clientWidth, clientHeight } = container;
      if (clientWidth === 0 || clientHeight === 0) {
        return;
      }
      camera.aspect = clientWidth / clientHeight;
      // Pull the camera back on narrow/portrait containers so the full
      // orbit envelope stays in frame instead of cropping to a giant arc.
      camera.position.z = THREE.MathUtils.clamp(
        4.6 * (1.35 / camera.aspect),
        4.6,
        10.5
      );
      camera.updateProjectionMatrix();
      renderer.setSize(clientWidth, clientHeight, false);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(container);

    const reducedQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    let reduced = reducedQuery.matches;
    let inView = true;
    let docVisible =
      typeof document !== "undefined" ? !document.hidden : true;

    const start = performance.now();
    const drawFrame = () => {
      const t = reduced ? 0 : (performance.now() - start) / 1000;

      globe.rotation.y = t * 0.04;
      root.rotation.y += (mouseX * 0.12 - root.rotation.y) * 0.03;
      root.rotation.x += (mouseY * 0.08 - root.rotation.x) * 0.03;

      ORBITS.forEach((spec, i) => {
        orbitPoint(spec, t, target);
        satMeshes[i].position.copy(target);
      });

      renderer.render(scene, camera);
    };

    // Only spend GPU/CPU on the loop while the scene is visible, the tab is
    // focused, and motion is allowed. Otherwise render a single static frame.
    const shouldRun = () => inView && docVisible && !reduced;
    const loop = () => {
      drawFrame();
      raf = requestAnimationFrame(loop);
    };
    const startLoop = () => {
      if (raf || !shouldRun()) return;
      raf = requestAnimationFrame(loop);
    };
    const stopLoop = () => {
      if (raf) {
        cancelAnimationFrame(raf);
        raf = 0;
      }
    };
    const sync = () => {
      if (shouldRun()) {
        startLoop();
      } else {
        stopLoop();
        drawFrame();
      }
    };

    const io = new IntersectionObserver(
      (entries) => {
        inView = entries.some((entry) => entry.isIntersecting);
        sync();
      },
      { threshold: 0 }
    );
    io.observe(container);

    const onVisibility = () => {
      docVisible = !document.hidden;
      sync();
    };
    document.addEventListener("visibilitychange", onVisibility);

    const onReducedChange = (event: MediaQueryListEvent) => {
      reduced = event.matches;
      sync();
    };
    reducedQuery.addEventListener("change", onReducedChange);

    sync();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMouse);
      document.removeEventListener("visibilitychange", onVisibility);
      reducedQuery.removeEventListener("change", onReducedChange);
      io.disconnect();
      ro.disconnect();
      renderer.dispose();
      scene.traverse((obj) => {
        if (obj instanceof THREE.Mesh || obj instanceof THREE.Line) {
          obj.geometry.dispose();
          const material = obj.material as THREE.Material | THREE.Material[];
          if (Array.isArray(material)) {
            material.forEach((m) => m.dispose());
          } else {
            material.dispose();
          }
        }
      });
      container.removeChild(renderer.domElement);
    };
  }, []);

  return <div aria-hidden className={className} ref={containerRef} />;
}
