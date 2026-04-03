'use client'

import { motion } from 'framer-motion'

import { ForecastEvent } from '@/types/mapa'

const intensityTone: Record<ForecastEvent['intensity'], string> = {
  high: 'text-[var(--danger)]',
  medium: 'text-[var(--warning)]',
  low: 'text-[var(--success)]',
}

const intensityAccent: Record<ForecastEvent['intensity'], string> = {
  high: 'bg-[var(--danger)]',
  medium: 'bg-[var(--warning)]',
  low: 'bg-[var(--success)]',
}

export function Timeline({ events }: { events: ForecastEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-[28px] border border-dashed border-[var(--line-strong)] px-5 py-6 text-sm text-[var(--muted)]">
        Nenhum evento priorizado para esta leitura.
      </div>
    )
  }

  return (
    <div className="content-auto space-y-4">
      {events.map((event, index) => (
        <motion.article
          key={event.id}
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          whileHover={{ y: -4 }}
          transition={{ duration: 0.4, delay: 0.06 * index }}
          className="relative overflow-hidden rounded-[30px] border border-[var(--line)] bg-[var(--bg-elevated)] p-6"
        >
          <div className={`absolute left-0 top-0 h-full w-1 ${intensityAccent[event.intensity]}`} />

          <div className="flex flex-wrap items-start justify-between gap-5">
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full bg-[var(--accent-soft)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
                  #{event.rank ?? index + 1}
                </span>
                <span className="rounded-full border border-[var(--line)] px-3 py-1 text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--muted)]">
                  {event.category}
                </span>
                <span className="rounded-full border border-[var(--line)] px-3 py-1 text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--muted)]">
                  {event.type}
                </span>
              </div>

              <div>
                <h3 className="text-2xl font-semibold leading-tight text-[var(--fg)]">{event.title}</h3>
                <p className="mt-3 max-w-3xl text-sm text-[var(--muted)] sm:text-base">{event.summary}</p>
              </div>
            </div>

            <div className="grid min-w-[12rem] gap-2 text-sm sm:text-right">
              <p className={`text-xs font-semibold uppercase tracking-[0.26em] ${intensityTone[event.intensity]}`}>
                {event.intensity}
              </p>
              <p className="text-[var(--muted)]">Prioridade {event.priority}</p>
              <p className="text-[var(--muted)]">Score {event.score.toFixed(2)}</p>
              <p className="text-[var(--muted)]">Confianca {Math.round(event.confidence * 100)}%</p>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            {event.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full border border-[var(--line)] px-3 py-1 text-xs text-[var(--muted)]"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-6 grid gap-3 lg:grid-cols-3">
            <MetricBlock
              label="Janela temporal"
              value={`${event.time_window.start} ate ${event.time_window.end}`}
              extra={event.time_window.peak ? `Pico em ${event.time_window.peak}` : undefined}
            />
            <MetricBlock
              label="Drivers"
              value={event.drivers.slice(0, 2).map((driver) => driver.code).join(' | ') || 'Sem drivers resumidos'}
              extra={`${event.drivers.length} sinais conectados`}
            />
            <MetricBlock
              label="Recommendations"
              value={event.recommendations.slice(0, 2).join(' | ') || 'Sem recomendacoes'}
            />
          </div>
        </motion.article>
      ))}
    </div>
  )
}

function MetricBlock({
  label,
  value,
  extra,
}: {
  label: string
  value: string
  extra?: string
}) {
  return (
    <div className="rounded-[24px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4">
      <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--muted-soft)]">{label}</p>
      <p className="mt-2 text-sm font-medium text-[var(--fg)]">{value}</p>
      {extra ? <p className="mt-2 text-xs text-[var(--muted)]">{extra}</p> : null}
    </div>
  )
}
