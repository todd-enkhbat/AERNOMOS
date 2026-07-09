import type { ReactNode } from "react";

type SectionBackdropProps = {
  variant?: "chart" | "charon" | "none";
  children: ReactNode;
  className?: string;
  id?: string;
};

export function SectionBackdrop({
  variant = "chart",
  children,
  className = "",
  id
}: SectionBackdropProps) {
  const variantClass =
    variant === "chart"
      ? "section-backdrop--chart"
      : variant === "charon"
        ? "section-backdrop--charon"
        : "";

  return (
    <section
      className={`section-backdrop ${variantClass} ${className}`.trim()}
      id={id}
    >
      {children}
    </section>
  );
}
