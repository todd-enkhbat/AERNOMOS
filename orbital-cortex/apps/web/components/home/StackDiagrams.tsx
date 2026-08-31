/**
 * Two contrasting views of the same space stack.
 *
 * Each tier is a disc in perspective — a plane seen edge-on — so "which layer"
 * reads literally. Both panels carry the identical six providers; the only
 * difference is how they are reached. Panel A wires each one by hand. Panel B
 * adds one gold plane above the stack and reaches all of them through it.
 */

const CX = 190;
const RX = 132;
const RY = 28;

const CROWN_Y = 56;

type Provider = { id: string; label: string; x: number };

type Layer = {
  id: string;
  name: string;
  y: number;
  icon: "orbital" | "ground" | "cloud";
  providers: Provider[];
};

const LAYERS: Layer[] = [
  {
    id: "orbital",
    name: "ORBITAL",
    y: 150,
    icon: "orbital",
    providers: [
      { id: "op-a", label: "Operator A", x: 130 },
      { id: "op-b", label: "Operator B", x: 250 }
    ]
  },
  {
    id: "ground",
    name: "GROUND",
    y: 228,
    icon: "ground",
    providers: [
      { id: "gs-a", label: "Station net", x: 126 },
      { id: "gs-b", label: "Teleport", x: 248 }
    ]
  },
  {
    id: "cloud",
    name: "CLOUD",
    y: 306,
    icon: "cloud",
    providers: [
      { id: "cl-a", label: "Region A", x: 130 },
      { id: "cl-b", label: "Region B", x: 250 }
    ]
  }
];

const NODE_Y_OFFSET = -6;

function LayerIcon({ kind, x, y }: { kind: Layer["icon"]; x: number; y: number }) {
  return (
    <g
      fill="none"
      opacity={0.8}
      stroke="#e3c05c"
      strokeLinecap="round"
      strokeWidth={1.3}
      transform={`translate(${x} ${y})`}
      vectorEffect="non-scaling-stroke"
    >
      {kind === "orbital" ? (
        <>
          <circle cx={0} cy={0} r={3.2} />
          <ellipse cx={0} cy={0} rx={10} ry={4.4} transform="rotate(-24)" />
        </>
      ) : null}
      {kind === "ground" ? (
        <>
          <path d="M-6.5 5.5 L0.5 5.5 L-3 -2.5 Z" />
          <path d="M-3 -2.5 A7.5 7.5 0 0 1 7.5 -5.5" />
        </>
      ) : null}
      {kind === "cloud" ? (
        <>
          <rect height={4} rx={1} width={15} x={-7.5} y={-6.5} />
          <rect height={4} rx={1} width={15} x={-7.5} y={0.5} />
          <path d="M-4.5 -4.5h.01M-4.5 2.5h.01" />
        </>
      ) : null}
    </g>
  );
}

/** Dark plate behind label text so copy never sits directly on a connector. */
function Pill({
  x,
  y,
  label,
  tone = "muted",
  width
}: {
  x: number;
  y: number;
  label: string;
  tone?: "muted" | "gold" | "warn";
  width: number;
}) {
  const palette = {
    muted: { fill: "rgba(6,10,28,0.88)", stroke: "rgba(200,196,220,0.3)", text: "#c8c4dc" },
    gold: { fill: "rgba(30,22,4,0.9)", stroke: "rgba(227,192,92,0.6)", text: "#e3c05c" },
    warn: { fill: "rgba(30,11,7,0.9)", stroke: "rgba(168,77,53,0.6)", text: "#d99178" }
  }[tone];

  return (
    <g>
      <rect
        fill={palette.fill}
        height={19}
        rx={9.5}
        stroke={palette.stroke}
        strokeWidth={1}
        vectorEffect="non-scaling-stroke"
        width={width}
        x={x - width / 2}
        y={y - 9.5}
      />
      <text
        className="metric-value"
        fill={palette.text}
        fontSize={9}
        textAnchor="middle"
        x={x}
        y={y + 3.2}
      >
        {label}
      </text>
    </g>
  );
}

