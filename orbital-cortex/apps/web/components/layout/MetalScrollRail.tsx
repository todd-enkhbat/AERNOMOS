"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Apple-like right-edge scroll control: brushed parchment rail + golden thumb.
 * Native macOS/Electron overlay scrollbars ignore most webkit styling, so we
 * hide them and drive a thin metal rail from document scroll.
 */
export function MetalScrollRail() {
  const trackRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const thumbH = useRef(48);
  const [metrics, setMetrics] = useState({
    visible: false,
    thumbTop: 0,
    thumbHeight: 48
  });

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const update = () => {
      const scrollEl = document.documentElement;
      const scrollHeight = scrollEl.scrollHeight;
      const clientHeight = window.innerHeight;
      const maxScroll = Math.max(0, scrollHeight - clientHeight);
      const trackHeight = track.clientHeight;
      const visible = maxScroll > 8 && trackHeight > 32;
      if (!visible) {
        setMetrics((m) => (m.visible ? { ...m, visible: false } : m));
        return;
      }
      const nextThumb = Math.max(
        40,
        Math.round((clientHeight / scrollHeight) * trackHeight)
      );
      thumbH.current = nextThumb;
      const travel = Math.max(1, trackHeight - nextThumb);
      const thumbTop = Math.round((window.scrollY / maxScroll) * travel);
      setMetrics({ visible: true, thumbTop, thumbHeight: nextThumb });
    };

    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    const ro = new ResizeObserver(update);
    ro.observe(document.body);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
      ro.disconnect();
    };
  }, []);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const scrollFromClientY = (clientY: number) => {
      const rect = track.getBoundingClientRect();
      const travel = Math.max(1, rect.height - thumbH.current);
      const y = clientY - rect.top - thumbH.current / 2;
      const ratio = Math.min(1, Math.max(0, y / travel));
      const maxScroll = Math.max(
        0,
        document.documentElement.scrollHeight - window.innerHeight
      );
      window.scrollTo({ top: ratio * maxScroll });
    };

    const onPointerMove = (e: PointerEvent) => {
      if (!dragging.current) return;
      e.preventDefault();
      scrollFromClientY(e.clientY);
    };
    const onPointerUp = () => {
      dragging.current = false;
      document.body.classList.remove("is-scroll-rail-dragging");
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointercancel", onPointerUp);
    return () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerUp);
    };
  }, []);

  return (
    <div
      aria-hidden
      className={`metal-scroll-rail${metrics.visible ? " is-visible" : ""}`}
    >
      <div
        className="metal-scroll-rail__track"
        ref={trackRef}
        onPointerDown={(e) => {
          if (e.button !== 0) return;
          dragging.current = true;
          document.body.classList.add("is-scroll-rail-dragging");
          const rect = trackRef.current?.getBoundingClientRect();
          if (!rect) return;
          const travel = Math.max(1, rect.height - thumbH.current);
          const y = e.clientY - rect.top - thumbH.current / 2;
          const ratio = Math.min(1, Math.max(0, y / travel));
          const maxScroll = Math.max(
            0,
            document.documentElement.scrollHeight - window.innerHeight
          );
          window.scrollTo({ top: ratio * maxScroll });
          e.currentTarget.setPointerCapture(e.pointerId);
        }}
      >
        <div
          className="metal-scroll-rail__thumb"
          style={{
            height: metrics.thumbHeight,
            transform: `translateY(${metrics.thumbTop}px)`
          }}
        />
      </div>
    </div>
  );
}
