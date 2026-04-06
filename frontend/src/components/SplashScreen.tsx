'use client'

import { useEffect, useState } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'

import { BrandOrb } from '@/components/BrandOrb'

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
          <div className="living-cosmos absolute inset-0" />
          <div className="starfield starfield-drift absolute inset-0 opacity-70" />

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: prefersReducedMotion ? 0.24 : 0.68, delay: 0.12 }}
            className="relative flex h-full flex-col items-center justify-center px-6 text-center"
          >
            <BrandOrb size="splash" />
            <p className="mt-8 text-xs uppercase tracking-[0.5em] text-[var(--muted-soft)]">Codigo do Destino</p>
            <h1 className="mt-5 max-w-4xl text-balance text-5xl font-semibold leading-[0.88] text-[var(--fg)] sm:text-7xl">
              A esfera esta abrindo o seu mapa.
            </h1>
            <p className="mt-4 max-w-2xl text-sm text-[var(--muted)] sm:text-base">
              Uma leitura em movimento, com tempo, atmosferas e pontos de virada.
            </p>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
