/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Greyscale base
        background: '#0a0a0f',
        surface: '#14141c',
        surfaceLight: '#1e1e2a',
        border: '#2a2a35',
        textPrimary: '#f0f0f5',
        textSecondary: '#a0a0b0',
        // Blue & green accents
        primary: '#2b6ef0',
        primaryDark: '#1e4fbc',
        secondary: '#10b981',
        secondaryDark: '#0d9488',
        accent: '#3b82f6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}