function LayerDisc({ layer, dim }: { layer: Layer; dim?: boolean }) {
  return (
    <g>
      <ellipse
        cx={CX}
        cy={layer.y}
        fill={dim ? "url(#disc-dim)" : "url(#disc-lit)"}
        rx={RX}
        ry={RY}
        stroke={dim ? "rgba(200,196,220,0.2)" : "rgba(227,192,92,0.28)"}
        strokeWidth={1}
        vectorEffect="non-scaling-stroke"
      />
      {/* Front rim reads brighter than the back — suggests a solid plane. */}
      <path
        d={`M ${CX - RX} ${layer.y} A ${RX} ${RY} 0 0 0 ${CX + RX} ${layer.y}`}
        fill="none"
        stroke={dim ? "rgba(200,196,220,0.4)" : "rgba(227,192,92,0.55)"}
        strokeWidth={1.2}
        vectorEffect="non-scaling-stroke"
      />
      <text
        className="metric-value"
        fill={dim ? "#8a86a8" : "#c9a227"}
        fontSize={10.5}
        letterSpacing="0.14em"
        x={CX - RX + 2}
        y={layer.y - RY - 8}
      >
        {layer.name}
      </text>
      <LayerIcon kind={layer.icon} x={CX + RX - 15} y={layer.y - 3} />
    </g>
  );
}

/** Each hand-built link gets its own dash, tone and bend — nothing is shared. */
const TANGLE = [
  { dash: "5 3", bend: 96, tone: "#a84d35", opacity: 0.75 },
  { dash: "1 4", bend: -88, tone: "#8a86a8", opacity: 0.6 },
  { dash: "7 4", bend: 74, tone: "#a84d35", opacity: 0.6 },
  { dash: "2 3", bend: -104, tone: "#b8b4c8", opacity: 0.5 },
  { dash: "9 5", bend: 112, tone: "#a84d35", opacity: 0.68 },
  { dash: "1 6", bend: -70, tone: "#8a86a8", opacity: 0.62 }
];

export function FragmentedStack() {
  const targets = LAYERS.flatMap((layer) =>
    layer.providers.map((provider) => ({
      ...provider,
      y: layer.y + NODE_Y_OFFSET
    }))
  );

  return (
    <figure className="rounded-2xl border border-white/10 bg-klein-void/40 p-5 sm:p-6">
      <figcaption className="chart-label text-muted-dark">
        Today · direct integration
      </figcaption>
      <svg
        aria-label="A single team wires itself by hand to six separate providers spread across the orbital, ground, and cloud layers. Each link crosses the stack on its own terms, with no shared layer between them."
        className="mt-4 w-full"
        role="img"
        viewBox="0 0 380 350"
      >
        <defs>
          <radialGradient cx="50%" cy="32%" id="disc-dim" r="72%">
            <stop offset="0%" stopColor="#2a2f52" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#0b1030" stopOpacity={0.2} />
          </radialGradient>
        </defs>

        {/* Links sit under the discs so they read as threading down through the stack. */}
        {targets.map((target, index) => {
          const wire = TANGLE[index];
          return (
            <path
              d={`M ${CX} ${CROWN_Y + 13} Q ${(CX + target.x) / 2 + wire.bend} ${
                (CROWN_Y + target.y) / 2
              } ${target.x} ${target.y}`}
              fill="none"
              key={target.id}
              stroke={wire.tone}
              strokeDasharray={wire.dash}
              strokeOpacity={wire.opacity}
              strokeWidth={1.5}
              vectorEffect="non-scaling-stroke"
            />
          );
        })}

        {LAYERS.map((layer) => (
          <LayerDisc dim key={layer.id} layer={layer} />
        ))}

        {targets.map((target) => (
          <g key={`node-${target.id}`}>
            <circle
              cx={target.x}
              cy={target.y}
              fill="rgba(6,10,28,0.92)"
              r={4.2}
              stroke="rgba(168,77,53,0.8)"
              strokeWidth={1.3}
              vectorEffect="non-scaling-stroke"
            />
            <Pill label={target.label} width={66} x={target.x} y={target.y + 18} />
          </g>
        ))}

        <circle
          cx={CX}
          cy={CROWN_Y}
          fill="rgba(168,77,53,0.16)"
          r={13}
          stroke="#a84d35"
          strokeWidth={1.5}
          vectorEffect="non-scaling-stroke"
        />
        <Pill label="YOUR TEAM" tone="warn" width={78} x={CX} y={CROWN_Y - 26} />
      </svg>
      <p className="mt-4 text-xs leading-5 text-muted-dark">
        Six providers, six interfaces, six sets of constraints — wired again by
        every team before a single workload runs.
      </p>
    </figure>
  );
}

