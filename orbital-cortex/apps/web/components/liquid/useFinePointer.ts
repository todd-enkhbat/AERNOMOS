"use client";

import { useEffect, useState } from "react";

const QUERY = "(hover: hover) and (pointer: fine)";

export function useFinePointer() {
  // Fixed SSR-safe default so the client's first (pre-hydration) render
  // matches the server regardless of the visitor's actual pointer type.
  // The real value applies a tick after mount, once hydration is done.
  const [finePointer, setFinePointer] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(QUERY);
    const update = () => setFinePointer(media.matches);

    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return finePointer;
}
