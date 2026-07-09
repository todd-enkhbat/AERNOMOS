"use client";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef } from "react";

import type { GroundStation } from "@/lib/types";

/** World map with live ground-station pins from the Nomos API registry. */
export function NetworkGlobeMap({ stations }: { stations: GroundStation[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          carto: {
            type: "raster",
            tiles: [
              "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
              "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
            ],
            tileSize: 256,
            attribution: "© OpenStreetMap © CARTO"
          }
        },
        layers: [{ id: "carto", type: "raster", source: "carto" }]
      },
      center: [10, 30],
      zoom: 1.4,
      pitch: 0,
      bearing: 0,
      interactive: true,
      attributionControl: false
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
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

    const addLayers = () => {
      const geojson: GeoJSON.FeatureCollection = {
        type: "FeatureCollection",
        features: stations
          .filter((s) => s.latitude != null && s.longitude != null)
          .map((s) => ({
            type: "Feature",
            geometry: {
              type: "Point",
              coordinates: [s.longitude!, s.latitude!]
            },
            properties: { name: s.name, id: s.id }
          }))
      };

      if (map.getSource("stations")) {
        (map.getSource("stations") as maplibregl.GeoJSONSource).setData(geojson);
        return;
      }

      map.addSource("stations", { type: "geojson", data: geojson });
      map.addLayer({
        id: "station-glow",
        type: "circle",
        source: "stations",
        paint: {
          "circle-radius": 14,
          "circle-color": "#e3c05c",
          "circle-opacity": 0.18,
          "circle-blur": 0.6
        }
      });
      map.addLayer({
        id: "station-dot",
        type: "circle",
        source: "stations",
        paint: {
          "circle-radius": 5,
          "circle-color": "#e3c05c",
          "circle-stroke-width": 1.5,
          "circle-stroke-color": "#f4efe6"
        }
      });
    };

    if (map.isStyleLoaded()) {
      addLayers();
    } else {
      map.on("load", addLayers);
    }
  }, [stations]);

  return (
    <div
      className="h-full min-h-[280px] w-full overflow-hidden rounded-[20px]"
      ref={containerRef}
    />
  );
}
