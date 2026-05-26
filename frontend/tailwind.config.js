/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0d12",
        panel: "#141821",
        panel2: "#1b212d",
        border: "#252b39",
        muted: "#8a93a6",
        text: "#e6e9ef",
        gain: "#22c55e",
        loss: "#ef4444",
        accent: "#60a5fa",
      },
    },
  },
  plugins: [],
};
