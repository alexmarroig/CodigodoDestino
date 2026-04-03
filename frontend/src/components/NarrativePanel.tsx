'use client'

import { motion } from 'framer-motion'

type NarrativePanelProps = {
  narrative: {
    text: string
    strategy: string
    requested_strategy?: string
    strategy_reason: string
    complexity_score: number
    prompt_event_count: number
    model: string
  }
}

export function NarrativePanel({ narrative }: NarrativePanelProps) {
  const curationLabel =
    narrative.strategy === narrative.requested_strategy || !narrative.requested_strategy
      ? narrative.strategy_reason
      : `${narrative.requested_strategy} -> ${narrative.strategy_reason}`

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="cinematic-panel relative overflow-hidden rounded-[38px] px-7 py-8 sm:px-9 sm:py-10"
    >
      <div className="pointer-events-none absolute inset-0 bg-aurora opacity-75" />
      <div className="pointer-events-none absolute inset-y-0 right-0 hidden w-[34%] bg-[linear-gradient(270deg,rgba(255,255,255,0.06),transparent)] xl:block" />

      <div className="relative grid gap-8 xl:grid-cols-[1.08fr,0.92fr] xl:items-end">
        <div className="space-y-6">
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--muted-soft)]">
              Narrative engine
            </p>
            <h2 className="max-w-3xl text-4xl font-semibold leading-[0.92] tracking-[-0.05em] sm:text-5xl">
              A síntese final entra como leitura, não como relatório.
            </h2>
          </div>

          <p className="max-w-4xl text-base leading-8 text-[var(--fg)] sm:text-[1.08rem] sm:leading-8">
            {narrative.text}
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          <MetaPill label="Strategy" value={narrative.strategy} />
          <MetaPill label="Modelo" value={narrative.model} />
          <MetaPill label="Complexidade" value={String(narrative.complexity_score)} />
          <MetaPill label="Eventos no prompt" value={String(narrative.prompt_event_count)} />
          <MetaPill label="Curadoria" value={curationLabel} className="sm:col-span-2 xl:col-span-1" />
        </div>
      </div>
    </motion.section>
  )
}

function MetaPill({
  label,
  value,
  className = '',
}: {
  label: string
  value: string
  className?: string
}) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.18 }}
      className={`surface-muted rounded-[24px] px-4 py-4 ${className}`}
    >
      <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--muted-soft)]">{label}</p>
      <p className="mt-2 text-sm font-medium text-[var(--fg)]">{value}</p>
    </motion.div>
  )
}
