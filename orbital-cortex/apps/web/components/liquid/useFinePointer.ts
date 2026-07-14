"use client";

import { useEffect, useState } from "react";

const QUERY = "(hover: hover) and (pointer: fine)";

function matchesFinePointer() {
  if (typeof window === "undefined") {
    return true;
  }
  return window.matchMedia(QUERY).matches;
}

export function useFinePointer() {
  const [finePointer, setFinePointer] = useState(matchesFinePointer);

  useEffect(() => {
    const media = window.matchMedia(QUERY);
    const update = () => setFinePointer(media.matches);

    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return finePointer;
}
