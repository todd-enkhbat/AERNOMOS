"use client";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useMemo, useRef } from "react";

import { TruthBadge, unwrapProvenance } from "@/components/truth";
import type {
  CatalogCandidate,
  MissionInfrastructureResponse,
  MissionSummary,
} from "@/lib/api";

type Geometry = GeoJSON.Geometry;

function asGeometry(value: Record<string, unknown> | undefined): Geometry | null {
  if (!value) return null;
  if (
    value.type === "bbox" &&
    Array.isArray(value.coordinates) &&
    value.coordinates.length === 4
  ) {
    const [west, south, east, north] = value.coordinates.map(Number);
    if ([west, south, east, north].every(Number.isFinite)) {
      return {
        type: "Polygon",
        coordinates: [
          [
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
          ],
        ],
      };
    }
  }
  if (
    typeof value.type === "string" &&
    "coordinates" in value &&
    Array.isArray(value.coordinates)
  ) {
    return value as unknown as Geometry;
  }
  return null;
}

function coordinatePairs(value: unknown): [number, number][] {
  if (!Array.isArray(value)) return [];
  if (
    value.length >= 2 &&
    typeof value[0] === "number" &&
    typeof value[1] === "number"
  ) {
    return [[value[0], value[1]]];
  }
  return value.flatMap(coordinatePairs);
}

function destinationLabel(mission: MissionSummary): string {
  if (mission.allowed_regions?.length) {
    return mission.allowed_regions.map(String).join(", ");
  }
  const residency = (mission.customer_systems ?? []).find(
    (item) =>
      typeof item === "object" &&
      item !== null &&
      "kind" in item &&
      item.kind === "data_residency"
  );
  if (
    typeof residency === "object" &&
    residency !== null &&
    "requirement" in residency
  ) {
    return String(residency.requirement);
  }
  return mission.preferred_compute_location || "Customer-selected environment";
}

