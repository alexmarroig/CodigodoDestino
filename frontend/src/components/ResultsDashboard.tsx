'use client'

import type { ReactNode } from 'react'
import { motion } from 'framer-motion'

import { DomainAnalysisEntry, MapaResponse, Uncertainty } from '@/types/mapa'

type ResultsDashboardProps = {
  result: MapaResponse
  onRestart: () => void
}

export function ResultsDashboard({ result, onRestart }: ResultsDashboardProps) {
  const sunSign = result.computed.astrology.signs.sun?.sign ?? 'Sinal central em movimento'
  const moonSign = result.computed.astrology.signs.moon?.sign ?? 'Sensibilidade em movimento'
  const personalYear = result.computed.numerology.personal_year.value
  const topTags = result.event_summary.top_tags.slice(0, 3)
  const quality = result.profile_quality ??
    result.analysis?.profile_quality ?? {
      code: 'C' as const,
      label: 'horario desconhecido',
      birth_time_precision: 'unknown' as const,
      birth_time_window: null,
      effective_time: result.input.time ?? '12:00:00',
      assumptions: ['Esta resposta nao trouxe o bloco de qualidade do perfil.'],
      confidence_modifier: 0.58,
      can_use_houses: false,
      can_use_angles: false,
    }
  const confidence = result.confidence ??
    result.analysis?.domain_analysis?.confidence ?? {
      level: 'low' as const,
      score: 0.3,
      reason: 'A resposta nao trouxe o bloco de confianca consolidado.',
      profile_quality: quality.code,
    }
  const domains = result.analysis?.domain_analysis?.domains ?? []
  const uncertainties = result.uncertainties ?? result.analysis?.domain_analysis?.uncertainties ?? []
  const macroHouse = result.analysis?.profections?.activated_house

  return (
    <section id="reading-stage" className="space-y-10">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.42, ease: 'easeOut' }}
        className="cosmic-shell-strong relative overflow-hidden rounded-[40px] px-6 py-10 sm:px-10 sm:py-12"
      >
        <div className="aurora-field absolute inset-0 opacity-85" />

        <div className="relative grid gap-8 xl:grid-cols-[1.08fr,0.92fr]">
          <div className="space-y-5">
            <div className="flex flex-wrap gap-2">
              <Badge tone={quality.code === 'A' ? 'warm' : quality.code === 'B' ? 'soft' : 'muted'}>
                Precisao {quality.code}
              </Badge>
              <Badge tone={confidence.level === 'high' ? 'warm' : confidence.level === 'medium' ? 'soft' : 'muted'}>
                Confianca {confidence.level}
              </Badge>
              {macroHouse ? <Badge tone="muted">Tema anual casa {macroHouse}</Badge> : null}
            </div>

            <div className="space-y-4">
              <p className="text-xs uppercase tracking-[0.4em] text-[var(--muted-soft)]">Sua leitura esta aberta</p>
              <h2 className="max-w-4xl text-4xl font-semibold leading-[0.9] sm:text-6xl">
                O que esta convergindo agora na sua historia.
              </h2>
              <p className="max-w-2xl text-base text-[var(--muted)] sm:text-lg">
                O motor cruzou tecnicas diferentes e separou o que parece forte, o que ainda esta incerto e onde a sua
                leitura pede mais cautela.
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
            <InsightPill label="Sol" value={sunSign} />
            <InsightPill label="Lua" value={moonSign} />
            <InsightPill label="Ciclo pessoal" value={`Ano ${personalYear}`} />
            <InsightPill label="Palavras do momento" value={topTags.join(' | ') || 'Sinais se reorganizando'} />
          </div>
        </div>
      </motion.div>

      <section className="grid gap-5 xl:grid-cols-[0.92fr,1.08fr]">
        <ConfidencePanel result={result} />
        <UncertaintyPanel uncertainties={uncertainties} qualityAssumptions={quality.assumptions} />
      </section>

      <section className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Convergencias</p>
            <h3 className="text-3xl font-semibold sm:text-5xl">Dominios mais ativos</h3>
          </div>
          <motion.button
            type="button"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.985 }}
            onClick={onRestart}
            className="ritual-button-muted inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
          >
            Fazer outra leitura
          </motion.button>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          {domains.length === 0 ? (
            <div className="cosmic-shell rounded-[32px] px-6 py-8 text-sm text-[var(--muted)]">
              O motor ainda nao conseguiu formar um bloco forte de convergencia. A narrativa abaixo continua sendo a melhor
              porta para a leitura deste momento.
            </div>
          ) : (
            domains.slice(0, 4).map((domain, index) => (
              <DomainCard key={domain.domain} domain={domain} index={index} />
            ))
          )}
        </div>
      </section>

      <section className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Eventos fortes</p>
          <h3 className="text-3xl font-semibold sm:text-5xl">O que aparece agora</h3>
        </div>

        <div className="grid gap-4">
          {result.events.length === 0 ? (
            <div className="cosmic-shell rounded-[32px] px-6 py-8 text-sm text-[var(--muted)]">
              Os sinais estao mais silenciosos agora. A narrativa abaixo continua sendo a melhor porta para a sua leitura.
            </div>
          ) : (
            result.events.map((event, index) => (
              <motion.article
                key={event.id}
                initial={{ opacity: 0, y: 28 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.42, delay: 0.1 * index, ease: 'easeOut' }}
                className="cosmic-shell relative overflow-hidden rounded-[32px] px-6 py-6 sm:px-8"
              >
                <div className="absolute left-0 top-0 h-full w-1 bg-[linear-gradient(180deg,rgba(241,212,162,0.95),transparent)]" />

                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <Badge tone="muted">{normalizeLabel(event.category)}</Badge>
                    <Badge tone={event.intensity === 'high' ? 'warm' : 'soft'}>{event.intensity}</Badge>
                    <Badge tone="soft">{Math.round((event.probability ?? event.confidence) * 100)}%</Badge>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-2xl font-semibold text-[var(--fg)] sm:text-3xl">{event.title}</h4>
                    <p className="max-w-3xl text-sm text-[var(--muted)] sm:text-base">{event.summary}</p>
                  </div>

                  <div className="grid gap-3 lg:grid-cols-[0.9fr,1.1fr]">
                    <SoftCard
                      label="Janela"
                      value={`${formatDate(event.time_window.start)} ate ${formatDate(event.time_window.end)}`}
                    />
                    <SoftCard label="Causa principal" value={event.cause ?? event.narrative_hint ?? 'Sinais em reorganizacao.'} />
                  </div>

                  {event.signals?.length ? (
                    <div className="flex flex-wrap gap-2">
                      {event.signals.slice(0, 4).map((signal) => (
                        <span
                          key={signal}
                          className="rounded-full border border-[var(--line)] bg-white/5 px-3 py-1 text-xs text-[var(--muted)]"
                        >
                          {signal}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              </motion.article>
            ))
          )}
        </div>
      </section>

      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Narrativa</p>
          <h3 className="text-3xl font-semibold sm:text-5xl">Sua leitura completa</h3>
        </div>

        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.25, ease: 'easeOut' }}
          className="cosmic-shell-strong relative overflow-hidden rounded-[40px] px-6 py-10 sm:px-10 sm:py-12"
        >
          <div className="aurora-field absolute inset-0 opacity-80" />
          <div className="relative reading-copy max-w-4xl">{result.narrative.text}</div>
        </motion.section>
      </div>
    </section>
  )
}

function ConfidencePanel({ result }: { result: MapaResponse }) {
  const quality = result.profile_quality ??
    result.analysis?.profile_quality ?? {
      code: 'C' as const,
      label: 'horario desconhecido',
      birth_time_precision: 'unknown' as const,
      birth_time_window: null,
      effective_time: result.input.time ?? '12:00:00',
      assumptions: [],
      confidence_modifier: 0.58,
      can_use_houses: false,
      can_use_angles: false,
    }
  const confidence = result.confidence ??
    result.analysis?.domain_analysis?.confidence ?? {
      level: 'low' as const,
      score: 0.3,
      reason: 'A resposta nao trouxe o bloco de confianca consolidado.',
      profile_quality: quality.code,
    }
  const techniques = (result.techniques_used ?? result.analysis?.techniques_used ?? []).slice(0, 6)

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="cosmic-shell rounded-[34px] px-6 py-6 sm:px-8"
    >
      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Confianca da leitura</p>
          <h3 className="text-2xl font-semibold sm:text-3xl">Quao firme esta esta leitura</h3>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <MetricCard label="Precisao do nascimento" value={`${quality.code} · ${quality.label}`} />
          <MetricCard label="Confianca geral" value={`${Math.round(confidence.score * 100)}% · ${confidence.level}`} />
          <MetricCard label="Tecnicas ativas" value={String((result.techniques_used ?? result.analysis?.techniques_used ?? []).length)} />
        </div>

        <p className="text-sm text-[var(--muted)]">{confidence.reason}</p>

        <div className="flex flex-wrap gap-2">
          {techniques.map((technique) => (
            <Badge key={technique} tone="muted">
              {normalizeLabel(technique)}
            </Badge>
          ))}
        </div>
      </div>
    </motion.section>
  )
}

