/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cyber: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e"
        },
        neon: {
          green: "#00ff41",
          blue: "#00d4ff",
          purple: "#b700ff",
          pink: "#ff00e5",
          red: "#ff0040"
        }
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        glow: "glow 2s ease-in-out infinite alternate",
        float: "float 6s ease-in-out infinite"
      },
      keyframes: {
        glow: {
          "0%": { boxShadow: "0 0 5px #00ff41, 0 0 10px #00ff41, 0 0 15px #00ff41" },
          "100%": { boxShadow: "0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41" }
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" }
        }
      },
      backgroundImage: {
        "cyber-grid": "linear-gradient(rgba(0,255,65,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,65,0.1) 1px, transparent 1px)"
      }
    }
  },
  plugins: []
};