export function MissionGeographyMap({
  mission,
  candidates,
  infrastructure,
}: {
  mission: MissionSummary;
  candidates: CatalogCandidate[];
  infrastructure: MissionInfrastructureResponse | null;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const destination = destinationLabel(mission);

  const geography = useMemo(() => {
    const aoi = asGeometry(mission.area_of_interest);
    const sceneFeatures = candidates.flatMap<GeoJSON.Feature>((candidate) => {
      const geometry = asGeometry(candidate.footprint);
      return geometry
        ? [
            {
              type: "Feature",
              geometry,
              properties: {
                id: candidate.id,
                label: candidate.external_item_id,
              },
            },
          ]
        : [];
    });
    const stationFeatures = (infrastructure?.ground_stations ?? []).flatMap<GeoJSON.Feature>(
      (station) => {
        const longitude = Number(unwrapProvenance(station.longitude));
        const latitude = Number(unwrapProvenance(station.latitude));
        return Number.isFinite(longitude) && Number.isFinite(latitude)
          ? [
              {
                type: "Feature",
                geometry: { type: "Point", coordinates: [longitude, latitude] },
                properties: { id: station.id, label: station.name },
              },
            ]
          : [];
      }
    );
    const allCoordinates = [
      ...(aoi && "coordinates" in aoi ? coordinatePairs(aoi.coordinates) : []),
      ...sceneFeatures.flatMap((feature) =>
        "coordinates" in feature.geometry
          ? coordinatePairs(feature.geometry.coordinates)
          : []
      ),
      ...stationFeatures.flatMap((feature) =>
        "coordinates" in feature.geometry
          ? coordinatePairs(feature.geometry.coordinates)
          : []
      ),
    ];
    return { aoi, sceneFeatures, stationFeatures, allCoordinates };
  }, [candidates, infrastructure, mission.area_of_interest]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          carto: {
            type: "raster",
            tiles: [
              "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
              "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: "© OpenStreetMap © CARTO",
          },
        },
        layers: [{ id: "carto", type: "raster", source: "carto" }],
      },
      center: [0, 20],
      zoom: 1.2,
      attributionControl: false,
    });
    map.addControl(
      new maplibregl.NavigationControl({ showCompass: false }),
      "top-right"
    );
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const updateMap = () => {
      const sources: Array<[string, GeoJSON.FeatureCollection]> = [
        [
          "mission-aoi",
          {
            type: "FeatureCollection",
            features: geography.aoi
              ? [{ type: "Feature", geometry: geography.aoi, properties: {} }]
              : [],
          },
        ],
        [
          "mission-scenes",
          { type: "FeatureCollection", features: geography.sceneFeatures },
        ],
        [
          "mission-stations",
          { type: "FeatureCollection", features: geography.stationFeatures },
        ],
      ];
      sources.forEach(([id, data]) => {
        const source = map.getSource(id) as maplibregl.GeoJSONSource | undefined;
        if (source) source.setData(data);
        else map.addSource(id, { type: "geojson", data });
      });

      if (!map.getLayer("mission-aoi-fill")) {
        map.addLayer({
          id: "mission-aoi-fill",
          type: "fill",
          source: "mission-aoi",
          paint: { "fill-color": "#c9a227", "fill-opacity": 0.12 },
        });
        map.addLayer({
          id: "mission-aoi-line",
          type: "line",
          source: "mission-aoi",
          paint: { "line-color": "#e3c05c", "line-width": 2 },
        });
        map.addLayer({
          id: "mission-scenes-fill",
          type: "fill",
          source: "mission-scenes",
          paint: { "fill-color": "#496a9b", "fill-opacity": 0.18 },
        });
        map.addLayer({
          id: "mission-scenes-line",
          type: "line",
          source: "mission-scenes",
          paint: {
            "line-color": "#9eb6d9",
            "line-width": 1.5,
            "line-dasharray": [3, 2],
          },
        });
        map.addLayer({
          id: "mission-stations-glow",
          type: "circle",
          source: "mission-stations",
          paint: {
            "circle-radius": 11,
            "circle-color": "#a84d35",
            "circle-opacity": 0.2,
            "circle-blur": 0.5,
          },
        });
        map.addLayer({
          id: "mission-stations-dot",
          type: "circle",
          source: "mission-stations",
          paint: {
            "circle-radius": 4,
            "circle-color": "#d48470",
            "circle-stroke-color": "#f4efe6",
            "circle-stroke-width": 1,
          },
        });
      }

      if (geography.allCoordinates.length) {
        const bounds = geography.allCoordinates.reduce(
          (box, coordinate) => box.extend(coordinate),
          new maplibregl.LngLatBounds(
            geography.allCoordinates[0],
            geography.allCoordinates[0]
          )
        );
        map.fitBounds(bounds, {
          padding: 48,
          maxZoom: 8,
          duration: 0,
        });
      }
    };

    if (map.isStyleLoaded()) updateMap();
    else map.once("load", updateMap);
  }, [geography]);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-void/60">
      <div
        aria-label={`Mission map showing the area of interest, ${candidates.length} selected scene footprints, and ${infrastructure?.ground_stations?.length ?? 0} candidate ground stations.`}
        className="h-[420px] w-full sm:h-[500px]"
        ref={containerRef}
        role="img"
      />
      <div className="pointer-events-none absolute inset-x-3 bottom-3 grid gap-2 rounded-xl border border-white/10 bg-void/90 p-3 backdrop-blur-md sm:inset-x-auto sm:left-3 sm:max-w-sm">
        <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-cream">
          <span><i className="mr-2 inline-block h-2 w-4 bg-gold/70" />AOI</span>
          <span><i className="mr-2 inline-block h-2 w-4 bg-cobalt/70" />Selected scene</span>
          <span><i className="mr-2 inline-block h-2 w-2 rounded-full bg-vermilion" />Ground station</span>
        </div>
        <p className="text-xs text-muted">
          Destination: <span className="text-cream">{destination}</span>
        </p>
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
          Satellite track
          <TruthBadge compact status="UNAVAILABLE" />
          <span>No trajectory coordinates are exposed by the current mission API.</span>
        </div>
      </div>
    </div>
  );
}
