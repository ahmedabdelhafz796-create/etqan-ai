import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/app/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1280px" },
    },
    extend: {
      colors: {
        // Dark luxury financial palette
        night: {
          DEFAULT: "#05070C",
          900: "#05070C",
          800: "#080B12",
          700: "#0C1019",
          600: "#121826",
          500: "#1A2233",
        },
        gold: {
          DEFAULT: "#E9C46A",
          light: "#F4D98B",
          deep: "#C9A227",
          muted: "#B08D2E",
        },
        emerald: {
          DEFAULT: "#12B981",
          light: "#34D399",
          deep: "#0B7A56",
        },
        royal: {
          DEFAULT: "#2563EB",
          light: "#3B82F6",
          deep: "#1E3A8A",
        },
        loss: {
          DEFAULT: "#EF4444",
          deep: "#B91C1C",
        },
        soft: "#E6EAF2",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-clash)", "var(--font-inter)", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        "grid-glow":
          "linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)",
        "gold-radial":
          "radial-gradient(circle at 50% 0%, rgba(233,196,106,0.18), transparent 60%)",
        "emerald-radial":
          "radial-gradient(circle at 80% 20%, rgba(18,185,129,0.14), transparent 55%)",
      },
      boxShadow: {
        glow: "0 0 40px -8px rgba(233,196,106,0.45)",
        "glow-emerald": "0 0 40px -8px rgba(18,185,129,0.45)",
        card: "0 24px 60px -20px rgba(0,0,0,0.7)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-14px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        "gradient-pan": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.25s ease-out",
        "accordion-up": "accordion-up 0.25s ease-out",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 3s linear infinite",
        "pulse-glow": "pulse-glow 3s ease-in-out infinite",
        marquee: "marquee 40s linear infinite",
        "gradient-pan": "gradient-pan 8s ease infinite",
      },
    },
  },
  plugins: [],
};

export default config;
