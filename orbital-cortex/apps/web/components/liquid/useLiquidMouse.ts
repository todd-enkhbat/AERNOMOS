"use client";

import { useCallback, useRef } from "react";

export function useLiquidMouse<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);

  const onMouseMove = useCallback((event: React.MouseEvent<T>) => {
    const el = event.currentTarget;
    const rect = el.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    el.style.setProperty("--x", `${x}%`);
    el.style.setProperty("--y", `${y}%`);
  }, []);

  const onMouseLeave = useCallback((event: React.MouseEvent<T>) => {
    event.currentTarget.style.setProperty("--x", "50%");
    event.currentTarget.style.setProperty("--y", "35%");
  }, []);

  return { ref, onMouseMove, onMouseLeave };
}
