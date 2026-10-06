import type { LucideIcon } from "lucide-react";
import {
  Antenna,
  Braces,
  CloudCog,
  Database,
  FileCheck2,
  Orbit,
  RadioTower,
  Route,
  Satellite,
  SatelliteDish,
  ServerCog,
  Waypoints
} from "lucide-react";

import { NomosMark } from "@/components/brand/NomosMark";

type Provider = {
  label: string;
  detail: string;
  icon: LucideIcon;
  selected?: boolean;
};

type Layer = {
  id: "orbital" | "ground" | "cloud";
  index: string;
  label: string;
  detail: string;
  icon: LucideIcon;
  providers: [Provider, Provider];
};

const LAYERS: Layer[] = [
  {
    id: "orbital",
    index: "01",
    label: "Orbital",
    detail: "spacecraft + sensors",
    icon: Orbit,
    providers: [
      { label: "Operator A", detail: "tasking API", icon: Satellite },
      {
        label: "Operator B",
        detail: "fleet constraints",
        icon: SatelliteDish,
        selected: true
      }
    ]
  },
  {
    id: "ground",
    index: "02",
    label: "Ground",
    detail: "contact + downlink",
    icon: RadioTower,
    providers: [
      {
        label: "Station net",
        detail: "pass interfaces",
        icon: RadioTower,
        selected: true
      },
      { label: "Teleport", detail: "reservation rules", icon: Antenna }
    ]
  },
  {
    id: "cloud",
    index: "03",
    label: "Cloud",
    detail: "compute + delivery",
    icon: CloudCog,
    providers: [
      {
        label: "Region A",
        detail: "processing runtime",
        icon: ServerCog,
        selected: true
      },
      { label: "Region B", detail: "data residency", icon: Database }
    ]
  }
];

function ProviderNode({
  provider,
  unified,
  direct
}: {
  provider: Provider;
  unified?: boolean;
  direct?: boolean;
}) {
  const Icon = provider.icon;
  const selected = unified && provider.selected;

  return (
    <div
      className={`stack-instrument__provider ${
        selected ? "stack-instrument__provider--selected" : ""
      } ${direct ? "stack-instrument__provider--direct" : ""}`}
    >
      <span className="stack-instrument__provider-icon">
        <Icon aria-hidden size={16} strokeWidth={1.45} />
      </span>
      <span className="stack-instrument__provider-copy">
        <strong>{provider.label}</strong>
        <small>{provider.detail}</small>
      </span>
      <span aria-hidden className="stack-instrument__port" />
      {selected ? <span className="stack-instrument__selected-label">Path</span> : null}
    </div>
  );
}

function LayerRow({ layer, unified }: { layer: Layer; unified?: boolean }) {
  const Icon = layer.icon;

  return (
    <div className={`stack-instrument__layer stack-instrument__layer--${layer.id}`}>
      <div className="stack-instrument__layer-label">
        <span>{layer.index}</span>
        <Icon aria-hidden size={15} strokeWidth={1.35} />
        <div>
          <strong>{layer.label}</strong>
          <small>{layer.detail}</small>
        </div>
      </div>
      <div className="stack-instrument__providers">
        {layer.providers.map((provider) => (
          <ProviderNode key={provider.label} provider={provider} unified={unified} />
        ))}
      </div>
    </div>
  );
}

function InstrumentHeader({
  index,
  label,
  metric,
  tone
}: {
  index: string;
  label: string;
  metric: string;
  tone: "fragmented" | "unified";
}) {
  return (
    <div className="stack-instrument__header">
      <div className="stack-instrument__title">
        <span>{index}</span>
        <p>{label}</p>
      </div>
      <p className={`stack-instrument__metric stack-instrument__metric--${tone}`}>
        {metric}
      </p>
    </div>
  );
}

