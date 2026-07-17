"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useReducer, useState, type ChangeEvent } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import {
  apiErrorMessage,
  createMission,
  ensureAnonymousSession
} from "@/lib/api";
import {
  COMPUTE_LOCATION_OPTIONS,
  MISSION_MODE_OPTIONS,
  OBJECTIVE_LABELS,
  OBJECTIVE_OPTIONS,
  ONBOARD_OPTIONS,
  aoiAreaKm2,
  areaFromBboxFields,
  buildMissionCreatePayload,
  initialMissionBuilderState,
  missionBuilderReducer,
  parseGeoJsonUpload,
  validateAreaOfInterest,
  validateStep,
  type AreaOfInterest,
  type ObjectiveType
} from "@/lib/mission-builder";

const AoiMapDraw = dynamic(
  () => import("@/components/plan/AoiMapDraw").then((m) => m.AoiMapDraw),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[280px] items-center justify-center rounded-xl border border-white/10 bg-black/20 text-sm text-muted sm:h-[340px]">
        Loading map…
      </div>
    )
  }
);

const STEPS = [
  { id: 1, label: "Objective" },
  { id: 2, label: "Area & time" },
  { id: 3, label: "Constraints" },
  { id: 4, label: "Context" },
  { id: 5, label: "Review" }
] as const;

function fieldClassName() {
  return "mt-1.5 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-cream outline-none focus:border-gold/40";
}

function labelClassName() {
  return "block text-sm text-muted";
}

