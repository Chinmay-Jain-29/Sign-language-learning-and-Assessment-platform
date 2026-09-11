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
          50: '#F0F9FF',
          100: '#E0F2FE',
          500: '#0284C7',
          600: '#0284C7',
          700: '#0369A1',
          900: '#0C4A6E',
        },
        slate: {
          850: '#111827',
          950: '#0B0F19'
        }
      }
    },
  },
  plugins: [],
}
