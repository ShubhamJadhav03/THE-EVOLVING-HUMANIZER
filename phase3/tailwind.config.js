/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb"
        }
      },
      boxShadow: {
        glass: "0 10px 30px rgba(2,6,23,0.6), inset 0 1px 0 rgba(255,255,255,0.02)"
      },
      borderRadius: {
        xl2: "16px",
      }
    }
  },
  plugins: []
};