export function UnifiedStack() {
  const spineTop = CROWN_Y + RY;
  const spineBottom = LAYERS[LAYERS.length - 1].y;

  return (
    <figure className="rounded-2xl border border-gold/35 bg-gold/[0.05] p-5 sm:p-6">
      <figcaption className="chart-label text-gold">
        With Nomos · one layer above
      </figcaption>
      <svg
        aria-label="A gold Nomos plane sits above the stack as its own layer. One spine runs from Nomos down through the orbital, ground, and cloud layers, reaching the same six providers through a single interface."
        className="mt-4 w-full"
        role="img"
        viewBox="0 0 380 350"
      >
        <defs>
          <radialGradient cx="50%" cy="32%" id="disc-lit" r="72%">
            <stop offset="0%" stopColor="#2d3566" stopOpacity={0.55} />
            <stop offset="100%" stopColor="#0b1030" stopOpacity={0.22} />
          </radialGradient>
          <radialGradient cx="50%" cy="38%" id="nomos-plane" r="70%">
            <stop offset="0%" stopColor="#e3c05c" stopOpacity={0.4} />
            <stop offset="65%" stopColor="#c9a227" stopOpacity={0.16} />
            <stop offset="100%" stopColor="#c9a227" stopOpacity={0.05} />
          </radialGradient>
          <filter height="260%" id="plane-glow" width="180%" x="-40%" y="-80%">
            <feGaussianBlur stdDeviation="7" />
          </filter>
        </defs>

        {/* One spine, drawn behind the discs so every layer sits on it. */}
        <line
          stroke="rgba(227,192,92,0.3)"
          strokeWidth={1.4}
          vectorEffect="non-scaling-stroke"
          x1={CX}
          x2={CX}
          y1={spineTop}
          y2={spineBottom}
        />
        <line
          className="route-flow"
          stroke="#e3c05c"
          strokeWidth={1.9}
          vectorEffect="non-scaling-stroke"
          x1={CX}
          x2={CX}
          y1={spineTop}
          y2={spineBottom}
        />

        {LAYERS.map((layer) => (
          <g key={layer.id}>
            <LayerDisc layer={layer} />
            {layer.providers.map((provider) => (
              <line
                key={`reach-${provider.id}`}
                stroke="rgba(227,192,92,0.45)"
                strokeWidth={1.1}
                vectorEffect="non-scaling-stroke"
                x1={CX}
                x2={provider.x}
                y1={layer.y}
                y2={layer.y + NODE_Y_OFFSET}
              />
            ))}
            <circle
              cx={CX}
              cy={layer.y}
              fill="#e3c05c"
              r={3.8}
              stroke="rgba(11,16,48,0.9)"
              strokeWidth={1.2}
              vectorEffect="non-scaling-stroke"
            />
            {layer.providers.map((provider) => (
              <g key={provider.id}>
                <circle
                  cx={provider.x}
                  cy={layer.y + NODE_Y_OFFSET}
                  fill="rgba(6,10,28,0.92)"
                  r={4.2}
                  stroke="rgba(227,192,92,0.85)"
                  strokeWidth={1.3}
                  vectorEffect="non-scaling-stroke"
                />
                <Pill
                  label={provider.label}
                  width={66}
                  x={provider.x}
                  y={layer.y + NODE_Y_OFFSET + 18}
                />
              </g>
            ))}
          </g>
        ))}

        {/* Nomos as a full-width plane, not a node — the layer above the stack. */}
        <ellipse
          cx={CX}
          cy={CROWN_Y}
          fill="rgba(227,192,92,0.22)"
          filter="url(#plane-glow)"
          rx={RX}
          ry={RY}
        />
        <ellipse
          cx={CX}
          cy={CROWN_Y}
          fill="url(#nomos-plane)"
          rx={RX}
          ry={RY}
          stroke="#e3c05c"
          strokeWidth={1.6}
          vectorEffect="non-scaling-stroke"
        />
        <path
          d={`M ${CX - RX} ${CROWN_Y} A ${RX} ${RY} 0 0 0 ${CX + RX} ${CROWN_Y}`}
          fill="none"
          stroke="#e3c05c"
          strokeWidth={2}
          vectorEffect="non-scaling-stroke"
        />
        <text
          className="metric-value"
          fill="#f4efe6"
          fontSize={12}
          fontWeight={600}
          letterSpacing="0.2em"
          textAnchor="middle"
          x={CX}
          y={CROWN_Y + 4}
        >
          NOMOS
        </text>
        <Pill label="ONE REQUEST" tone="gold" width={88} x={CX} y={CROWN_Y - RY - 12} />
      </svg>
      <p className="mt-4 text-xs leading-5 text-cream/70">
        The same six providers, unchanged. Nomos resolves which of them should
        answer a request — everything below stays reachable through one interface.
      </p>
    </figure>
  );
}
