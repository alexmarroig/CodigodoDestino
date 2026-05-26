'use client'

import type { ReactNode } from 'react'
import { motion } from 'framer-motion'

import {
  ForecastAreaEntry,
  LifeEpisode,
  MapaResponse,
  PredictiveInsight,
  TimelinePeriodEntry,
  TurningPoint,
  Uncertainty,
} from '@/types/mapa'

type ResultsDashboardProps = {
  result: MapaResponse
  onRestart: () => void
}

export function ResultsDashboard({ result, onRestart }: ResultsDashboardProps) {
  const quality = result.profile_quality ?? {
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
  const confidence = result.confidence ?? {
    level: 'low' as const,
    score: 0.3,
    reason: 'A leitura veio com pouca convergencia.',
    profile_quality: quality.code,
  }
  const predictive = result.predictive_insights ?? { detected_events: [], watchlist: [], summary: { detected_count: 0, watchlist_count: 0, strongest_category: null } }
  const areas = result.forecast_360?.areas_da_vida ?? []
  const timelinePeriods = result.timeline?.periods ?? []
  const monthlyTimeline = timelinePeriods.filter((item) => item.granularity === 'month').slice(0, 12)
  const turningPoints = result.turning_points ?? []
  const lifeEpisodes = result.life_episodes ?? []
  const uncertainties = result.uncertainties ?? []

  return (
    <section id="reading-stage" className="space-y-8">
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="cosmic-shell-strong rounded-[36px] px-6 py-8 sm:px-10 sm:py-10"
      >
        <div className="space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              <Badge tone={quality.code === 'A' ? 'warm' : quality.code === 'B' ? 'soft' : 'muted'}>
                Precisao {quality.code}
              </Badge>
              <Badge tone={confidence.level === 'high' ? 'warm' : confidence.level === 'medium' ? 'soft' : 'muted'}>
                Confianca {Math.round(confidence.score * 100)}%
              </Badge>
            </div>

            <motion.button
              type="button"
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.99 }}
              onClick={onRestart}
              className="ritual-button-muted inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
            >
              Nova leitura
            </motion.button>
          </div>

          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Resumo direto</p>
            <h2 className="max-w-4xl text-3xl font-semibold leading-tight sm:text-5xl">
              O que tende a acontecer agora.
            </h2>
            <p className="max-w-3xl text-sm text-[var(--muted)] sm:text-base">
              A tela abaixo mostra previsoes em linguagem direta, com janelas de tempo legiveis e menos repeticao.
            </p>
          </div>
        </div>
      </motion.section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr,0.9fr]">
        <SimpleConfidencePanel confidence={confidence} quality={quality} />
        <SimpleCautionPanel uncertainties={uncertainties} />
      </section>

      <section className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Previsoes principais</p>
          <h3 className="text-3xl font-semibold sm:text-4xl">O que esta mais claro no seu mapa</h3>
        </div>

        <div className="grid gap-4">
          {predictive.detected_events.length ? (
            predictive.detected_events.map((item, index) => (
              <PredictiveCard key={`${item.category_key}-${index}`} insight={item} index={index} />
            ))
          ) : (
            <EmptyState text="Ainda nao apareceu um evento forte o bastante para entrar como previsao principal." />
          )}
        </div>
      </section>

      {predictive.watchlist.length ? (
        <section className="space-y-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Temas em observacao</p>
            <h3 className="text-3xl font-semibold sm:text-4xl">O que apareceu, mas ainda nao fechou</h3>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {predictive.watchlist.map((item, index) => (
              <WatchCard key={`${item.category_key}-${index}`} insight={item} index={index} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-[1.05fr,0.95fr]">
        <SimpleTimelinePanel periods={monthlyTimeline} />
        <SimpleTurningPointsPanel points={turningPoints} />
      </section>

      <section className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Areas da vida</p>
          <h3 className="text-3xl font-semibold sm:text-4xl">Onde isso mexe de verdade</h3>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          {areas.map((area, index) => (
            <AreaCard key={area.key} area={area} index={index} />
          ))}
        </div>
      </section>

      {lifeEpisodes.length ? (
        <section className="space-y-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Capitulos</p>
            <h3 className="text-3xl font-semibold sm:text-4xl">Fases que estao abrindo</h3>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {lifeEpisodes.slice(0, 6).map((episode, index) => (
              <EpisodeCard key={episode.id} episode={episode} index={index} />
            ))}
          </div>
        </section>
      ) : null}
    </section>
  )
}

function PredictiveCard({ insight, index }: { insight: PredictiveInsight; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.34, delay: 0.05 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[30px] px-6 py-6"
    >
      <div className="space-y-5">
        <div className="flex flex-wrap gap-2">
          <Badge tone={insight.probability_level === 'Alta' ? 'warm' : 'soft'}>{translateProbability(insight.probability_level)}</Badge>
          <Badge tone="muted">{Math.round(insight.probability_score * 100)}%</Badge>
          {insight.exact_dates[0] ? <Badge tone="soft">Pico {formatFullDate(insight.exact_dates[0])}</Badge> : null}
        </div>

        <div className="space-y-2">
          <h4 className="text-2xl font-semibold text-[var(--fg)]">{translateEventType(insight.event_type)}</h4>
          <p className="text-sm text-[var(--muted)]">{insight.explanation}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <SoftCard label="Quando" value={buildDateRange(insight.time_window)} />
          <SoftCard label="Janela" value={translateTimeLabel(insight.time_window.label)} />
        </div>

        <DetailBlock title="O que esta acontecendo" text={insight.what_is_happening} />
        <BulletBlock title="Como isso pode aparecer na vida real" items={insight.what_this_may_look_like_in_real_life.slice(0, 2)} />
        {insight.signals.length ? <BulletBlock title="Aspectos e confirmacoes usadas" items={insight.signals.slice(0, 4)} /> : null}
        {insight.rule_hits.length ? <BulletBlock title="Regras que reforcam a leitura" items={insight.rule_hits.slice(0, 3)} /> : null}
        <DetailBlock title="Impacto" text={insight.impact} />
        <DetailBlock title="Risco" text={insight.risk} />
        <DetailBlock title="Acao recomendada" text={insight.recommended_action} />
      </div>
    </motion.article>
  )
}

function WatchCard({ insight, index }: { insight: PredictiveInsight; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, delay: 0.04 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[28px] px-5 py-5"
    >
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          <Badge tone="soft">Em observacao</Badge>
          <Badge tone="muted">{Math.round(insight.probability_score * 100)}%</Badge>
        </div>

        <h4 className="text-xl font-semibold text-[var(--fg)]">{translateEventType(insight.event_type)}</h4>
        <p className="text-sm text-[var(--muted)]">{insight.what_is_happening}</p>
        <SoftCard label="Quando observar" value={translateTimeLabel(insight.time_window.label)} />
        {insight.signals.length ? <BulletBlock title="Sinais usados" items={insight.signals.slice(0, 3)} /> : null}
      </div>
    </motion.article>
  )
}

function SimpleTimelinePanel({ periods }: { periods: TimelinePeriodEntry[] }) {
  return (
    <section className="cosmic-shell rounded-[30px] px-6 py-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Linha do tempo</p>
          <h3 className="text-2xl font-semibold">Mes a mes</h3>
        </div>

        <div className="space-y-3">
          {periods.map((period) => (
            <div key={period.period_key} className="rounded-[22px] border border-[var(--line)] bg-white/5 px-4 py-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-medium text-[var(--fg)]">{period.label}</p>
                <span className="text-xs text-[var(--muted)]">Pico {formatFullDate(period.peak)}</span>
              </div>
              <p className="mt-2 text-sm text-[var(--muted)]">{period.headline ?? 'O periodo ganha movimento.'}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function SimpleTurningPointsPanel({ points }: { points: TurningPoint[] }) {
  return (
    <section className="cosmic-shell rounded-[30px] px-6 py-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Datas-chave</p>
          <h3 className="text-2xl font-semibold">Pontos de virada</h3>
        </div>

        <div className="space-y-3">
          {points.length ? (
            points.slice(0, 6).map((point) => (
              <div key={`${point.domain}-${point.date}`} className="rounded-[22px] border border-[var(--line)] bg-white/5 px-4 py-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-medium text-[var(--fg)]">{point.headline}</p>
                  <span className="text-xs text-[var(--muted)]">{formatFullDate(point.date)}</span>
                </div>
                <p className="mt-2 text-sm text-[var(--muted)]">{point.summary}</p>
              </div>
            ))
          ) : (
            <EmptyState text="Ainda nao apareceu uma data dominante acima do resto do ciclo." />
          )}
        </div>
      </div>
    </section>
  )
}

function AreaCard({ area, index }: { area: ForecastAreaEntry; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, delay: 0.04 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[28px] px-5 py-5"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge tone={area.status === 'active' ? 'warm' : area.status === 'watch' ? 'soft' : 'muted'}>
            {area.status === 'active' ? 'Ativo' : area.status === 'watch' ? 'Observacao' : 'Calmo'}
          </Badge>
          <Badge tone="muted">{Math.round(area.probability * 100)}%</Badge>
        </div>

        <div className="space-y-2">
          <h4 className="text-xl font-semibold text-[var(--fg)]">{area.label}</h4>
          <p className="text-sm text-[var(--muted)]">{area.what_tends_to_happen}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <SoftCard label="Agora" value={area.short_term.summary} />
          <SoftCard label="Depois" value={area.mid_term.summary} />
        </div>

        {area.peak_dates[0] ? <SoftCard label="Data mais forte" value={formatFullDate(area.peak_dates[0])} /> : null}

        <p className="text-sm text-[var(--muted)]">
          <span className="text-[var(--fg)]">O que fazer:</span> {area.advice}
        </p>
      </div>
    </motion.article>
  )
}

function EpisodeCard({ episode, index }: { episode: LifeEpisode; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, delay: 0.04 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[28px] px-5 py-5"
    >
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          <Badge tone="soft">{normalizeLabel(episode.domain)}</Badge>
          {episode.peak ? <Badge tone="muted">Pico {formatFullDate(episode.peak)}</Badge> : null}
        </div>

        <h4 className="text-xl font-semibold text-[var(--fg)]">{episode.title}</h4>
        <p className="text-sm text-[var(--muted)]">{episode.summary}</p>
        <SoftCard label="Periodo" value={`${formatFullDate(episode.start)} a ${formatFullDate(episode.end)}`} />
      </div>
    </motion.article>
  )
}

function SimpleConfidencePanel({
  confidence,
  quality,
}: {
  confidence: MapaResponse['confidence']
  quality: MapaResponse['profile_quality']
}) {
  return (
    <section className="cosmic-shell rounded-[30px] px-6 py-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Leitura</p>
          <h3 className="text-2xl font-semibold">Quao firme isso esta</h3>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <SoftCard label="Confianca" value={`${Math.round(confidence.score * 100)}%`} />
          <SoftCard label="Precisao do horario" value={`${quality.code} - ${quality.label}`} />
        </div>

        <p className="text-sm text-[var(--muted)]">{confidence.reason}</p>
      </div>
    </section>
  )
}

function SimpleCautionPanel({ uncertainties }: { uncertainties: Uncertainty[] }) {
  const notes = uncertainties.slice(0, 2)

  return (
    <section className="cosmic-shell rounded-[30px] px-6 py-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Cautela</p>
          <h3 className="text-2xl font-semibold">O que ainda nao esta fechado</h3>
        </div>

        {notes.length ? (
          notes.map((item) => (
            <div key={`${item.domain}-${item.kind}`} className="rounded-[22px] border border-[var(--line)] bg-white/5 px-4 py-4 text-sm text-[var(--muted)]">
              {item.message}
            </div>
          ))
        ) : (
          <p className="text-sm text-[var(--muted)]">Os sinais vieram relativamente coerentes nesta leitura.</p>
        )}
      </div>
    </section>
  )
}

function DetailBlock({ title, text }: { title: string; text: string }) {
  return (
    <div className="space-y-1">
      <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{title}</p>
      <p className="text-sm text-[var(--fg)]">{text}</p>
    </div>
  )
}

function BulletBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="space-y-2">
      <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{title}</p>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item} className="rounded-[20px] border border-[var(--line)] bg-white/5 px-4 py-3 text-sm text-[var(--fg)]">
            {item}
          </div>
        ))}
      </div>
    </div>
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

function SoftCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] border border-[var(--line)] bg-white/5 px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{label}</p>
      <p className="mt-2 text-sm text-[var(--fg)]">{value}</p>
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return <div className="cosmic-shell rounded-[26px] px-5 py-5 text-sm text-[var(--muted)]">{text}</div>
}

function formatShortDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
  }).format(new Date(`${value}T12:00:00`))
}

function formatFullDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(`${value}T12:00:00`))
}

function buildDateRange(window: { start?: string; end?: string }) {
  if (!window.start || !window.end) {
    return 'Janela em formacao'
  }
  if (window.start === window.end) {
    return formatFullDate(window.start)
  }
  return `${formatShortDate(window.start)} a ${formatFullDate(window.end)}`
}

function translateProbability(value: PredictiveInsight['probability_level']) {
  switch (value) {
    case 'Alta':
      return 'Alta probabilidade'
    case 'Moderada':
      return 'Probabilidade moderada'
    case 'Baixa':
      return 'Sinal fraco'
    default:
      return 'Descartado'
  }
}

function translateEventType(value: string) {
  switch (value) {
    case 'Saude, doenca ou acidente':
      return 'Saude e desgaste'
    case 'Emprego, carreira ou perda de trabalho':
      return 'Mudanca de carreira ou trabalho'
    case 'Relacionamento, namoro ou casamento':
      return 'Relacionamentos'
    case 'Briga, ruptura ou separacao':
      return 'Ruptura ou separacao'
    case 'Grande mudanca de vida':
      return 'Grande virada de vida'
    default:
      return value
  }
}

function translateTimeLabel(value: string) {
  switch (value) {
    case 'proximas 1 a 2 semanas':
      return 'Proximas 1 a 2 semanas'
    case 'proximas 2 a 4 semanas':
      return 'Proximas 2 a 4 semanas'
    case 'dentro de 1 a 2 meses':
      return 'Dentro de 1 a 2 meses'
    case 'dentro de 2 a 4 meses':
      return 'Dentro de 2 a 4 meses'
    case 'dentro de 6 a 8 meses':
      return 'Dentro de 6 a 8 meses'
    case 'ao longo dos proximos 12 a 24 meses':
      return 'Ao longo dos proximos 12 a 24 meses'
    default:
      return value
  }
}

function normalizeLabel(value: string) {
  return value.replaceAll('_', ' ')
}
