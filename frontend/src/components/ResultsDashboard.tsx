'use client'

import type { ReactNode } from 'react'
import { motion } from 'framer-motion'

import {
  DomainAnalysisEntry,
  DomainCoverageEntry,
  ForecastAreaEntry,
  ForecastHouseEntry,
  LifeEpisode,
  MapaResponse,
  TimelinePeriodEntry,
  TurningPoint,
  Uncertainty,
} from '@/types/mapa'

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
  const coverage = result.analysis?.domain_analysis?.coverage ?? []
  const uncertainties = result.uncertainties ?? result.analysis?.domain_analysis?.uncertainties ?? []
  const macroHouse = result.analysis?.profections?.activated_house
  const forecast360 = result.forecast_360
  const timelinePeriods = result.timeline?.periods ?? []
  const lifeEpisodes = result.life_episodes ?? []
  const turningPoints = result.turning_points ?? []
  const lifeEvents = result.life_events ?? forecast360?.life_events ?? []
  const purpose = forecast360?.proposito ?? result.analysis?.purpose_analysis

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

      {forecast360 ? (
        <>
          <section className="space-y-5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Leitura 360</p>
              <h3 className="text-3xl font-semibold sm:text-5xl">O ciclo inteiro, nao so um evento</h3>
              <p className="max-w-3xl text-sm text-[var(--muted)] sm:text-base">{forecast360.summary}</p>
            </div>

            <div className="grid gap-4 xl:grid-cols-[1.12fr,0.88fr]">
              <TimelinePanel periods={timelinePeriods} />
              <TurningPointsPanel points={turningPoints} />
            </div>
          </section>

          {lifeEvents.length ? <LifeEventsPanel events={lifeEvents} /> : null}

          {purpose ? <PurposePanel purpose={purpose} /> : null}

          <section className="space-y-5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Episodios</p>
              <h3 className="text-3xl font-semibold sm:text-5xl">Capitulos que estao abrindo</h3>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {lifeEpisodes.map((episode, index) => (
                <EpisodeCard key={episode.id} episode={episode} index={index} />
              ))}
            </div>
          </section>

          <section className="space-y-5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Areas da vida</p>
              <h3 className="text-3xl font-semibold sm:text-5xl">Curto prazo, ano e proximo capitulo</h3>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {forecast360.areas_da_vida.map((area, index) => (
                <AreaForecastCard key={area.key} area={area} index={index} />
              ))}
            </div>
          </section>

          <section className="space-y-5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Casa por casa</p>
              <h3 className="text-3xl font-semibold sm:text-5xl">As 12 casas do seu ciclo</h3>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {forecast360.casas.map((house, index) => (
                <HouseForecastCard key={house.house} house={house} index={index} />
              ))}
            </div>
          </section>
        </>
      ) : null}

      <section className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Panorama completo</p>
            <h3 className="text-3xl font-semibold sm:text-5xl">Os temas da sua vida agora</h3>
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

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {coverage.map((item, index) => (
            <CoverageCard key={item.key} item={item} index={index} />
          ))}
        </div>
      </section>

      <section className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Convergencias tecnicas</p>
          <h3 className="text-3xl font-semibold sm:text-5xl">Onde os sinais batem mais forte</h3>
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

