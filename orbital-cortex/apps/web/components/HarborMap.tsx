"use client";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef } from "react";

import type { GeoJsonFeature } from "@/lib/types";

type HarborMapProps = {
  features: GeoJsonFeature[];
  selectedId?: string | null;
  darkShipsOnly?: boolean;
  onSelect?: (feature: GeoJsonFeature) => void;
};

const HARBOR_BOUNDS: [[number, number], [number, number]] = [
  [-74.3, 40.3],
  [-73.5, 41.0]
];

export function HarborMap({
  features,
  selectedId,
  darkShipsOnly = false,
  onSelect
}: HarborMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  const visibleFeatures = darkShipsOnly
    ? features.filter((feature) => feature.properties.dark_ship === true)
    : features;

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors"
          }
        },
        layers: [
          {
            id: "osm",
            type: "raster",
            source: "osm"
          }
        ]
      },
      bounds: HARBOR_BOUNDS,
      fitBoundsOptions: { padding: 24 }
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const sourceId = "detections";
    const layerId = "detection-points";

    const geojson = {
      type: "FeatureCollection" as const,
      features: visibleFeatures
    };

    const paintLayer = () => {
      if (!map.getSource(sourceId)) {
        map.addSource(sourceId, { type: "geojson", data: geojson });
        map.addLayer({
          id: layerId,
          type: "circle",
          source: sourceId,
          paint: {
            "circle-radius": [
              "case",
              ["==", ["get", "detection_id"], selectedId ?? ""],
              10,
              7
            ],
            "circle-color": [
              "case",
              ["==", ["get", "dark_ship"], true],
              "#e0b16f",
              "#25495a"
            ],
            "circle-stroke-color": "#fffaf0",
            "circle-stroke-width": 2
          }
        });
        map.on("click", layerId, (event) => {
          const feature = event.features?.[0];
          if (feature && onSelect) {
            onSelect(feature as unknown as GeoJsonFeature);
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
    };

    if (map.isStyleLoaded()) {
      paintLayer();
    } else {
      map.once("load", paintLayer);
    }
  }, [visibleFeatures, selectedId, onSelect]);

  return (
    <div
      className="min-h-[380px] overflow-hidden rounded-lg border border-[rgba(86,67,42,0.22)]"
      ref={containerRef}
    />
  );
}
