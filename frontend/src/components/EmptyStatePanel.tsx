'use client'

import { motion } from 'framer-motion'

type EmptyStatePanelProps = {
  onPrimaryAction: () => void
}

const EMPTY_PROMISES = [
  'Mapa astrológico real com signos, casas e ângulos.',
  'Eventos ranqueados por intensidade, confiança e timing.',
  'Narrativa final com acabamento editorial e telemetria da engine.',
]

export function EmptyStatePanel({ onPrimaryAction }: EmptyStatePanelProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.36, ease: 'easeOut' }}
      className="cinematic-panel relative overflow-hidden rounded-[40px] px-7 py-8 sm:px-10 sm:py-10"
    >
      <div className="pointer-events-none absolute inset-0 bg-aurora opacity-75" />
      <div className="pointer-events-none absolute inset-y-0 right-0 hidden w-[38%] bg-[linear-gradient(270deg,rgba(255,255,255,0.08),transparent)] xl:block" />
      <div className="relative grid gap-8 xl:grid-cols-[1.08fr,0.92fr] xl:items-end">
        <div className="space-y-5">
          <p className="text-xs font-semibold uppercase tracking-[0.34em] text-[var(--muted-soft)]">
            Output workspace
          </p>
          <div className="space-y-4">
            <h2 className="max-w-3xl text-4xl font-semibold leading-[0.92] tracking-[-0.05em] sm:text-5xl">
              A leitura ainda está silenciosa. O palco abre quando você envia a origem do mapa.
            </h2>
            <p className="max-w-2xl text-base text-[var(--muted)] sm:text-lg">
              Preencha o formulário para transformar data, hora e coordenadas em um panorama técnico com narrativa final.
            </p>
          </div>
          <motion.button
            type="button"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.985 }}
            onClick={onPrimaryAction}
            className="inline-flex items-center justify-center rounded-full bg-[var(--fg)] px-6 py-3 text-sm font-semibold text-[var(--bg)] shadow-[var(--shadow-soft)] transition hover:opacity-95"
          >
            Abrir o formulário
          </motion.button>
        </div>

        <div className="grid gap-3">
          {EMPTY_PROMISES.map((item, index) => (
            <motion.div
              key={item}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.08 * index }}
              className="surface-muted rounded-[28px] px-5 py-5"
            >
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--muted-soft)]">
                Track {index + 1}
              </p>
              <p className="mt-3 text-sm text-[var(--fg)]">{item}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.section>
  )
}
