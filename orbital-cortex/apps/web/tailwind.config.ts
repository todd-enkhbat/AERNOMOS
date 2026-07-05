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
        bone: "#f5eddf",
        parchment: "#fffaf0",
        ink: "#17140f",
        basalt: "#232018",
        copper: "#a86f35",
        umber: "#6f4d2e",
        orbital: "#25495a",
        sage: "#68735d"
      },
      fontFamily: {
        serif: ["Georgia", "\"Times New Roman\"", "serif"],
        mono: ["\"SFMono-Regular\"", "Consolas", "\"Liberation Mono\"", "monospace"]
      },
      boxShadow: {
        panel: "0 18px 50px rgba(37, 32, 22, 0.10)"
      }
    }
  },
  plugins: []
};

export default config;
