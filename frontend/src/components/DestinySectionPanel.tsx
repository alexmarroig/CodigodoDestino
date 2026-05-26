'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

import type { DestinySection } from '@/types/mapa'

type DestinySectionPanelProps = {
  section: DestinySection
}

const CERTAINTY_TONE: Record<DestinySection['certainty_level'], 'muted' | 'soft' | 'warm'> = {
  chance: 'muted',
  tendency: 'soft',
  must: 'warm',
  will: 'warm',
}

export function DestinySectionPanel({ section }: DestinySectionPanelProps) {
  const [expanded, setExpanded] = useState(false)
  const [showEvidence, setShowEvidence] = useState(false)
  const tone = CERTAINTY_TONE[section.certainty_level] ?? 'soft'

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      className="cosmic-shell rounded-[32px] px-6 py-7 sm:px-8 sm:py-8"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">{section.title}</p>
          <h3 className="text-2xl font-semibold sm:text-3xl">{section.summary}</h3>
        </div>
        <Badge tone={tone}>{section.certainty_label}</Badge>
      </div>

      <div className="mt-5 space-y-4 text-sm leading-relaxed text-[var(--fg)] sm:text-base">
        <p className="whitespace-pre-line">{expanded ? section.body : truncateBody(section.body)}</p>
        {section.body.length > 420 ? (
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            className="text-xs uppercase tracking-[0.2em] text-[var(--muted-soft)] transition hover:text-[var(--fg)]"
          >
            {expanded ? 'Ver menos' : 'Ler mais'}
          </button>
        ) : null}
      </div>

      {section.evidence.length ? (
        <div className="mt-6 border-t border-[var(--line)] pt-4">
          <button
            type="button"
            onClick={() => setShowEvidence((current) => !current)}
            className="text-xs uppercase tracking-[0.2em] text-[var(--muted-soft)] transition hover:text-[var(--fg)]"
          >
            {showEvidence ? 'Ocultar' : 'Como o mapa chegou aqui'}
          </button>
          {showEvidence ? (
            <ul className="mt-3 space-y-2 text-sm text-[var(--muted)]">
              {section.evidence.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </motion.article>
  )
}

function truncateBody(body: string) {
  if (body.length <= 420) {
    return body
  }
  return `${body.slice(0, 417).trim()}…`
}

function Badge({ children, tone }: { children: string; tone: 'muted' | 'soft' | 'warm' }) {
  const classes = {
    muted: 'border-white/10 bg-white/5 text-[var(--muted)]',
    soft: 'border-[var(--line)] bg-white/8 text-[var(--fg)]',
    warm: 'border-[rgba(241,212,162,0.35)] bg-[rgba(241,212,162,0.12)] text-[var(--accent)]',
  }
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${classes[tone]}`}>
      {children}
    </span>
  )
}
