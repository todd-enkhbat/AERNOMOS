"use client";

import type { MotionValue } from "framer-motion";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import styles from "./AboutScrollStory.module.css";

/** A solid, beveled record. All geometry shares one transform and reflection field. */
export function GoldenRecord({ progress, reduced }: { progress: MotionValue<number>; reduced: boolean }) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;
    setReady(false);
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    } catch { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.setClearColor(0x001045, 0);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    mount.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 30);
    camera.position.z = 4.8;
    const pmrem = new THREE.PMREMGenerator(renderer);
    const room = new RoomEnvironment();
    const environment = pmrem.fromScene(room, 0.04);
    scene.environment = environment.texture;
    room.dispose();
    pmrem.dispose();

    const disc = new THREE.Group();
    scene.add(disc);
    const gold = new THREE.MeshStandardMaterial({ color: 0xe5b747, metalness: 1, roughness: 0.25 });
    const faceMaterial = new THREE.MeshStandardMaterial({ metalness: 0.65, roughness: 0.38, envMapIntensity: 1.5 });
    const face = new THREE.Mesh(new THREE.CircleGeometry(1.12, 128), faceMaterial);
    // Keep the textured face above the cylinder cap to avoid depth flicker.
    face.position.z = 0.065;
    const edge = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, 0.12, 128), gold);
    edge.rotation.x = Math.PI / 2;
    disc.add(edge, face);
    for (const z of [-0.05, 0.05]) {
      const bevel = new THREE.Mesh(new THREE.TorusGeometry(1.112, 0.018, 12, 128), gold);
      bevel.position.z = z;
      disc.add(bevel);
    }
    // Fine concentric grooves on the reverse catch the same studio illumination.
    for (let radius = 0.28; radius < 1.08; radius += 0.025) {
      const groove = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.002, 4, 128), gold);
      groove.position.z = -0.062;
      disc.add(groove);
    }
    const light = new THREE.DirectionalLight(0xffedca, 3);
    light.position.set(-3, 4, 5);
    scene.add(light, new THREE.HemisphereLight(0xdce7ff, 0x73521a, 1.4));

    let disposed = false;
    let loaded = false;
    let revealed = false;
    let visible = false;
    let raf = 0;
    let angle = progress.get();
    let lastTime = 0;
    const pointer = new THREE.Vector2();
    const pointerTarget = new THREE.Vector2();
    const render = (time: number) => {
      raf = 0;
      const delta = Math.min((time - lastTime) / 1000 || 0.016, 0.05);
      lastTime = time;
      const target = reduced ? 0.22 : progress.get();
      angle = reduced ? target : THREE.MathUtils.damp(angle, target, 7, delta);
      pointer.lerp(pointerTarget, 1 - Math.exp(-7 * delta));
      disc.rotation.set(-0.24 + pointer.y * 0.08, -0.65 + Math.sin(angle * Math.PI) * 0.25 + pointer.x * 0.12, -0.18 + angle * Math.PI * 0.65);
      renderer.render(scene, camera);
      if (loaded && !revealed) { revealed = true; setReady(true); }
      if (!reduced && visible && document.visibilityState === "visible") raf = requestAnimationFrame(render);
    };
    const requestRender = () => { if (!disposed && !raf) raf = requestAnimationFrame(render); };
    const texture = new THREE.TextureLoader().load('/images/nomos-golden-record-disc.png', () => {
      if (disposed) return;
      loaded = true;
      requestRender();
    });
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.center.set(0.5, 0.5);
    texture.repeat.set(0.88, 0.88);
    texture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    faceMaterial.map = texture;

    const resize = new ResizeObserver(() => {
      const { width, height } = mount.getBoundingClientRect();
      if (!width || !height) return;
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      requestRender();
    });
    resize.observe(mount);
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) requestRender();
      else { cancelAnimationFrame(raf); raf = 0; }
    });
    observer.observe(mount);
    const onVisibility = () => {
      if (document.visibilityState === "visible" && visible) requestRender();
      else { cancelAnimationFrame(raf); raf = 0; }
    };
    const onContextLost = (event: Event) => {
      event.preventDefault();
      loaded = false;
      revealed = false;
      cancelAnimationFrame(raf);
      raf = 0;
      setReady(false);
    };
    const onContextRestored = () => { loaded = true; requestRender(); };
    const onPointer = (event: PointerEvent) => {
      if (reduced || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
      const rect = mount.getBoundingClientRect();
      pointerTarget.set((event.clientX - rect.left) / rect.width - 0.5, (event.clientY - rect.top) / rect.height - 0.5);
    };
    const resetPointer = () => pointerTarget.set(0, 0);
    mount.addEventListener('pointermove', onPointer);
    mount.addEventListener('pointerleave', resetPointer);
    renderer.domElement.addEventListener('webglcontextlost', onContextLost);
    renderer.domElement.addEventListener('webglcontextrestored', onContextRestored);
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      observer.disconnect();
      resize.disconnect();
      mount.removeEventListener('pointermove', onPointer);
      mount.removeEventListener('pointerleave', resetPointer);
      document.removeEventListener('visibilitychange', onVisibility);
      renderer.domElement.removeEventListener('webglcontextlost', onContextLost);
      renderer.domElement.removeEventListener('webglcontextrestored', onContextRestored);
      disc.traverse((object) => { if (object instanceof THREE.Mesh) object.geometry.dispose(); });
      gold.dispose();
      faceMaterial.dispose();
      texture.dispose();
      environment.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [progress, reduced]);

  return (
    <div className={styles.canvas} data-ready={ready} ref={mountRef} role="img" aria-label="Three-dimensional golden Voyager record with an engraved face and polished metal edge">
      <Image alt="" aria-hidden className={styles.fallback} fill sizes="(max-width: 900px) 85vw, 540px" src="/images/nomos-golden-record-disc.png" />
    </div>
  );
}
