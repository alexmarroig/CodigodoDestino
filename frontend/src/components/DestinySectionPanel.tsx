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

/** Strip raw markdown bold markers (**text**) returning plain text. */
function stripMarkdown(text: string): string {
  return text.replace(/\*\*([^*]+)\*\*/g, '$1')
}

/** Render body text with newlines and stripped markdown. */
function BodyText({ text, full }: { text: string; full: boolean }) {
  const display = full ? text : truncateBody(text)
  return (
    <p className="whitespace-pre-line">{stripMarkdown(display)}</p>
  )
}

export function DestinySectionPanel({ section }: DestinySectionPanelProps) {
  const [expanded, setExpanded] = useState(false)
  const [showTechnical, setShowTechnical] = useState(false)
  const tone = CERTAINTY_TONE[section.certainty_level] ?? 'soft'

  const hasTechnical = !!(section.technical_detail?.trim() || section.evidence.length)

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
          <h3 className="text-2xl font-semibold sm:text-3xl">{stripMarkdown(section.summary)}</h3>
        </div>
        <Badge tone={tone}>{section.certainty_label}</Badge>
      </div>

      <div className="mt-5 space-y-4 text-sm leading-relaxed text-[var(--fg)] sm:text-base">
        <BodyText text={section.body} full={expanded} />
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

      {hasTechnical ? (
        <div className="mt-6 border-t border-[var(--line)] pt-4">
          <button
            type="button"
            onClick={() => setShowTechnical((current) => !current)}
            className="text-xs uppercase tracking-[0.2em] text-[var(--muted-soft)] transition hover:text-[var(--fg)]"
          >
            {showTechnical ? 'Ocultar' : 'Como o mapa chegou aqui'}
          </button>
          {showTechnical ? (
            <div className="mt-3 space-y-3 text-sm text-[var(--muted)]">
              {section.technical_detail?.trim() ? (
                <p className="whitespace-pre-line leading-relaxed">
                  {stripMarkdown(section.technical_detail)}
                </p>
              ) : null}
              {section.evidence.length ? (
                <ul className="mt-2 space-y-1">
                  {section.evidence.map((item) => (
                    <li key={item}>• {stripMarkdown(item)}</li>
                  ))}
                </ul>
              ) : null}
            </div>
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
