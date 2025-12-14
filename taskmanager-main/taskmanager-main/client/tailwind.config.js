/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        main: {
          DEFAULT: '#441662',
          hover: '#F57A6A',
        },
        background: '#f3f4f6',
      },
      animation: {
        'rotate-in-up-left': 'rotate-in-up-left 2s ease infinite',
        'pulse': 'pulse 1.5s infinite ease-in-out',
      },
      keyframes: {
        'rotate-in-up-left': {
          '0%': {
            transformOrigin: 'left bottom',
            transform: 'rotate(90deg)',
            opacity: '0',
          },
          '100%': {
            transformOrigin: 'left bottom',
            transform: 'rotate(0)',
            opacity: '1',
          },
        },
        'pulse': {
          '0%, 100%': {
            transform: 'scale(0.8)',
            backgroundColor: '#441662',
            boxShadow: '0 0 0 0 rgba(68, 22, 98, 0.4)',
          },
          '50%': {
            transform: 'scale(1.2)',
            backgroundColor: '#F57A6A',
            boxShadow: '0 0 0 10px rgba(245, 122, 106, 0)',
          },
        },
      },
    },
  },
  plugins: [],
}