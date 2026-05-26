'use client'

import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'

import { DestinySectionPanel } from '@/components/DestinySectionPanel'
import type { DestinySection, MapaResponse } from '@/types/mapa'

type DestinyReadingProps = {
  result: MapaResponse
  onRestart: () => void
}

const FALLBACK_SECTIONS: Array<{ id: DestinySection['id']; title: string; order: number }> = [
  { id: 'central_reading', title: 'Leitura central', order: 1 },
  { id: 'personality', title: 'Personalidade real', order: 2 },
  { id: 'core_wound', title: 'Ferida principal', order: 3 },
  { id: 'emotional_pattern', title: 'Padrão emocional', order: 4 },
  { id: 'relationships', title: 'Relações', order: 5 },
  { id: 'family', title: 'Família', order: 6 },
  { id: 'money', title: 'Dinheiro', order: 7 },
  { id: 'career', title: 'Carreira', order: 8 },
  { id: 'life_timeline', title: 'Linha temporal', order: 9 },
  { id: 'future_events', title: 'Eventos futuros', order: 10 },
  { id: 'critical_cycles', title: 'Ciclos críticos', order: 11 },
  { id: 'conclusion', title: 'Conclusão final', order: 12 },
]

export function DestinyReading({ result, onRestart }: DestinyReadingProps) {
  const quality = result.profile_quality
  const confidence = result.confidence
  const sections = useMemo(() => {
    const fromApi = [...(result.destiny_sections ?? [])].sort((a, b) => a.order - b.order)
    if (fromApi.length >= 12) {
      return fromApi
    }
    return fromApi
  }, [result.destiny_sections])

  const [activeId, setActiveId] = useState(sections[0]?.id ?? 'central_reading')
  const activeSection = sections.find((section) => section.id === activeId) ?? sections[0]

  if (!sections.length) {
    return (
      <section id="reading-stage" className="cosmic-shell-strong rounded-[36px] px-6 py-10 text-center sm:px-10">
        <p className="text-sm text-[var(--muted)]">A leitura ainda está sendo gerada. Tente novamente em instantes.</p>
        <button type="button" onClick={onRestart} className="ritual-button mt-6 rounded-full px-6 py-3 text-sm font-semibold">
          Nova leitura
        </button>
      </section>
    )
  }

  return (
    <section id="reading-stage" className="space-y-6">
      <motion.header
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="cosmic-shell-strong rounded-[36px] px-6 py-7 sm:px-9 sm:py-8"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            <HeaderBadge>{`Precisão ${quality.code}`}</HeaderBadge>
            <HeaderBadge>{`Confiança ${Math.round(confidence.score * 100)}%`}</HeaderBadge>
          </div>
          <button type="button" onClick={onRestart} className="ritual-button-muted rounded-full px-5 py-3 text-sm font-semibold">
            Nova leitura
          </button>
        </div>
        <div className="mt-5 space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Sua narrativa de destino</p>
          <h2 className="text-3xl font-semibold sm:text-4xl">Doze leituras. Um só fio.</h2>
          <p className="max-w-2xl text-sm text-[var(--muted)] sm:text-base">
            Linguagem direta sobre o que tende a acontecer na sua vida — sem blá-blá técnico na superfície.
          </p>
        </div>
      </motion.header>

      <div className="grid gap-6 lg:grid-cols-[240px,1fr]">
        <nav className="cosmic-shell rounded-[28px] p-3 lg:sticky lg:top-6 lg:self-start">
          <p className="mb-3 px-2 text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">Seções</p>
          <div className="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
            {(sections.length ? sections : FALLBACK_SECTIONS).map((section) => {
              const isActive = section.id === activeId
              return (
                <button
                  key={section.id}
                  type="button"
                  onClick={() => setActiveId(section.id)}
                  className={`shrink-0 rounded-2xl px-3 py-2.5 text-left text-sm transition lg:w-full ${
                    isActive
                      ? 'bg-[rgba(241,212,162,0.14)] font-semibold text-[var(--accent)]'
                      : 'text-[var(--muted)] hover:bg-white/5 hover:text-[var(--fg)]'
                  }`}
                >
                  {section.title}
                </button>
              )
            })}
          </div>
        </nav>

        <div className="min-w-0">
          {activeSection ? <DestinySectionPanel section={activeSection} /> : null}
        </div>
      </div>
    </section>
  )
}

function HeaderBadge({ children }: { children: string }) {
  return (
    <span className="inline-flex rounded-full border border-[var(--line)] bg-white/5 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--muted)]">
      {children}
    </span>
  )
}
