'use client'

import { motion, useReducedMotion } from 'framer-motion'

export function LivingBackground() {
  const prefersReducedMotion = useReducedMotion()

  return (
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="living-cosmos absolute inset-0" />
      <motion.div
        animate={prefersReducedMotion ? undefined : { x: ['-6%', '6%', '-6%'], y: ['-4%', '4%', '-4%'] }}
        transition={{ duration: 24, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
        className="nebula-band nebula-band-a absolute left-[-10%] top-[8%] h-[32rem] w-[32rem]"
      />
      <motion.div
        animate={prefersReducedMotion ? undefined : { x: ['8%', '-8%', '8%'], y: ['5%', '-6%', '5%'] }}
        transition={{ duration: 30, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
        className="nebula-band nebula-band-b absolute right-[-12%] top-[18%] h-[34rem] w-[34rem]"
      />
      <motion.div
        animate={prefersReducedMotion ? undefined : { scale: [1, 1.08, 1], opacity: [0.45, 0.7, 0.45] }}
        transition={{ duration: 16, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
        className="nebula-band nebula-band-c absolute bottom-[-12%] left-[18%] h-[30rem] w-[30rem]"
      />
      <div className="cosmic-grid-drift absolute inset-0 opacity-30" />
      <div className="starfield starfield-drift absolute inset-0 opacity-60" />
    </div>
  )
}
