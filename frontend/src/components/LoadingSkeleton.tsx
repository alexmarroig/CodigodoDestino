'use client'

import { motion } from 'framer-motion'

export function LoadingSkeleton() {
  return (
    <section className="cosmic-shell-strong relative overflow-hidden rounded-[40px] px-6 py-16 text-center sm:px-10 sm:py-24">
      <div className="aurora-field absolute inset-0 opacity-90" />
      <div className="starfield absolute inset-0 opacity-55" />

      <div className="relative flex flex-col items-center">
        <div className="relative mb-10 h-44 w-44">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 12, ease: 'linear', repeat: Number.POSITIVE_INFINITY }}
            className="absolute inset-0 rounded-full border border-[var(--line)]"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 18, ease: 'linear', repeat: Number.POSITIVE_INFINITY }}
            className="absolute inset-[18px] rounded-full border border-[rgba(241,212,162,0.18)]"
          />
          <motion.div
            animate={{ scale: [0.96, 1.05, 0.96], opacity: [0.5, 0.9, 0.5] }}
            transition={{ duration: 2.8, ease: 'easeInOut', repeat: Number.POSITIVE_INFINITY }}
            className="absolute left-1/2 top-1/2 h-20 w-20 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(241,212,162,0.3),transparent_68%)]"
          />
        </div>

        <p className="text-xs uppercase tracking-[0.42em] text-[var(--muted-soft)]">Leitura em andamento</p>
        <h2 className="mt-5 text-4xl font-semibold leading-[0.92] sm:text-6xl">Analisando seu padrao...</h2>
        <p className="mt-5 max-w-2xl text-base text-[var(--muted)] sm:text-lg">
          Estamos reunindo os sinais mais fortes do seu momento para abrir a sua leitura com calma.
        </p>
      </div>
    </section>
  )
}
