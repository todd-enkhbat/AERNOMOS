import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        void: "var(--void)",
        "void-2": "var(--void-2)",
        panel: "var(--panel)",
        klein: "var(--klein)",
        "klein-deep": "var(--klein-deep)",
        "klein-void": "var(--klein-void)",
        cream: "var(--cream)",
        "cream-2": "var(--cream-2)",
        ink: "var(--ink)",
        gold: "#c9a227",
        "gold-bright": "#e3c05c",
        brass: "#a8842c",
        cobalt: "#4a6ec8",
        vermilion: "#a84d35",
        silver: "#c8c4dc",
        "silver-dim": "#8a86a8",
        muted: "#b8b4c8",
        "muted-dark": "#7a7694",
        parchment: "var(--parchment)",
        "parchment-ink": "var(--parchment-ink)",
        "parchment-muted": "var(--parchment-muted)",
        line: "rgba(244, 239, 230, 0.1)"
      },
      fontFamily: {
        serif: ["var(--font-serif)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "SFMono-Regular", "monospace"]
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0, 0, 0, 0.28)",
        lift: "0 16px 48px rgba(0, 0, 0, 0.38)"
      },
      letterSpacing: {
        chart: "0.14em"
      }
    }
  },
  plugins: []
};

export default config;
