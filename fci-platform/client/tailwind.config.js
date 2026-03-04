/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        surface: {
          950: '#0B0E11',
          900: '#12161C',
          850: '#181C23',
          800: '#1E2329',
          750: '#252A31',
          700: '#2E3440',
          600: '#474D57',
          500: '#6A7282',
          400: '#8B95A5',
          300: '#AEB7C4',
          200: '#D1D6DD',
          100: '#EAECEF',
          50:  '#F5F6F7',
        },
        gold: {
          950: '#2D2305',
          900: '#4A3A08',
          800: '#6B540C',
          700: '#8C6E10',
          600: '#B08B14',
          500: '#F0B90B',
          400: '#F5C842',
          300: '#F8D66F',
          200: '#FBE59D',
          100: '#FDF2CE',
          50:  '#FFFBEB',
        },
      },
      boxShadow: {
        'soft-sm':    '0 1px 2px rgba(0, 0, 0, 0.2), 0 1px 3px rgba(0, 0, 0, 0.15)',
        'soft':       '0 2px 8px rgba(0, 0, 0, 0.25), 0 4px 12px rgba(0, 0, 0, 0.15)',
        'soft-lg':    '0 4px 16px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.18)',
        'soft-xl':    '0 8px 32px rgba(0, 0, 0, 0.35), 0 16px 48px rgba(0, 0, 0, 0.2)',
        'glow-gold':  '0 0 20px -4px rgba(240, 185, 11, 0.3)',
        'glow-gold-lg': '0 0 32px -4px rgba(240, 185, 11, 0.4)',
      },
    },
  },
  plugins: [],
};
