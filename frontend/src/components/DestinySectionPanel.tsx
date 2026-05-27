'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

import type { AstroProvenance, DestinySection } from '@/types/mapa'

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
  return <p className="whitespace-pre-line">{stripMarkdown(display)}</p>
}

function ProvenancePanel({ provenance }: { provenance: AstroProvenance }) {
  const timing = provenance.timing
  const longCycle = timing?.mode === 'tema_no_periodo'

  return (
    <div className="space-y-4 rounded-2xl border border-[var(--line)] bg-white/[0.03] p-4 text-sm">
      {longCycle ? (
        <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted-soft)]">
          Ciclo longo — sem data exata fechada
        </p>
      ) : null}

      {provenance.primary_drivers?.length ? (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted-soft)]">
            Drivers principais
          </p>
          <ul className="space-y-2">
            {provenance.primary_drivers.map((driver, index) => (
              <li key={`${driver.label}-${index}`} className="leading-relaxed">
                <span className="text-[var(--fg)]">
                  {index + 1}. [{driver.technique}] {stripMarkdown(driver.label)}
                </span>
                {driver.orb_degrees != null ? (
                  <span className="text-[var(--muted)]"> — orbe {Number(driver.orb_degrees).toFixed(2)}°</span>
                ) : null}
                {driver.brady_line ? (
                  <p className="mt-1 text-[var(--muted)]">{stripMarkdown(driver.brady_line)}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {provenance.supporting_techniques?.length ? (
        <p className="text-[var(--muted)]">
          <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted-soft)]">
            Técnicas:{' '}
          </span>
          {provenance.supporting_techniques.join(', ')}
        </p>
      ) : null}

      {provenance.dignity_note ? (
        <p className="text-[var(--muted)]">
          <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted-soft)]">
            Dignidade:{' '}
          </span>
          {stripMarkdown(provenance.dignity_note)}
        </p>
      ) : null}

      {provenance.excluded?.length ? (
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted-soft)]">
            Sinais não usados como causa principal
          </p>
          <ul className="space-y-1 text-[var(--muted)]">
            {provenance.excluded.map((item) => (
              <li key={item}>• {stripMarkdown(item)}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {provenance.confidence_caps?.length ? (
        <div className="border-t border-[var(--line)] pt-3">
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted-soft)]">
            Limites de interpretação
          </p>
          <ul className="space-y-1 text-xs text-[var(--muted)]">
            {provenance.confidence_caps.map((cap) => (
              <li key={cap}>• {stripMarkdown(cap)}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  )
}

export function DestinySectionPanel({ section }: DestinySectionPanelProps) {
  const [expanded, setExpanded] = useState(false)
  const [showTechnical, setShowTechnical] = useState(false)
  const tone = CERTAINTY_TONE[section.certainty_level] ?? 'soft'

  const hasTechnical = !!(
    section.technical_detail?.trim() ||
    section.evidence.length ||
    section.astro_provenance
  )

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
              {section.astro_provenance ? (
                <ProvenancePanel provenance={section.astro_provenance} />
              ) : null}
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
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${classes[tone]}`}
    >
      {children}
    </span>
  )
}
