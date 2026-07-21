"use client";

import { useCallback, useRef } from "react";

/**
 * Pointer specular for liquid glass. Writes --x/--y only onto a dedicated
 * `[data-liquid-specular]` child when present, so parent style recalc stays narrow.
 * Falls back to the host element if no specular layer exists.
 */
export function useLiquidMouse<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  const rafRef = useRef<number | null>(null);
  const pendingRef = useRef<{ x: number; y: number } | null>(null);

  const targetFor = useCallback((host: HTMLElement): HTMLElement => {
    const specular = host.querySelector<HTMLElement>("[data-liquid-specular]");
    return specular ?? host;
  }, []);

  const flush = useCallback(
    (host: HTMLElement) => {
      rafRef.current = null;
      const pending = pendingRef.current;
      if (!pending) return;
      pendingRef.current = null;
      const target = targetFor(host);
      target.style.setProperty("--x", `${pending.x}%`);
      target.style.setProperty("--y", `${pending.y}%`);
    },
    [targetFor]
  );

  const onMouseMove = useCallback(
    (event: React.MouseEvent<T>) => {
      const el = event.currentTarget;
      const rect = el.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      pendingRef.current = { x, y };
      if (rafRef.current == null) {
        rafRef.current = window.requestAnimationFrame(() => flush(el));
      }
    },
    [flush]
  );

  const onMouseLeave = useCallback(
    (event: React.MouseEvent<T>) => {
      const el = event.currentTarget;
      if (rafRef.current != null) {
        window.cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      pendingRef.current = null;
      const target = targetFor(el);
      target.style.setProperty("--x", "50%");
      target.style.setProperty("--y", "35%");
    },
    [targetFor]
  );

  return { ref, onMouseMove, onMouseLeave };
}
