"use client";

import { Pause, Play } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import styles from "./OrbitalField.module.css";

type Ripple = { x: number; y: number; start: number };

/** Decorative glyph topography, never telemetry. Events belong to the host so links and touch scrolling keep working. */
export function OrbitalField({ variant = "hero" }: { variant?: "hero" | "footer" }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const clockRef = useRef(0);
  const [paused, setPaused] = useState(false);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const host = canvas?.parentElement?.parentElement;
    const ctx = canvas?.getContext("2d", { alpha: true });
    if (!canvas || !host || !ctx) return;
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    let reduceMotion = media.matches;
    setReduced(reduceMotion);
    let width = 1;
    let height = 1;
    let visible = false;
    let raf = 0;
    let clock = clockRef.current;
    let lastFrame = 0;
    let lastPaint = 0;
    const pointer = { x: -1000, y: -1000, strength: 0 };
    const target = { x: -1000, y: -1000, strength: 0 };
    let ripples: Ripple[] = [];
    const glyphs = ["·", ":", "+", "/", "∶", "N", "—"];
    const active = () => !paused && !reduceMotion && visible && document.visibilityState === "visible";

    let fontFamily = "monospace";
    const paint = () => {
      ctx.clearRect(0, 0, width, height);
      const spacing = width < 600 ? 20 : 18;
      const cols = Math.ceil(width / spacing) + 2;
      const rows = Math.ceil(height / spacing) + 6;
      const time = reduceMotion ? 0 : clock;
      const radius = width < 600 ? 130 : 220;
      if (pointer.strength > 0.01) {
        const glow = ctx.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, radius);
        glow.addColorStop(0, `rgba(219,175,77,${pointer.strength * 0.16})`);
        glow.addColorStop(1, "rgba(219,175,77,0)");
        ctx.fillStyle = glow;
        ctx.fillRect(0, 0, width, height);
      }
      ctx.font = `11px ${fontFamily}`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      for (let row = -3; row < rows; row++) {
        for (let col = -1; col < cols; col++) {
          const x = col * spacing;
          const y = row * spacing;
          const nx = x / width;
          const ny = y / height;
          // Two interfering waves form an inclined, rolling orbital surface.
          const wave = Math.sin(nx * 8 + ny * 5 - time * 0.24);
          const cross = Math.cos(nx * 4 - ny * 7 + time * 0.18);
          const ridge = Math.pow((wave + 1) / 2, 3);
          const distance = Math.hypot(x - pointer.x, y - pointer.y);
          const influence = Math.exp(-Math.pow(distance / radius, 2) * 2) * pointer.strength;
          let impulse = 0;
          for (const ripple of ripples) {
            const age = clock - ripple.start;
            const d = Math.hypot(x - ripple.x, y - ripple.y);
            impulse += Math.exp(-Math.pow((d - age * 210) / 48, 2)) * Math.max(0, 1 - age / 2.4);
          }
          const displacement = (ridge * 26 + cross * 9) + influence * 38 + impulse * 32;
          const rightBias = variant === "hero" ? 0.1 + Math.min(1, nx * 1.8) * 0.9 : 0.4 + nx * 0.6;
          const intensity = Math.min(1, 0.18 + ridge * 0.68 + influence * 0.8 + impulse * 0.85);
          ctx.globalAlpha = intensity * rightBias;
          ctx.fillStyle = influence + impulse > 0.25 ? "#f5dc90" : ridge > 0.52 ? "#d6b66a" : "#608fed";
          const glyph = glyphs[Math.abs(Math.floor((wave + cross) * 2 + col * 0.07 + row * 0.09)) % glyphs.length];
          ctx.fillText(glyph, x + cross * 7 + influence * (x - pointer.x) * 0.26, y + displacement);
        }
      }
      ctx.globalAlpha = 1;
      // Thin orbit contours echo the glyph surface and make its depth readable.
      for (let line = 0; line < 3; line++) {
        ctx.beginPath();
        for (let x = 0; x <= width; x += 12) {
          const y = height * (0.28 + line * 0.21) + Math.sin(x / width * 6 + time * 0.14 + line) * height * 0.12;
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = line === 1 ? "rgba(227,192,92,0.16)" : "rgba(108,151,240,0.12)";
        ctx.lineWidth = 0.65;
        ctx.stroke();
      }
    };
    const frame = (now: number) => {
      raf = 0;
      if (!active()) return;
      if (now - lastPaint >= 32) {
        const delta = Math.min((now - lastFrame) / 1000 || 0.033, 0.06);
        lastFrame = now;
        lastPaint = now;
        clock += delta;
        clockRef.current = clock;
        const ease = 1 - Math.exp(-delta * 10);
        pointer.x += (target.x - pointer.x) * ease;
        pointer.y += (target.y - pointer.y) * ease;
        pointer.strength += (target.strength - pointer.strength) * ease;
        ripples = ripples.filter(ripple => clock - ripple.start < 2.4);
        paint();
      }
      raf = requestAnimationFrame(frame);
    };
    const resume = () => {
      if (active() && !raf) { lastFrame = performance.now(); raf = requestAnimationFrame(frame); }
    };
    const stop = () => { cancelAnimationFrame(raf); raf = 0; };
    const resize = new ResizeObserver(() => {
      fontFamily = getComputedStyle(canvas).fontFamily;
      const rect = host.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      const dpr = Math.min(devicePixelRatio, 1.5);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      paint();
      resume();
    });
    resize.observe(host);
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) resume(); else stop();
    });
    observer.observe(host);
    const move = (event: PointerEvent) => {
      if (!active()) return;
      const rect = host.getBoundingClientRect();
      target.x = event.clientX - rect.left;
      target.y = event.clientY - rect.top;
      target.strength = 1;
      if (pointer.x === -1000) { pointer.x = target.x; pointer.y = target.y; }
    };
    const leave = () => { target.strength = 0; };
    const impulse = (event: PointerEvent) => {
      if (!active() || (event.target as Element).closest("button, a, input")) return;
      move(event);
      ripples = [...ripples.slice(-3), { x: target.x, y: target.y, start: clock }];
    };
    const visibility = () => { if (active()) resume(); else stop(); };
    const preference = () => {
      reduceMotion = media.matches;
      setReduced(reduceMotion);
      if (reduceMotion) { stop(); pointer.strength = 0; ripples = []; paint(); } else resume();
    };
    host.addEventListener("pointermove", move, { passive: true });
    host.addEventListener("pointerdown", impulse, { passive: true });
    host.addEventListener("pointerleave", leave);
    host.addEventListener("pointerup", leave);
    host.addEventListener("pointercancel", leave);
    media.addEventListener("change", preference);
    document.addEventListener("visibilitychange", visibility);
    return () => {
      stop();
      resize.disconnect();
      observer.disconnect();
      host.removeEventListener("pointermove", move);
      host.removeEventListener("pointerdown", impulse);
      host.removeEventListener("pointerleave", leave);
      host.removeEventListener("pointerup", leave);
      host.removeEventListener("pointercancel", leave);
      media.removeEventListener("change", preference);
      document.removeEventListener("visibilitychange", visibility);
    };
  }, [paused, variant]);

  return (
    <div className={`${styles.field} ${styles[variant]}`} data-orbital-field={variant}>
      <canvas aria-hidden ref={canvasRef} />
      {!reduced ? (
        <button className={styles.toggle} type="button" aria-label={paused ? "Resume background animation" : "Pause background animation"} aria-pressed={paused} onClick={() => setPaused(value => !value)}>
          {paused ? <Play size={12} aria-hidden /> : <Pause size={12} aria-hidden />}
          <span>{paused ? "Motion paused" : "Pause motion"}</span>
        </button>
      ) : null}
    </div>
  );
}