function UncertaintyPanel({
  uncertainties,
  qualityAssumptions,
}: {
  uncertainties: Uncertainty[]
  qualityAssumptions: string[]
}) {
  const notes = [...qualityAssumptions, ...uncertainties.map((item) => item.message)].slice(0, 3)

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.38, ease: 'easeOut', delay: 0.06 }}
      className="cosmic-shell rounded-[34px] px-6 py-6 sm:px-8"
    >
      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Zonas de cautela</p>
          <h3 className="text-2xl font-semibold sm:text-3xl">O que ainda nao esta fechado</h3>
        </div>

        {notes.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">
            Nesta leitura, os sinais ficaram relativamente coerentes. Ainda assim, vale observar a vida real antes de
            tomar qualquer interpretacao como definitiva.
          </p>
        ) : (
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note} className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4 text-sm text-[var(--muted)]">
                {note}
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.section>
  )
}

function DomainCard({ domain, index }: { domain: DomainAnalysisEntry; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.38, delay: 0.08 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[32px] px-6 py-6"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge tone={domain.converged ? 'warm' : 'muted'}>{domain.converged ? 'Convergente' : 'Em observacao'}</Badge>
          <Badge tone={domain.tone === 'challenging' ? 'soft' : domain.tone === 'supportive' ? 'warm' : 'muted'}>
            {domain.tone === 'challenging' ? 'Tensao' : domain.tone === 'supportive' ? 'Abertura' : 'Misto'}
          </Badge>
        </div>

        <div className="space-y-2">
          <h4 className="text-2xl font-semibold text-[var(--fg)]">{domain.domain_label}</h4>
          <p className="text-sm text-[var(--muted)]">
            {Math.round(domain.probability * 100)}% de forca com {domain.independent_techniques.length} tecnicas apontando
            para o mesmo tema.
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <MetricCard label="Janela" value={`${formatDate(domain.time_window.start)} · ${formatDate(domain.time_window.end)}`} />
          <MetricCard
            label="Tecnicas"
            value={domain.independent_techniques.map((technique) => normalizeLabel(technique)).join(' · ')}
          />
        </div>

        <div className="space-y-2">
          {domain.signals.slice(0, 3).map((signal) => (
            <div key={`${domain.domain}-${signal.label}`} className="rounded-[22px] border border-[var(--line)] bg-white/5 px-4 py-3">
              <p className="text-sm text-[var(--fg)]">{signal.label}</p>
              <p className="mt-1 text-xs uppercase tracking-[0.16em] text-[var(--muted-soft)]">
                {normalizeLabel(signal.technique)} · {signal.polarity}
              </p>
            </div>
          ))}
        </div>
      </div>
    </motion.article>
  )
}

function Badge({ children, tone }: { children: ReactNode; tone: 'warm' | 'soft' | 'muted' }) {
  const toneClass =
    tone === 'warm'
      ? 'border-[rgba(241,212,162,0.34)] bg-[rgba(241,212,162,0.12)] text-[var(--accent-strong)]'
      : tone === 'soft'
        ? 'border-[rgba(129,149,219,0.28)] bg-[rgba(129,149,219,0.08)] text-[#d7def8]'
        : 'border-[var(--line)] bg-white/5 text-[var(--muted)]'

  return <span className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.2em] ${toneClass}`}>{children}</span>
}

function InsightPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{label}</p>
      <p className="mt-2 text-sm text-[var(--fg)]">{value}</p>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{label}</p>
      <p className="mt-2 text-sm text-[var(--fg)]">{value}</p>
    </div>
  )
}

function SoftCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[26px] border border-[var(--line)] bg-white/5 px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{label}</p>
      <p className="mt-2 text-sm text-[var(--fg)]">{value}</p>
    </div>
  )
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
  }).format(new Date(`${value}T12:00:00`))
}

function normalizeLabel(value: string) {
  return value.replaceAll('_', ' ')
}
