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
        cream: "var(--cream)",
        "cream-2": "var(--cream-2)",
        ink: "var(--ink)",
        gold: "#c9a227",
        "gold-bright": "#e3c05c",
        brass: "#a8842c",
        cobalt: "#496a9b",
        vermilion: "#a84d35",
        silver: "#b8b4ac",
        "silver-dim": "#6f6c66",
        muted: "#a49b8b",
        "muted-dark": "#6f6a5e",
        line: "rgba(244, 239, 230, 0.08)"
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
