/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        fm: {
          green: "#23392E",
          "green-deep": "#17261F",
          cream: "#EFE8D8",
          rust: "#C1602B",
          line: "rgba(35,57,46,0.22)",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        slab: ["var(--font-slab)", "serif"],
        body: ["var(--font-body)", "sans-serif"],
      },
    },
  },
  plugins: [],
};