function FragmentedInstrument() {
  const directInterfaces = LAYERS.flatMap((layer) =>
    layer.providers.map((provider) => ({ layer, provider }))
  );

  return (
    <section className="stack-instrument stack-instrument--fragmented">
      <InstrumentHeader
        index="A"
        label="Today · direct integration"
        metric="6 provider surfaces"
        tone="fragmented"
      />
      <div
        aria-label="A mission team connects independently to six provider interfaces across orbital, ground, and cloud infrastructure."
        className="stack-instrument__viewport"
        role="img"
      >
        <div aria-hidden className="stack-instrument__registration">
          NOMOS / ACCESS STUDY / A
        </div>
        <div aria-hidden className="stack-instrument__direct-matrix">
          <div className="stack-instrument__direct-team">
            <Braces size={16} strokeWidth={1.4} />
            <span>
              <strong>Mission team</strong>
              <small>one objective</small>
            </span>
          </div>
          {directInterfaces.map(({ layer, provider }, index) => (
            <div
              className="stack-instrument__direct-source"
              key={`${layer.id}-${provider.label}`}
              style={{ gridRow: index + 2 }}
            >
              <span className="stack-instrument__direct-port" />
              <small>CONTRACT {String(index + 1).padStart(2, "0")}</small>
            </div>
          ))}
          {directInterfaces.map(({ layer, provider }, index) => {
            const Icon = layer.icon;

            return (
              <div
                className="stack-instrument__direct-route"
                key={`${layer.id}-${provider.label}`}
                style={{ gridRow: index + 2 }}
              >
                <div className="stack-instrument__direct-route-meta">
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <Icon aria-hidden size={14} strokeWidth={1.35} />
                  <small>{provider.detail}</small>
                </div>
                <ProviderNode direct provider={provider} />
              </div>
            );
          })}
        </div>
      </div>
      <div className="stack-instrument__footer">
        <span>Duplicated contracts</span>
        <span>Manual coordination</span>
        <span>Opaque constraints</span>
      </div>
    </section>
  );
}

function UnifiedInstrument() {
  return (
    <section className="stack-instrument stack-instrument--unified">
      <InstrumentHeader
        index="B"
        label="With Nomos · one layer above"
        metric="1 request surface"
        tone="unified"
      />
      <div
        aria-label="One request enters the Nomos intelligence layer. Nomos resolves a source-backed path across the same six orbital, ground, and cloud providers through one interface."
        className="stack-instrument__viewport"
        role="img"
      >
        <div aria-hidden className="stack-instrument__registration">
          NOMOS / ACCESS STUDY / B
        </div>
        <div aria-hidden className="stack-instrument__request stack-instrument__request--objective">
          <Route size={16} strokeWidth={1.4} />
          <span>
            <strong>One request</strong>
            <small>objective · AOI · timing</small>
          </span>
        </div>
        <div aria-hidden className="stack-instrument__nomos">
          <div className="stack-instrument__nomos-identity">
            <NomosMark size={30} />
            <span>
              <strong>Nomos</strong>
              <small>resolve · rank · explain</small>
            </span>
          </div>
          <div className="stack-instrument__nomos-logic">
            <Waypoints size={15} strokeWidth={1.35} />
            <span>source-backed path</span>
          </div>
        </div>
        <div aria-hidden className="stack-instrument__spine">
          <span className="stack-instrument__signal stack-instrument__signal--one" />
          <span className="stack-instrument__signal stack-instrument__signal--two" />
          <span className="stack-instrument__signal stack-instrument__signal--three" />
        </div>
        <div aria-hidden className="stack-instrument__layers stack-instrument__layers--unified">
          {LAYERS.map((layer) => (
            <LayerRow key={layer.id} layer={layer} unified />
          ))}
        </div>
      </div>
      <div className="stack-instrument__footer stack-instrument__footer--unified">
        <span>One objective</span>
        <span>Ranked path</span>
        <span>Sources attached</span>
      </div>
    </section>
  );
}

export function StackComparison() {
  return (
    <figure className="stack-comparison">
      <div className="stack-comparison__frame" aria-hidden />
      <div className="stack-comparison__grid">
        <FragmentedInstrument />
        <div aria-hidden className="stack-comparison__divider">
          <span>vs</span>
        </div>
        <UnifiedInstrument />
      </div>
      <figcaption className="stack-comparison__caption">
        <span>
          <Orbit aria-hidden size={15} strokeWidth={1.4} /> Same infrastructure
        </span>
        <span>
          <Waypoints aria-hidden size={15} strokeWidth={1.4} /> Same six providers
        </span>
        <span>
          <FileCheck2 aria-hidden size={15} strokeWidth={1.4} /> One coherent access model
        </span>
      </figcaption>
    </figure>
  );
}
