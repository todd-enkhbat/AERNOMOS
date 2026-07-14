"use client";

import { useReducedMotion } from "framer-motion";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Crosshair, Minus, Plus, Radar, Ship, Sparkles } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { LiquidChip } from "@/components/liquid/LiquidChip";
import type { GeoJsonFeature } from "@/lib/types";

export type HarborFilter = "all" | "dark";
export type HarborMode = "explore" | "cinema";

type HarborMapProps = {
  features: GeoJsonFeature[];
  selectedId?: string | null;
  darkShipsOnly?: boolean;
  filter?: HarborFilter;
  onFilterChange?: (filter: HarborFilter) => void;
  onSelect?: (feature: GeoJsonFeature) => void;
  title?: string;
  subtitle?: string;
  compact?: boolean;
};

const HARBOR_BOUNDS: [[number, number], [number, number]] = [
  [-74.3, 40.3],
  [-73.5, 41.0]
];

const DARK_STYLE = {
  version: 8 as const,
  sources: {
    carto: {
      type: "raster" as const,
      tiles: [
        "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        "https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
      ],
      tileSize: 256
    }
  },
  layers: [{ id: "carto", type: "raster" as const, source: "carto" }]
};

export function HarborMap({
  features,
  selectedId,
  darkShipsOnly = false,
  filter,
  onFilterChange,
  onSelect,
  title,
  subtitle,
  compact = false
}: HarborMapProps) {
  const shellRef = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const pulseRef = useRef(0);
  const onSelectRef = useRef(onSelect);
  const reduced = useReducedMotion();

  const [internalFilter, setInternalFilter] = useState<HarborFilter>(
    darkShipsOnly ? "dark" : "all"
  );
  const [livePulse, setLivePulse] = useState(true);
  const [mode, setMode] = useState<HarborMode>("explore");
  const [mapReady, setMapReady] = useState(false);
  const [mapInView, setMapInView] = useState(true);
  const [pageVisible, setPageVisible] = useState(true);

  const activeFilter = filter ?? internalFilter;

  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    const shell = shellRef.current;
    if (!shell) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => setMapInView(entry.isIntersecting),
      { rootMargin: "120px" }
    );
    const onVisibilityChange = () => setPageVisible(document.visibilityState === "visible");

    observer.observe(shell);
    onVisibilityChange();
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () => {
      observer.disconnect();
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, []);

  const setFilter = (next: HarborFilter) => {
    if (onFilterChange) {
      onFilterChange(next);
    } else {
      setInternalFilter(next);
    }
  };

  const visibleFeatures = useMemo(
    () =>
      activeFilter === "dark"
        ? features.filter((feature) => feature.properties.dark_ship === true)
        : features,
    [activeFilter, features]
  );

  useEffect(() => {
    const container = containerRef.current;
    const shell = shellRef.current;
    if (!container || !shell || mapRef.current) {
      return;
    }

    let cancelled = false;
    let raf = 0;
    let map: maplibregl.Map | null = null;
    let observer: ResizeObserver | null = null;
    let resize: (() => void) | null = null;

    const start = () => {
      if (cancelled || mapRef.current) {
        return;
      }
      if (shell.clientWidth < 8 || shell.clientHeight < 8) {
        raf = requestAnimationFrame(start);
        return;
      }

      map = new maplibregl.Map({
        container,
        style: DARK_STYLE,
        center: [-73.9, 40.65],
        zoom: 9,
        attributionControl: false,
        dragRotate: false,
        pitchWithRotate: false
      });

      mapRef.current = map;

      resize = () => {
        map?.resize();
      };

      const onReady = () => {
        map?.fitBounds(HARBOR_BOUNDS, { padding: 28, maxZoom: 10 });
        resize?.();
        setMapReady(true);
      };

      resize();
      observer = new ResizeObserver(resize);
      observer.observe(shell);
      window.addEventListener("resize", resize);

      if (map.isStyleLoaded()) {
        onReady();
      } else {
        map.once("load", onReady);
      }

      map.on("error", (event) => {
        console.error("HarborMap:", event.error);
      });
    };

    start();

    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      observer?.disconnect();
      if (resize) {
        window.removeEventListener("resize", resize);
      }
      setMapReady(false);
      map?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapReady) {
      return;
    }

    if (mode === "explore") {
      map.scrollZoom.enable();
      map.dragPan.enable();
      map.doubleClickZoom.enable();
    } else {
      map.scrollZoom.disable();
      map.dragPan.disable();
      map.doubleClickZoom.disable();
    }
  }, [mode, mapReady]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapReady) {
      return;
    }

    const sourceId = "detections";
    const layerId = "detection-points";
    const pulseId = "detection-pulse";

    const geojson: GeoJSON.FeatureCollection = {
      type: "FeatureCollection",
      features: visibleFeatures
    };

    const paintLayers = () => {
      if (!map.isStyleLoaded()) {
        return;
      }

      if (!map.getSource(sourceId)) {
        map.addSource(sourceId, { type: "geojson", data: geojson });
        map.addLayer({
          id: pulseId,
          type: "circle",
          source: sourceId,
          paint: {
            "circle-radius": 16,
            "circle-color": "#e3c05c",
            "circle-opacity": 0.12,
            "circle-blur": 0.55
          }
        });
        map.addLayer({
          id: layerId,
          type: "circle",
          source: sourceId,
          paint: {
            "circle-radius": [
              "case",
              ["==", ["to-string", ["get", "detection_id"]], selectedId ?? ""],
              9,
              6
            ],
            "circle-color": [
              "case",
              ["==", ["get", "dark_ship"], true],
              "#e3c05c",
              "#8eb4c9"
            ],
            "circle-stroke-color": "#f4efe6",
            "circle-stroke-width": 1.5,
            "circle-opacity": 0.95
          }
        });

        map.on("click", layerId, (event) => {
          const feature = event.features?.[0];
          if (feature && onSelectRef.current) {
            onSelectRef.current(feature as unknown as GeoJsonFeature);
          }
        });
        map.on("mouseenter", layerId, () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", layerId, () => {
          map.getCanvas().style.cursor = "";
        });
      } else {
        (map.getSource(sourceId) as maplibregl.GeoJSONSource).setData(geojson);
      }

      if (map.getLayer(layerId)) {
        map.setPaintProperty(layerId, "circle-radius", [
          "case",
          ["==", ["to-string", ["get", "detection_id"]], selectedId ?? ""],
          9,
          6
        ]);
      }
    };

    paintLayers();
    map.on("load", paintLayers);
    map.on("styledata", paintLayers);

    return () => {
      map.off("load", paintLayers);
      map.off("styledata", paintLayers);
    };
  }, [visibleFeatures, selectedId, mapReady]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapReady || !livePulse || reduced || !mapInView || !pageVisible) {
      return;
    }

    let raf = 0;
    const tick = () => {
      pulseRef.current += 0.045;
      const pulse = 14 + Math.sin(pulseRef.current) * 5;
      const opacity = 0.08 + (Math.sin(pulseRef.current) + 1) * 0.06;
      if (map.getLayer("detection-pulse")) {
        map.setPaintProperty("detection-pulse", "circle-radius", pulse);
        map.setPaintProperty("detection-pulse", "circle-opacity", opacity);
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [livePulse, visibleFeatures, mapReady, reduced, mapInView, pageVisible]);

  const zoomBy = (delta: number) => {
    const map = mapRef.current;
    if (!map) {
      return;
    }
    map.zoomTo(map.getZoom() + delta, { duration: 280 });
  };

  const resetView = () => {
    mapRef.current?.fitBounds(HARBOR_BOUNDS, { padding: 28, duration: 450, maxZoom: 10 });
  };

  const heightClass = compact ? "h-[280px]" : "h-[360px]";

  return (
    <div
      className={[
        "harbor-map relative w-full overflow-hidden rounded-[16px] border border-gold/12 bg-[#0a0c10]",
        heightClass
      ].join(" ")}
      ref={shellRef}
    >
      <div className="absolute inset-0 z-0" ref={containerRef} />

      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-[1] bg-[radial-gradient(ellipse_at_center,transparent_82%,rgba(5,5,6,0.15)_100%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 z-[3] h-px bg-gradient-to-r from-transparent via-gold/35 to-transparent"
      />

      <div className="absolute inset-x-3 top-3 z-[2] flex flex-wrap items-start justify-between gap-2 md:inset-x-4 md:top-4">
        <div className="pointer-events-none min-w-0">
          {title ? <p className="text-sm font-medium text-cream">{title}</p> : null}
          {subtitle ? (
            <p className="metric-value mt-0.5 text-[10px] text-muted">{subtitle}</p>
          ) : null}
        </div>
        <div className="flex max-w-full flex-wrap justify-end gap-1.5">
          <LiquidChip active={activeFilter === "all"} onClick={() => setFilter("all")}>
            <span className="inline-flex items-center gap-1.5">
              <Ship size={12} strokeWidth={1.8} />
              All vessels
            </span>
          </LiquidChip>
          <LiquidChip active={activeFilter === "dark"} onClick={() => setFilter("dark")}>
            <span className="inline-flex items-center gap-1.5">
              <Radar size={12} strokeWidth={1.8} />
              Dark ships
            </span>
          </LiquidChip>
          <LiquidChip
            active={livePulse && !reduced}
            onClick={() => setLivePulse((value) => !value)}
          >
            <span className="inline-flex items-center gap-1.5">
              <Sparkles size={12} strokeWidth={1.8} />
              Highlight pulse
            </span>
          </LiquidChip>
          <LiquidChip
            active={mode === "cinema"}
            onClick={() => setMode((m) => (m === "explore" ? "cinema" : "explore"))}
          >
            <span className="inline-flex items-center gap-1.5">
              <Crosshair size={12} strokeWidth={1.8} />
              {mode === "explore" ? "Cinema" : "Explore"}
            </span>
          </LiquidChip>
        </div>
      </div>

      <div className="absolute bottom-3 right-3 z-[2] flex flex-col gap-1.5">
        <button
          aria-label="Zoom in"
          className="liquid-glass liquid-glass--chip grid h-8 w-8 place-items-center text-cream"
          onClick={() => zoomBy(0.65)}
          type="button"
        >
          <Plus size={14} strokeWidth={1.8} />
        </button>
        <button
          aria-label="Zoom out"
          className="liquid-glass liquid-glass--chip grid h-8 w-8 place-items-center text-cream"
          onClick={() => zoomBy(-0.65)}
          type="button"
        >
          <Minus size={14} strokeWidth={1.8} />
        </button>
        <button
          aria-label="Reset harbor view"
          className="liquid-glass liquid-glass--chip px-2 py-1 text-[10px] text-muted"
          onClick={resetView}
          type="button"
        >
          Reset
        </button>
      </div>

      <p className="chart-label pointer-events-none absolute bottom-2 left-3 z-[2] text-[9px] text-muted-dark/80">
        NY Harbor · demo AOI
      </p>
    </div>
  );
}
