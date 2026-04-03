'use client'

import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

type Theme = 'dark' | 'light'

function resolveTheme(): Theme {
  if (typeof window === 'undefined') {
    return 'dark'
  }

  const stored = window.localStorage.getItem('codigodestino-theme')
  if (stored === 'dark' || stored === 'light') {
    return stored
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark')
  document.documentElement.dataset.theme = theme
  window.localStorage.setItem('codigodestino-theme', theme)
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('dark')

  useEffect(() => {
    const nextTheme = resolveTheme()
    setTheme(nextTheme)
    applyTheme(nextTheme)
  }, [])

  function toggleTheme() {
    const nextTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(nextTheme)
    applyTheme(nextTheme)
  }

  return (
    <motion.button
      type="button"
      onClick={toggleTheme}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.985 }}
      className="surface-muted relative inline-flex h-12 items-center gap-3 rounded-full px-3.5 text-sm font-semibold text-[var(--fg)] transition hover:border-[var(--line-strong)]"
      aria-label="Alternar tema"
      aria-pressed={theme === 'dark'}
    >
      <span className="relative flex h-6 w-11 items-center rounded-full bg-[var(--accent-soft)]">
        <motion.span
          layout
          transition={{ type: 'spring', stiffness: 420, damping: 30 }}
          className="absolute left-0.5 h-5 w-5 rounded-full bg-[var(--accent)] shadow-[0_8px_24px_rgba(52,88,255,0.35)]"
          style={{ x: theme === 'dark' ? 20 : 0 }}
        />
      </span>

      <span className="hidden text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--muted-soft)] sm:block">
        Theme
      </span>

      <span className="relative h-5 min-w-[4.8rem] overflow-hidden text-left">
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={theme}
            initial={{ y: 8, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -8, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="block"
          >
            {theme === 'dark' ? 'Nocturne' : 'Daylight'}
          </motion.span>
        </AnimatePresence>
      </span>
    </motion.button>
  )
}
