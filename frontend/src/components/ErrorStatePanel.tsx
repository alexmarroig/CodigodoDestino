'use client'

import { motion } from 'framer-motion'

type ErrorStatePanelProps = {
  message: string
  onRetry?: () => void
  onReviewInputs: () => void
  compact?: boolean
  reviewLabel?: string
}

export function ErrorStatePanel({
  message,
  onRetry,
  onReviewInputs,
  compact = false,
  reviewLabel = 'Voltar aos passos',
}: ErrorStatePanelProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`cosmic-shell relative overflow-hidden rounded-[34px] px-6 ${
        compact ? 'py-6' : 'py-8 sm:px-8 sm:py-10'
      }`}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,140,164,0.12),transparent_34%)]" />

      <div className="relative space-y-6">
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.36em] text-[var(--muted-soft)]">A leitura foi interrompida</p>
          <h2 className={`${compact ? 'text-2xl' : 'text-4xl sm:text-5xl'} font-semibold leading-[0.92]`}>
            Nao consegui terminar essa passagem agora.
          </h2>
          <p className="max-w-2xl text-sm text-[var(--muted)] sm:text-base">{message}</p>
        </div>

        <div className="flex flex-wrap gap-3">
          {onRetry ? (
            <motion.button
              type="button"
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.985 }}
              onClick={onRetry}
              className="ritual-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
            >
              Tentar novamente
            </motion.button>
          ) : null}
          <motion.button
            type="button"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.985 }}
            onClick={onReviewInputs}
            className="ritual-button-muted inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
          >
            {reviewLabel}
          </motion.button>
        </div>
      </div>
    </motion.section>
  )
}
