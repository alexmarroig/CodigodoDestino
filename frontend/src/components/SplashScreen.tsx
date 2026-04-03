'use client'

import { useEffect, useState } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'

const SPLASH_MS = 1450
const SPLASH_REDUCED_MS = 620

export function SplashScreen() {
  const prefersReducedMotion = useReducedMotion()
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setVisible(false)
    }, prefersReducedMotion ? SPLASH_REDUCED_MS : SPLASH_MS)

    return () => {
      window.clearTimeout(timeout)
    }
  }, [prefersReducedMotion])

  return (
    <AnimatePresence>
      {visible ? (
        <motion.div
          key="splash-screen"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, transition: { duration: prefersReducedMotion ? 0.2 : 0.5, ease: 'easeOut' } }}
          className="fixed inset-0 z-[70] overflow-hidden bg-[var(--bg)]"
          aria-hidden="true"
        >
          <div className="aurora-field absolute inset-0" />
          <div className="starfield absolute inset-0" />

          <motion.div
            animate={prefersReducedMotion ? undefined : { rotate: 360 }}
            transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
            className="absolute left-1/2 top-1/2 h-[30rem] w-[30rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--line)]"
          />
          <motion.div
            initial={{ scale: 0.88, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: prefersReducedMotion ? 0.28 : 0.75, ease: [0.22, 1, 0.36, 1] }}
            className="absolute left-1/2 top-1/2 h-[24rem] w-[24rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(241,212,162,0.13),transparent_64%)]"
          />

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: prefersReducedMotion ? 0.24 : 0.68, delay: 0.12 }}
            className="relative flex h-full flex-col items-center justify-center px-6 text-center"
          >
            <p className="text-xs uppercase tracking-[0.5em] text-[var(--muted-soft)]">Codigo do Destino</p>
            <h1 className="mt-6 max-w-3xl text-5xl font-semibold leading-[0.88] text-[var(--fg)] sm:text-7xl">
              Sua leitura esta prestes a se abrir.
            </h1>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
