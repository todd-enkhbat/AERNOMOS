"use client";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef } from "react";

import {
  type AreaOfInterest,
  bboxFromPolygon,
  validateAreaOfInterest
} from "@/lib/mission-builder";

type AoiMapDrawProps = {
  value: AreaOfInterest | null;
  onChange: (area: AreaOfInterest | null, error?: string) => void;
};

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

function featureToAoi(feature: GeoJSON.Feature): AreaOfInterest | null {
  const geometry = feature.geometry;
  if (!geometry) return null;
  if (geometry.type === "Polygon") {
    return validateAreaOfInterest(geometry);
  }
  return null;
}

export function AoiMapDraw({ value, onChange }: AoiMapDrawProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const drawRef = useRef<MapboxDraw | null>(null);
  const onChangeRef = useRef(onChange);
  const syncingRef = useRef(false);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: DARK_STYLE,
      center: [-74.0, 40.7],
      zoom: 8,
      attributionControl: false
    });

    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: {
        polygon: true,
        trash: true
      },
      defaultMode: "draw_polygon"
    });

    // mapbox-gl-draw typings target mapbox-gl; MapLibre is API-compatible here.
    map.addControl(draw as unknown as maplibregl.IControl);
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    const emitFromDraw = () => {
      if (syncingRef.current) return;
      const collection = draw.getAll();
      const feature = collection.features[0];
      if (!feature) {
        onChangeRef.current(null);
        return;
      }
      try {
        const area = featureToAoi(feature);
        onChangeRef.current(area);
      } catch (error) {
        onChangeRef.current(
          null,
          error instanceof Error ? error.message : "Drawn area is invalid"
        );
      }
    };

    map.on("load", () => {
      map.resize();
    });
    map.on("draw.create", emitFromDraw);
    map.on("draw.update", emitFromDraw);
    map.on("draw.delete", emitFromDraw);

    mapRef.current = map;
    drawRef.current = draw;

    return () => {
      map.remove();
      mapRef.current = null;
      drawRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const draw = drawRef.current;
    if (!map || !draw || !value) return;

    syncingRef.current = true;
    try {
      const geometry =
        value.type === "bbox"
          ? {
              type: "Polygon" as const,
              coordinates: [
                [
                  [value.coordinates[0], value.coordinates[1]],
                  [value.coordinates[2], value.coordinates[1]],
                  [value.coordinates[2], value.coordinates[3]],
                  [value.coordinates[0], value.coordinates[3]],
                  [value.coordinates[0], value.coordinates[1]]
                ]
              ]
            }
          : value;

      const existing = draw.getAll();
      const current = JSON.stringify(existing.features[0]?.geometry ?? null);
      const next = JSON.stringify(geometry);
      if (current !== next) {
        draw.deleteAll();
        draw.add({
          type: "Feature",
          properties: {},
          geometry
        });
      }

      const [west, south, east, north] = bboxFromPolygon(value);
      map.fitBounds(
        [
          [west, south],
          [east, north]
        ],
        { padding: 48, maxZoom: 10, duration: 0 }
      );
    } catch {
      // Ignore sync failures from partial edits.
    } finally {
      syncingRef.current = false;
    }
  }, [value]);

  return (
    <div className="aoi-map overflow-hidden rounded-xl border border-white/10">
      <div className="flex flex-wrap items-center gap-2 border-b border-white/10 bg-black/30 px-3 py-2 text-xs text-muted">
        <span>Draw a polygon on the map, or use coordinates / upload below.</span>
        <button
          className="rounded-md border border-white/15 px-2 py-1 text-cream 	ransition-colors hover:border-gold/40"
          onClick={() => drawRef.current?.changeMode("draw_polygon")}
          type="button"
        >
          Draw polygon
        </button>
        <button
          className="rounded-md border border-white/15 px-2 py-1 text-cream 	ransition-colors hover:border-gold/40"
          onClick={() => {
            drawRef.current?.deleteAll();
            onChange(null);
          }}
          type="button"
        >
          Clear
        </button>
      </div>
      <div className="h-[280px] w-full sm:h-[340px]" ref={containerRef} />
    </div>
  );
}
