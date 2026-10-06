"use client";

import { Globe2, Map as MapIcon } from "lucide-react";
import { useMemo, useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Graticule,
  Marker,
  Sphere,
  ZoomableGroup
} from "react-simple-maps";
import world from "world-atlas/countries-110m.json";

import { GroundNetworkGlobe } from "@/components/network/GroundNetworkGlobe";
import type { ContactWindow, GroundStation } from "@/lib/types";

type RegistryMode = "api" | "reference";
type AtlasView = "globe" | "map";

function hasValidCoordinates(station: GroundStation) {
  return (
    Number.isFinite(station.latitude) &&
    Number.isFinite(station.longitude) &&
    station.latitude >= -90 &&
    station.latitude <= 90 &&
    station.longitude >= -180 &&
    station.longitude <= 180
  );
}

/** Ground-network atlas with synchronized globe, map, registry, and provenance. */
export function NetworkGlobeMap({
  stations,
  registryMode,
  contactWindows
}: {
  stations: GroundStation[];
  registryMode: RegistryMode;
  contactWindows: ContactWindow[];
}) {
  const plottedStations = useMemo(() => stations.filter(hasValidCoordinates), [stations]);
  const providers = useMemo(
    () => ["All", ...Array.from(new Set(plottedStations.map((station) => station.provider)))],
    [plottedStations]
  );
  const [view, setView] = useState<AtlasView>("globe");
  const [provider, setProvider] = useState("All");
  const [selectedId, setSelectedId] = useState(plottedStations[0]?.id ?? "");
  const [mapPosition, setMapPosition] = useState({
    coordinates: [8, 8] as [number, number],
    zoom: 1
  });

  const visibleStations =
    provider === "All"
      ? plottedStations
      : plottedStations.filter((station) => station.provider === provider);
  const selectedStation =
    visibleStations.find((station) => station.id === selectedId) ?? visibleStations[0];
  const stationWindowCount = selectedStation
    ? contactWindows.filter((window) => window.ground_station_id === selectedStation.id).length
    : 0;

  const selectProvider = (nextProvider: string) => {
    const nextStations =
      nextProvider === "All"
        ? plottedStations
        : plottedStations.filter((station) => station.provider === nextProvider);
    setProvider(nextProvider);
    setSelectedId(nextStations[0]?.id ?? "");
  };

  const selectStation = (stationId: string) => {
    const station = visibleStations.find((candidate) => candidate.id === stationId);
    setSelectedId(stationId);
    if (station && view === "map") {
      setMapPosition({ coordinates: [station.longitude, station.latitude], zoom: 2.15 });
    }
  };

  return (
    <section className="ground-atlas" aria-labelledby="ground-atlas-title">
      <header className="ground-atlas__header page-shell">
        <div>
          <p className="chart-label text-gold">Ground network atlas</p>
          <h2 id="ground-atlas-title">Inspect the ground layer.</h2>
        </div>
        <p>
          Six public reference locations used in Nomos geometry calculations. Select a
          provider or station to inspect what is sourced, calculated, and unavailable.
        </p>
      </header>

      <div className="ground-atlas__toolbar page-shell">
        <div className="ground-atlas__view-toggle" aria-label="Atlas view" role="group">
          <button
            aria-pressed={view === "globe"}
            className={view === "globe" ? "is-active" : ""}
            onClick={() => setView("globe")}
            type="button"
          >
            <Globe2 aria-hidden size={15} /> Globe
          </button>
          <button
            aria-pressed={view === "map"}
            className={view === "map" ? "is-active" : ""}
            onClick={() => setView("map")}
            type="button"
          >
            <MapIcon aria-hidden size={15} /> Map
          </button>
        </div>
        <div className="ground-atlas__provider-filter" aria-label="Filter by provider" role="group">
          {providers.map((item) => (
            <button
              aria-pressed={provider === item}
              className={provider === item ? "is-active" : ""}
              key={item}
              onClick={() => selectProvider(item)}
              type="button"
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <div className="ground-atlas__workspace page-shell">
        <div className={`ground-atlas__viewport ground-atlas__viewport--${view}`}>
          <div className="ground-atlas__viewport-meta">
            <span>{view === "globe" ? "3D NETWORK VIEW" : "EQUAL EARTH PROJECTION"}</span>
            <span>{visibleStations.length} SOURCED LOCATIONS</span>
            <span>{registryMode === "api" ? "API CONNECTED" : "PINNED PUBLIC SNAPSHOT"}</span>
          </div>

          {view === "globe" ? (
            <GroundNetworkGlobe
              onSelect={selectStation}
              selectedId={selectedStation?.id ?? ""}
              stations={visibleStations}
            />
          ) : (
            <div className="ground-flat-map">
              <ComposableMap
                aria-label={`Map of ${visibleStations.length} sourced ground-station locations`}
                height={600}
                projection="geoEqualEarth"
                projectionConfig={{ center: [0, 0], scale: 190 }}
                role="img"
                width={1000}
              >
                <Sphere fill="#001045" id="ground-atlas-sphere" stroke="rgba(227, 192, 92, 0.24)" strokeWidth={0.8} />
                <Graticule stroke="rgba(227, 192, 92, 0.1)" strokeWidth={0.55} />
                <ZoomableGroup
                  center={mapPosition.coordinates}
                  maxZoom={4}
                  minZoom={1}
                  onMoveEnd={({ coordinates, zoom }) =>
                    setMapPosition({ coordinates: coordinates as [number, number], zoom })
                  }
                  zoom={mapPosition.zoom}
                >
                  <Geographies geography={world}>
                    {({ geographies }) =>
                      geographies.map((geography) => (
                        <Geography
                          fill="#123da5"
                          geography={geography}
                          key={geography.rsmKey}
                          stroke="rgba(232, 226, 212, 0.3)"
                          strokeWidth={0.5}
                          tabIndex={-1}
                          style={{
                            default: { outline: "none" },
                            hover: { fill: "#1b4cc4", outline: "none" },
                            pressed: { fill: "#1b4cc4", outline: "none" }
                          }}
                        />
                      ))
                    }
                  </Geographies>
                  {visibleStations.map((station, index) => {
                    const active = station.id === selectedStation?.id;
                    return (
                      <Marker
                        coordinates={[station.longitude, station.latitude]}
                        key={station.id}
                        onClick={() => selectStation(station.id)}
                        style={{
                          default: { cursor: "pointer" },
                          hover: { cursor: "pointer" },
                          pressed: { cursor: "pointer" }
                        }}
                      >
                        <title>{station.name}</title>
                        <circle fill={active ? "#f4efe6" : "#e3c05c"} r={active ? 9 : 6.5} stroke="#001045" strokeWidth={2} />
                        <text
                          dominantBaseline="central"
                          fill="#001045"
                          fontFamily="ui-monospace, monospace"
                          fontSize={6.5}
                          fontWeight={700}
                          textAnchor="middle"
                        >
                          {String(index + 1).padStart(2, "0")}
                        </text>
                      </Marker>
                    );
                  })}
                </ZoomableGroup>
              </ComposableMap>
            </div>
          )}

          <p className="ground-atlas__interaction-note">
            {view === "globe"
              ? "SELECT A GOLD STATION MARKER TO INSPECT ITS SOURCE RECORD"
              : "SELECT A MARKER OR REGISTRY ROW TO INSPECT ITS SOURCE RECORD"}
          </p>
        </div>

        <aside className="ground-atlas__inspector" aria-label="Selected ground station">
          {selectedStation ? (
            <>
              <div className="ground-atlas__station-heading">
                <p className="chart-label text-gold">Selected station</p>
                <h3>{selectedStation.name}</h3>
                <p>{selectedStation.location}</p>
              </div>
              <dl className="ground-atlas__facts">
                <div>
                  <dt>Provider</dt>
                  <dd>{selectedStation.provider}</dd>
                </div>
                <div>
                  <dt>Coordinates</dt>
                  <dd>{selectedStation.latitude.toFixed(4)}° · {selectedStation.longitude.toFixed(4)}°</dd>
                </div>
                <div>
                  <dt>Coordinate truth</dt>
                  <dd><span className="ground-atlas__truth-dot" /> OBSERVED</dd>
                </div>
                <div>
                  <dt>Calculated windows loaded</dt>
                  <dd>{stationWindowCount ? `${stationWindowCount} CALCULATED` : "UNAVAILABLE"}</dd>
                </div>
                <div>
                  <dt>Booking / operational access</dt>
                  <dd>UNAVAILABLE</dd>
                </div>
              </dl>
              <div className="ground-atlas__station-list">
                {visibleStations.map((station, index) => (
                  <button
                    aria-pressed={station.id === selectedStation.id}
                    className={station.id === selectedStation.id ? "is-active" : ""}
                    key={station.id}
                    onClick={() => selectStation(station.id)}
                    type="button"
                  >
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <strong>{station.name}</strong>
                    <small>{station.provider}</small>
                  </button>
                ))}
              </div>
            </>
          ) : null}
        </aside>
      </div>
    </section>
  );
}