export function MissionPlanBuilder() {
  const router = useRouter();
  const [state, dispatch] = useReducer(
    missionBuilderReducer,
    initialMissionBuilderState
  );
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  function goNext() {
    const message = validateStep(state.step, state);
    if (message) {
      setError(message);
      return;
    }
    if (state.step === 2 && !state.areaOfInterest) {
      try {
        const area = validateAreaOfInterest(areaFromBboxFields(state));
        dispatch({ type: "setArea", area });
        dispatch({
          type: "patch",
          patch: {
            west: String(area.type === "bbox" ? area.coordinates[0] : state.west),
            south: String(area.type === "bbox" ? area.coordinates[1] : state.south),
            east: String(area.type === "bbox" ? area.coordinates[2] : state.east),
            north: String(area.type === "bbox" ? area.coordinates[3] : state.north)
          }
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Invalid area");
        return;
      }
    }
    setError(null);
    dispatch({ type: "setStep", step: Math.min(5, state.step + 1) });
  }

  function goBack() {
    setError(null);
    dispatch({ type: "setStep", step: Math.max(1, state.step - 1) });
  }

  function applyBboxFromFields() {
    try {
      const area = validateAreaOfInterest(areaFromBboxFields(state));
      dispatch({ type: "setArea", area });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid coordinates");
    }
  }

  function onAreaChange(area: AreaOfInterest | null, mapError?: string) {
    if (mapError) {
      setError(mapError);
      return;
    }
    dispatch({ type: "setArea", area });
    if (area?.type === "bbox") {
      dispatch({
        type: "patch",
        patch: {
          west: String(area.coordinates[0]),
          south: String(area.coordinates[1]),
          east: String(area.coordinates[2]),
          north: String(area.coordinates[3])
        }
      });
    } else if (area?.type === "Polygon") {
      const ring = area.coordinates[0] ?? [];
      const lons = ring.map((p) => p[0]);
      const lats = ring.map((p) => p[1]);
      if (lons.length && lats.length) {
        dispatch({
          type: "patch",
          patch: {
            west: String(Math.min(...lons)),
            south: String(Math.min(...lats)),
            east: String(Math.max(...lons)),
            north: String(Math.max(...lats))
          }
        });
      }
    }
    setError(null);
  }

  async function onUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (file.size > 200_000) {
      setError("GeoJSON file is too large (max ~200 KB).");
      return;
    }
    try {
      const text = await file.text();
      const area = parseGeoJsonUpload(text);
      onAreaChange(area);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not read GeoJSON");
    }
  }

  async function onSubmit() {
    for (let step = 1; step <= 4; step += 1) {
      const message = validateStep(step, state);
      if (message) {
        setError(message);
        dispatch({ type: "setStep", step });
        return;
      }
    }
    setSubmitting(true);
    setError(null);
    try {
      await ensureAnonymousSession();
      const payload = buildMissionCreatePayload(state);
      const created = await createMission(payload);
      router.push(`/missions/${created.mission.id}`);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not create this mission plan."));
      setSubmitting(false);
    }
  }

  const areaPreview = (() => {
    try {
      const area = state.areaOfInterest ?? areaFromBboxFields(state);
      const valid = validateAreaOfInterest(area);
      return `${aoiAreaKm2(valid).toFixed(1)} km²`;
    } catch {
      return "—";
    }
  })();

  return (
    <div className="space-y-6">
      <ol className="flex flex-wrap gap-2" aria-label="Mission plan steps">
        {STEPS.map((step) => {
          const active = state.step === step.id;
          const done = state.step > step.id;
          return (
            <li key={step.id}>
              <button
                aria-current={active ? "step" : undefined}
                className={[
                  "rounded-lg border px-3 py-1.5 text-xs transition-colors",
                  active
                    ? "border-gold/50 bg-gold/10 text-cream"
                    : done
                      ? "border-white/20 text-cream"
                      : "border-white/10 text-muted"
                ].join(" ")}
                onClick={() => {
                  if (step.id < state.step) {
                    setError(null);
                    dispatch({ type: "setStep", step: step.id });
                  }
                }}
                type="button"
              >
                {step.id}. {step.label}
              </button>
            </li>
          );
        })}
      </ol>

      {error ? <InlineNotice message={error} /> : null}

      <LiquidCard>
        {state.step === 1 ? (
          <fieldset className="space-y-3">
            <legend className="chart-label text-gold">What are you trying to do?</legend>
            <p className="text-sm text-muted">
              Pick the closest match. You can refine details later — no account needed.
            </p>
            <div className="mt-4 space-y-2">
              {OBJECTIVE_OPTIONS.map((option) => {
                const selected = state.objectiveType === option.value;
                return (
                  <label
                    className={[
                      "block cursor-pointer rounded-xl border px-4 py-3 transition-colors",
                      selected
                        ? "border-gold/40 bg-gold/5"
                        : "border-white/10 hover:border-white/25"
                    ].join(" ")}
                    key={option.value}
                  >
                    <input
                      checked={selected}
                      className="sr-only"
                      name="objective"
                      onChange={() =>
                        dispatch({
                          type: "set",
                          field: "objectiveType",
                          value: option.value
                        })
                      }
                      type="radio"
                      value={option.value}
                    />
                    <span className="block text-sm font-medium text-cream">
                      {option.label}
                    </span>
                    <span className="mt-1 block text-xs text-muted">
                      {option.description}
                    </span>
                  </label>
                );
              })}
            </div>
          </fieldset>
        ) : null}

        {state.step === 2 ? (
          <div className="space-y-5">
            <div>
              <p className="chart-label text-gold">Where and when?</p>
              <p className="mt-2 text-sm text-muted">
                Draw an area of interest, enter a bounding box, or upload a simple Polygon
                GeoJSON. Coordinates are WGS84.
              </p>
            </div>

            <AoiMapDraw value={state.areaOfInterest} onChange={onAreaChange} />

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {(
                [
                  ["west", "West (lon)"],
                  ["south", "South (lat)"],
                  ["east", "East (lon)"],
                  ["north", "North (lat)"]
                ] as const
              ).map(([field, label]) => (
                <label className={labelClassName()} key={field}>
                  {label}
                  <input
                    className={fieldClassName()}
                    inputMode="decimal"
                    onChange={(event) =>
                      dispatch({ type: "set", field, value: event.target.value })
                    }
                    value={state[field]}
                  />
                </label>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <LiquidButton onClick={applyBboxFromFields} type="button" variant="outline">
                Apply coordinates
              </LiquidButton>
              <p className="text-xs text-muted">Approx. area: {areaPreview}</p>
            </div>

            <label className={labelClassName()}>
              Upload GeoJSON (Polygon only)
              <input
                accept=".json,.geojson,application/geo+json,application/json"
                className="mt-1.5 block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1.5 file:text-cream"
                onChange={onUpload}
                type="file"
              />
            </label>

            <div className="grid gap-3 sm:grid-cols-2">
              <label className={labelClassName()}>
                Start date
                <input
                  className={fieldClassName()}
                  onChange={(event) =>
                    dispatch({ type: "set", field: "startDate", value: event.target.value })
                  }
                  type="date"
                  value={state.startDate}
                />
              </label>
              <label className={labelClassName()}>
                End date
                <input
                  className={fieldClassName()}
                  onChange={(event) =>
                    dispatch({ type: "set", field: "endDate", value: event.target.value })
                  }
                  type="date"
                  value={state.endDate}
                />
              </label>
              <label className={labelClassName()}>
                Desired data freshness (max age, days)
                <input
                  className={fieldClassName()}
                  inputMode="numeric"
                  onChange={(event) =>
                    dispatch({ type: "set", field: "maxAgeDays", value: event.target.value })
                  }
                  placeholder="e.g. 14"
                  value={state.maxAgeDays}
                />
              </label>
              <label className={labelClassName()}>
                Satellite or sensor preference
                <input
                  className={fieldClassName()}
                  onChange={(event) =>
                    dispatch({
                      type: "set",
                      field: "sensorPreference",
                      value: event.target.value
                    })
                  }
                  placeholder="e.g. Sentinel-1"
                  value={state.sensorPreference}
                />
              </label>
            </div>
          </div>
        ) : null}

        {state.step === 3 ? (
          <div className="space-y-5">
            <div>
              <p className="chart-label text-gold">Constraints</p>
              <p className="mt-2 text-sm text-muted">
                Optional limits help later planning. Leave blank if you are unsure.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className={labelClassName()}>
                Deadline
                <input
                  className={fieldClassName()}
                  onChange={(event) =>
                    dispatch({ type: "set", field: "deadline", value: event.target.value })
                  }
                  type="date"
                  value={state.deadline}
                />
              </label>
              <label className={labelClassName()}>
                Preferred place to process
                <select
                  className={fieldClassName()}
                  onChange={(event) =>
                    dispatch({
                      type: "set",
                      field: "preferredComputeLocation",
                      value: event.target.value
                    })
                  }
                  value={state.preferredComputeLocation}
                >
                  {COMPUTE_LOCATION_OPTIONS.map((option) => (
                    <option key={option.value || "none"} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className={labelClassName()}>
                Onboard processing
                <select
                  className={fieldClassName()}
                  onChange={(event) =>
                    dispatch({
                      type: "set",
                      field: "onboardProcessing",
                      value: event.target.value
                    })
                  }
                  value={state.onboardProcessing}
                >
                  {ONBOARD_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div>
              <button
                aria-expanded={advancedOpen}
                className="text-sm text-gold hover:underline"
                onClick={() => setAdvancedOpen((open) => !open)}
                type="button"
              >
                {advancedOpen ? "Hide advanced" : "Advanced"}
              </button>
              {advancedOpen ? (
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <label className={labelClassName()}>
                    Max cost (USD)
                    <input
                      className={fieldClassName()}
                      inputMode="decimal"
                      onChange={(event) =>
                        dispatch({
                          type: "set",
                          field: "maxCostUsd",
                          value: event.target.value
                        })
                      }
                      value={state.maxCostUsd}
                    />
                  </label>
                  <label className={labelClassName()}>
                    Max data volume (MB)
                    <input
                      className={fieldClassName()}
                      inputMode="decimal"
                      onChange={(event) =>
                        dispatch({
                          type: "set",
                          field: "maxDataVolumeMb",
                          value: event.target.value
                        })
                      }
                      value={state.maxDataVolumeMb}
                    />
                  </label>
                  <label className={labelClassName()}>
                    Allowed geographic regions
                    <input
                      className={fieldClassName()}
                      onChange={(event) =>
                        dispatch({
                          type: "set",
                          field: "allowedRegions",
                          value: event.target.value
                        })
                      }
                      placeholder="e.g. EU, US"
                      value={state.allowedRegions}
                    />
                  </label>
                  <label className={labelClassName()}>
                    Data residency requirement
                    <input
                      className={fieldClassName()}
                      onChange={(event) =>
                        dispatch({
                          type: "set",
                          field: "dataResidency",
                          value: event.target.value
                        })
                      }
                      placeholder="e.g. Must stay in EU"
                      value={state.dataResidency}
                    />
                  </label>
                  <label className={`${labelClassName()} sm:col-span-2`}>
                    Existing cloud or infrastructure
                    <input
                      className={fieldClassName()}
                      onChange={(event) =>
                        dispatch({
                          type: "set",
                          field: "cloudProvider",
                          value: event.target.value
                        })
                      }
                      placeholder="e.g. AWS, Azure, on-prem"
                      value={state.cloudProvider}
                    />
                  </label>
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        {state.step === 4 ? (
          <div className="space-y-5">
            <div>
              <p className="chart-label text-gold">Mission context</p>
              <p className="mt-2 text-sm text-muted">
                A short title is enough to save a private plan in this browser session.
              </p>
            </div>
            <label className={labelClassName()}>
              Mission title
              <input
                className={fieldClassName()}
                onChange={(event) =>
                  dispatch({ type: "set", field: "title", value: event.target.value })
                }
                required
                value={state.title}
              />
            </label>
            <label className={labelClassName()}>
              Organization name (optional)
              <input
                className={fieldClassName()}
                onChange={(event) =>
                  dispatch({
                    type: "set",
                    field: "organizationName",
                    value: event.target.value
                  })
                }
                value={state.organizationName}
              />
            </label>
            <label className={labelClassName()}>
              Use case
              <textarea
                className={`${fieldClassName()} min-h-[88px]`}
                onChange={(event) =>
                  dispatch({ type: "set", field: "useCase", value: event.target.value })
                }
                value={state.useCase}
              />
            </label>
            <label className={labelClassName()}>
              Technical notes
              <textarea
                className={`${fieldClassName()} min-h-[88px]`}
                onChange={(event) =>
                  dispatch({ type: "set", field: "notes", value: event.target.value })
                }
                value={state.notes}
              />
            </label>
            <fieldset className="space-y-2">
              <legend className="text-sm text-muted">Mission mode</legend>
              {MISSION_MODE_OPTIONS.map((option) => (
                <label className="flex items-start gap-2 text-sm text-cream" key={option.value}>
                  <input
                    checked={state.missionMode === option.value}
                    className="mt-1"
                    name="missionMode"
                    onChange={() =>
                      dispatch({
                        type: "set",
                        field: "missionMode",
                        value: option.value
                      })
                    }
                    type="radio"
                    value={option.value}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </fieldset>
          </div>
        ) : null}

        {state.step === 5 ? (
          <div className="space-y-4">
            <div>
              <p className="chart-label text-gold">Review your mission plan</p>
              <p className="mt-2 text-sm text-muted">
                Confirm these details. Saving creates a private mission for this browser
                session only.
              </p>
            </div>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <ReviewItem
                label="Objective"
                value={
                  state.objectiveType
                    ? OBJECTIVE_LABELS[state.objectiveType as ObjectiveType]
                    : "—"
                }
              />
              <ReviewItem label="Title" value={state.title || "—"} />
              <ReviewItem label="Mode" value={state.missionMode} />
              <ReviewItem label="Approx. area" value={areaPreview} />
              <ReviewItem
                label="Date range"
                value={
                  state.startDate || state.endDate
                    ? `${state.startDate || "…"} → ${state.endDate || "…"}`
                    : "Not set"
                }
              />
              <ReviewItem
                label="Freshness"
                value={state.maxAgeDays ? `${state.maxAgeDays} days` : "Not set"}
              />
              <ReviewItem
                label="Sensor preference"
                value={state.sensorPreference || "Not set"}
              />
              <ReviewItem label="Deadline" value={state.deadline || "Not set"} />
              <ReviewItem
                label="Preferred processing"
                value={state.preferredComputeLocation || "No preference"}
              />
              <ReviewItem label="Onboard processing" value={state.onboardProcessing} />
              <ReviewItem
                label="Max cost"
                value={state.maxCostUsd ? `$${state.maxCostUsd}` : "Not set"}
              />
              <ReviewItem
                label="Max data volume"
                value={state.maxDataVolumeMb ? `${state.maxDataVolumeMb} MB` : "Not set"}
              />
              <ReviewItem
                label="Allowed regions"
                value={state.allowedRegions || "Not set"}
              />
              <ReviewItem
                label="Data residency"
                value={state.dataResidency || "Not set"}
              />
              <ReviewItem
                label="Cloud / infra"
                value={state.cloudProvider || "Not set"}
              />
              <ReviewItem
                label="Organization"
                value={state.organizationName || "Not set"}
              />
              <ReviewItem label="Use case" value={state.useCase || "Not set"} />
              <ReviewItem label="Notes" value={state.notes || "Not set"} />
            </dl>
          </div>
        ) : null}

        <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
          <LiquidButton
            disabled={state.step === 1 || submitting}
            onClick={goBack}
            type="button"
            variant="ghost"
          >
            Back
          </LiquidButton>
          {state.step < 5 ? (
            <LiquidButton onClick={goNext} type="button" variant="primary">
              Continue
            </LiquidButton>
          ) : (
            <LiquidButton
              disabled={submitting}
              onClick={onSubmit}
              type="button"
              variant="primary"
            >
              {submitting ? "Saving…" : "Create mission plan"}
            </LiquidButton>
          )}
        </div>
      </LiquidCard>
    </div>
  );
}

function ReviewItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 px-3 py-2">
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="mt-1 whitespace-pre-wrap text-cream">{value}</dd>
    </div>
  );
}
