import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-body)'],
        display: ['var(--font-display)'],
      },
      boxShadow: {
        halo: '0 0 0 1px rgba(255,255,255,0.08), 0 24px 80px rgba(0,0,0,0.35)',
      },
      backgroundImage: {
        aurora:
          'radial-gradient(circle at top, rgba(125, 211, 252, 0.2), transparent 30%), radial-gradient(circle at 80% 20%, rgba(129, 140, 248, 0.2), transparent 22%), radial-gradient(circle at 50% 80%, rgba(244, 114, 182, 0.14), transparent 26%)',
      },
    },
  },
  plugins: [],
}

export default config
