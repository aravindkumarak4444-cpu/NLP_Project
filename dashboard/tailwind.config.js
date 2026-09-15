/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        oil: {
          dark: '#0f172a',
          navy: '#1e293b',
          blue: '#0284c7',
          amber: '#d97706',
          green: '#16a34a',
          red: '#dc2626',
        },
        risk: {
          critical: '#b91c1c',
          high: '#c2410c',
          medium: '#b45309',
          low: '#15803d',
        }
      }
    },
  },
  plugins: [],
}