function TimelinePanel({ periods }: { periods: TimelinePeriodEntry[] }) {
  const visible = periods.slice(0, 12)

  return (
    <section className="cosmic-shell rounded-[34px] px-6 py-6 sm:px-8">
      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Linha do tempo</p>
          <h3 className="text-2xl font-semibold sm:text-3xl">Mes a mes, onde a vida aperta</h3>
        </div>

        <div className="space-y-3">
          {visible.map((period) => (
            <div key={period.period_key} className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">{period.label}</p>
              <p className="mt-2 text-sm text-[var(--fg)]">{period.headline}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function TurningPointsPanel({ points }: { points: TurningPoint[] }) {
  return (
    <section className="cosmic-shell rounded-[34px] px-6 py-6 sm:px-8">
      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Pontos de virada</p>
          <h3 className="text-2xl font-semibold sm:text-3xl">Datas que merecem atencao</h3>
        </div>

        <div className="space-y-3">
          {points.length === 0 ? (
            <p className="text-sm text-[var(--muted)]">Ainda nao apareceu uma data-pico dominante acima do ruido geral.</p>
          ) : (
            points.slice(0, 6).map((point) => (
              <div key={`${point.domain}-${point.date}`} className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
                <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">
                  {formatDate(point.date)} · {point.label}
                </p>
                <p className="mt-2 text-sm text-[var(--fg)]">{point.headline}</p>
                <p className="mt-2 text-sm text-[var(--muted)]">{point.summary}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  )
}

function EpisodeCard({ episode, index }: { episode: LifeEpisode; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.36, delay: 0.05 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[30px] px-6 py-6"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge tone="warm">{normalizeLabel(episode.domain)}</Badge>
          {episode.peak ? <Badge tone="soft">Pico {formatDate(episode.peak)}</Badge> : null}
        </div>

        <div className="space-y-2">
          <h4 className="text-2xl font-semibold text-[var(--fg)]">{episode.title}</h4>
          <p className="text-sm text-[var(--muted)]">{episode.summary}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <SoftCard label="Capitulo" value={`${episode.start} ate ${episode.end}`} />
          <SoftCard label="Arco" value={episode.arc} />
        </div>
      </div>
    </motion.article>
  )
}

function AreaForecastCard({ area, index }: { area: ForecastAreaEntry; index: number }) {
  const specialMetrics = buildAreaSpecialMetrics(area)
  const exactHits = area.special_focus?.exact_hits ?? []
  const lifeEvents = area.special_focus?.life_events ?? []

  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.36, delay: 0.05 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[30px] px-6 py-6"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge tone={area.status === 'active' ? 'warm' : area.status === 'watch' ? 'soft' : 'muted'}>
            {area.status === 'active' ? 'Ativo' : area.status === 'watch' ? 'Em observacao' : 'Silencioso'}
          </Badge>
          <Badge tone={area.confidence === 'high' ? 'warm' : area.confidence === 'medium' ? 'soft' : 'muted'}>
            {Math.round(area.probability * 100)}%
          </Badge>
        </div>

        <div className="space-y-2">
          <h4 className="text-2xl font-semibold text-[var(--fg)]">{area.label}</h4>
          <p className="text-sm text-[var(--muted)]">{area.what_tends_to_happen}</p>
        </div>

        {specialMetrics.length ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {specialMetrics.map((metric) => (
              <SoftCard key={`${area.key}-${metric.label}`} label={metric.label} value={metric.value} />
            ))}
          </div>
        ) : null}

        <div className="grid gap-3">
          <SoftCard label="Curto prazo" value={area.short_term.summary} />
          <SoftCard label="Proximos 12 meses" value={area.mid_term.summary} />
          <SoftCard label="Capitulo mais longo" value={area.long_term.summary} />
        </div>

        {area.special_focus?.why_now ? (
          <p className="text-sm text-[var(--muted)]">
            <span className="text-[var(--fg)]">Por que agora:</span> {area.special_focus.why_now}
          </p>
        ) : null}

        {exactHits.length ? (
          <div className="space-y-3">
            <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">Datas mais exatas</p>
            {exactHits.slice(0, 2).map((hit) => (
              <div key={`${area.key}-${hit.type}-${hit.date}`} className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
                <p className="text-sm text-[var(--fg)]">
                  {formatFullDate(hit.time_window.start)} ate {formatFullDate(hit.time_window.end)}
                </p>
                <p className="mt-2 text-sm text-[var(--muted)]">
                  Pico em {formatFullDate(hit.time_window.peak ?? hit.date)} com {normalizeLabel(hit.label)}.
                </p>
              </div>
            ))}
          </div>
        ) : null}

        {lifeEvents.length ? (
          <div className="space-y-3">
            <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">Eventos de vida</p>
            {lifeEvents.slice(0, 2).map((event) => (
              <div key={`${area.key}-${event.type}-${event.date}`} className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
                <p className="text-sm text-[var(--fg)]">{event.label}</p>
                <p className="mt-2 text-sm text-[var(--muted)]">
                  {formatFullDate(event.window.start)} ate {formatFullDate(event.window.end)}, com pico em{' '}
                  {formatFullDate(event.window.peak)}.
                </p>
              </div>
            ))}
          </div>
        ) : null}

        <p className="text-sm text-[var(--muted)]">{area.advice}</p>
      </div>
    </motion.article>
  )
}

function LifeEventsPanel({ events }: { events: MapaResponse['life_events'] }) {
  return (
    <section className="space-y-5">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Eventos de vida</p>
        <h3 className="text-3xl font-semibold sm:text-5xl">Janelas mais provaveis do ciclo</h3>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {events?.map((event, index) => (
          <motion.article
            key={`${event.type}-${event.date}`}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.36, delay: 0.05 * index, ease: 'easeOut' }}
            className="cosmic-shell rounded-[30px] px-6 py-6"
          >
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Badge tone={event.intensity === 'high' ? 'warm' : 'soft'}>{event.intensity}</Badge>
                <Badge tone="muted">{normalizeLabel(event.area_key)}</Badge>
                <Badge tone="soft">{event.strength} sinais</Badge>
              </div>

              <div className="space-y-2">
                <h4 className="text-2xl font-semibold text-[var(--fg)]">{event.label}</h4>
                <p className="text-sm text-[var(--muted)]">{event.summary}</p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <SoftCard
                  label="Janela"
                  value={`${formatFullDate(event.window.start)} ate ${formatFullDate(event.window.end)}`}
                />
                <SoftCard label="Pico" value={formatFullDate(event.window.peak)} />
              </div>

              <p className="text-sm text-[var(--muted)]">
                <span className="text-[var(--fg)]">Causa principal:</span> {normalizeLabel(event.cause)}
              </p>
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  )
}

function PurposePanel({ purpose }: { purpose: NonNullable<MapaResponse['forecast_360']>['proposito'] | NonNullable<MapaResponse['analysis']>['purpose_analysis'] }) {
  return (
    <section className="cosmic-shell rounded-[34px] px-6 py-6 sm:px-8">
      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Proposito</p>
          <h3 className="text-2xl font-semibold sm:text-3xl">Direcao mais profunda do ciclo</h3>
        </div>

        <div className="space-y-3">
          <p className="text-sm text-[var(--fg)]">{purpose?.summary}</p>
          <p className="text-sm text-[var(--muted)]">{purpose?.current_focus}</p>
          <p className="text-sm text-[var(--muted)]">{purpose?.long_arc}</p>
        </div>

        {purpose?.focus_domains?.length ? (
          <div className="flex flex-wrap gap-2">
            {purpose.focus_domains.map((domain) => (
              <Badge key={domain} tone="soft">
                {normalizeLabel(domain)}
              </Badge>
            ))}
          </div>
        ) : null}

        {purpose?.evidence?.length ? (
          <div className="space-y-3">
            {purpose.evidence.slice(0, 3).map((item) => (
              <div key={item} className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4 text-sm text-[var(--muted)]">
                {item}
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  )
}

function HouseForecastCard({ house, index }: { house: ForecastHouseEntry; index: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.34, delay: 0.03 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[28px] px-5 py-5"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge tone={house.status === 'active' ? 'warm' : house.status === 'watch' ? 'soft' : 'muted'}>
            {house.status === 'active' ? 'Ativa' : house.status === 'watch' ? 'Observacao' : 'Silenciosa'}
          </Badge>
        </div>
        <div className="space-y-2">
          <h4 className="text-xl font-semibold text-[var(--fg)]">{house.label}</h4>
          <p className="text-sm text-[var(--muted)]">{house.what_tends_to_happen}</p>
        </div>
        <div className="grid gap-3">
          <SoftCard label="Curto" value={house.short_term.summary} />
          <SoftCard label="Ano" value={house.mid_term.summary} />
        </div>
      </div>
    </motion.article>
  )
}

function CoverageCard({ item, index }: { item: DomainCoverageEntry; index: number }) {
  const statusTone = item.status === 'active' ? 'warm' : item.status === 'watch' ? 'soft' : 'muted'
  const statusLabel = item.status === 'active' ? 'Ativo' : item.status === 'watch' ? 'Em observacao' : 'Silencioso'
  const peakDate = item.time_window?.peak ? formatDate(item.time_window.peak) : 'Sem pico forte'

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.34, delay: 0.05 * index, ease: 'easeOut' }}
      className="cosmic-shell rounded-[30px] px-5 py-5"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge tone={statusTone}>{statusLabel}</Badge>
          <Badge tone={item.confidence === 'high' ? 'warm' : item.confidence === 'medium' ? 'soft' : 'muted'}>
            {Math.round(item.probability * 100)}%
          </Badge>
        </div>

        <div className="space-y-2">
          <h4 className="text-xl font-semibold text-[var(--fg)]">{item.label}</h4>
          <p className="text-sm text-[var(--muted)]">{item.summary}</p>
        </div>

        <div className="grid gap-3">
          <SoftCard label="Data-pico" value={peakDate} />
          <SoftCard
            label="Janela"
            value={
              item.time_window
                ? `${formatDate(item.time_window.start)} ate ${formatDate(item.time_window.end)}`
                : 'Sem janela forte por enquanto'
            }
          />
        </div>
      </div>
    </motion.article>
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

function formatFullDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${value}T12:00:00`))
}

function normalizeLabel(value: string) {
  return value.replaceAll('_', ' ')
}

function buildAreaSpecialMetrics(area: ForecastAreaEntry) {
  const focus = area.special_focus
  if (!focus) {
    return []
  }

  if (area.key === 'relacionamento') {
    return [
      {
        label: 'Compromisso',
        value: `${Math.round((focus.marriage_probability ?? focus.bonding_probability ?? 0) * 100)}%`,
      },
      {
        label: 'Ruptura',
        value: `${Math.round((focus.breakup_probability ?? focus.tension_probability ?? 0) * 100)}%`,
      },
    ]
  }

  if (area.key === 'financas') {
    return [
      {
        label: 'Expansao',
        value: `${Math.round((focus.growth_probability ?? 0) * 100)}%`,
      },
      {
        label: 'Restricao',
        value: `${Math.round((focus.restriction_probability ?? 0) * 100)}%`,
      },
    ]
  }

  return focus.current_theme
    ? [
        {
          label: 'Tema dominante',
          value: normalizeLabel(focus.current_theme),
        },
      ]
    : []
}
