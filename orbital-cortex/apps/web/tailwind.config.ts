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
        void: "#0a0a0b",
        "void-2": "#12110f",
        panel: "#161513",
        cream: "#f4efe6",
        "cream-2": "#e8e0cf",
        ink: "#1a1814",
        gold: "#c9a227",
        "gold-bright": "#e3c05c",
        brass: "#a8842c",
        teal: "#5f97ad",
        "teal-deep": "#25495a",
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
