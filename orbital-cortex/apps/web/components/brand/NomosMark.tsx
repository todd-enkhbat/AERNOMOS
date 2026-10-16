import Image from "next/image";
import styles from "./NomosMark.module.css";

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
      className={`${styles.mark} ${spinning ? "record-spin" : ""} ${className ?? ""}`}
      style={{ width: size, height: size }}
    >
      <Image
        alt=""
        className={styles.image}
        height={size * 2}
        priority={size >= 32}
        src="/images/nomos-golden-record.png"
        width={size * 2}
      />
    </span>
  );
}
