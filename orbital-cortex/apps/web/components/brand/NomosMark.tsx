import Image from "next/image";

type NomosMarkProps = {
  size?: number;
  className?: string;
  /** Slow idle rotation of the disc. */
  spinning?: boolean;
};

/** Voyager Golden Record. Nomos Orbital company mark. */
export function NomosMark({
  size = 32,
  className,
  spinning = false
}: NomosMarkProps) {
  return (
    <span
      aria-hidden
      className={`inline-block shrink-0 overflow-hidden rounded-full shadow-[0_0_12px_rgba(201,162,39,0.35)] ${spinning ? "record-spin" : ""} ${className ?? ""}`}
      style={{ width: size, height: size }}
    >
      <Image
        alt=""
        className="h-full w-full object-cover"
        height={size * 2}
        priority={size >= 32}
        src="/images/nomos-golden-record.png"
        width={size * 2}
      />
    </span>
  );
}
