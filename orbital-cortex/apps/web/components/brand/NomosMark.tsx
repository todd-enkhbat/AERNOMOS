type NomosMarkProps = {
  size?: number;
  className?: string;
  /** Slow idle rotation of the etched disc. */
  spinning?: boolean;
  /** Line color; defaults to gold. */
  tone?: "gold" | "cream" | "ink";
};

const tones = {
  gold: "#c9a227",
  cream: "#f4efe6",
  ink: "#1a1814"
};

/**
 * Nomos Orbital medallion — an homage to the Voyager Golden Record.
 * Etched diagrams: playback stylus (top-left), waveform (top-right),
 * pulsar burst (bottom-left), hydrogen hyperfine pair (bottom-right).
 */
export function NomosMark({
  size = 32,
  className,
  spinning = false,
  tone = "gold"
}: NomosMarkProps) {
  const stroke = tones[tone];

  return (
    <svg
      aria-hidden
      className={className}
      fill="none"
      height={size}
      viewBox="0 0 100 100"
      width={size}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* outer orbit ring */}
      <circle
        className="orbit-dash"
        cx="50"
        cy="50"
        opacity="0.5"
        r="48"
        stroke={stroke}
        strokeWidth="1"
      />

      <g className={spinning ? "record-spin" : undefined}>
        {/* disc rim */}
        <circle cx="50" cy="50" r="41" stroke={stroke} strokeWidth="1.6" />
        {/* groove hints */}
        <circle cx="50" cy="50" opacity="0.35" r="36.5" stroke={stroke} strokeWidth="0.5" />
        <circle cx="50" cy="50" opacity="0.2" r="32" stroke={stroke} strokeWidth="0.5" />
        {/* spindle hole */}
        <circle cx="50" cy="50" r="2.4" stroke={stroke} strokeWidth="1.2" />

        {/* playback stylus arc — top-left */}
        <circle cx="35" cy="35" opacity="0.9" r="9" stroke={stroke} strokeDasharray="2.5 2" strokeWidth="1" />
        <circle cx="35" cy="35" r="1.4" fill={stroke} />
        <path d="M42 28 L47 23" stroke={stroke} strokeLinecap="round" strokeWidth="1.2" />

        {/* waveform — top-right */}
        <path
          d="M56 30 l3 0 2 -5 2 9 2 -7 2 5 2 -3 2 4 3 0"
          stroke={stroke}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.1"
        />
        <path d="M58 37 h16" opacity="0.55" stroke={stroke} strokeDasharray="1.5 2" strokeWidth="0.9" />

        {/* pulsar burst — bottom-left */}
        <g stroke={stroke} strokeLinecap="round" strokeWidth="1">
          <path d="M36 65 L21 57" />
          <path d="M36 65 L26 74" />
          <path d="M36 65 L45 79" />
          <path d="M36 65 L52 66" opacity="0.85" />
          <path d="M36 65 L40 51" opacity="0.85" />
          <path d="M36 65 L24 66.5" opacity="0.6" />
          <path d="M36 65 L34 78" opacity="0.6" />
        </g>
        <circle cx="36" cy="65" fill={stroke} r="1.3" />

        {/* hydrogen hyperfine transition — bottom-right */}
        <circle cx="63" cy="68" r="4.2" stroke={stroke} strokeWidth="1" />
        <circle cx="77" cy="68" r="4.2" stroke={stroke} strokeWidth="1" />
        <path d="M67.2 68 h5.6" stroke={stroke} strokeWidth="1" />
        <path d="M63 63.8 v-2.6" stroke={stroke} strokeLinecap="round" strokeWidth="1" />
        <path d="M77 72.2 v2.6" stroke={stroke} strokeLinecap="round" strokeWidth="1" />
      </g>
    </svg>
  );
}
