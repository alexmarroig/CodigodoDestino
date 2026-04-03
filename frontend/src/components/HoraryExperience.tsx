'use client'

import Link from 'next/link'
import type { ReactNode } from 'react'
import type { FormEvent } from 'react'
import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

import { ErrorStatePanel } from '@/components/ErrorStatePanel'
import { ApiError, requestHorary } from '@/lib/api'
import { BRAZIL_CITY_OPTIONS } from '@/lib/brazilCities'
import { HoraryRequest, HoraryResponse } from '@/types/mapa'

type FormState = {
  question: string
  date: string
  time: string
  cityQuery: string
  selectedCityId: string | null
}

const initialState: FormState = {
  question: '',
  date: '2026-04-03',
  time: '14:30',
  cityQuery: '',
  selectedCityId: null,
}

function normalizeValue(value: string) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()
}

export function HoraryExperience() {
  const [values, setValues] = useState<FormState>(initialState)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<HoraryResponse | null>(null)

  const selectedCity = BRAZIL_CITY_OPTIONS.find((city) => city.id === values.selectedCityId) ?? null
  const filteredCities = BRAZIL_CITY_OPTIONS.filter((city) =>
    normalizeValue(city.label).includes(normalizeValue(values.cityQuery)),
  ).slice(0, values.cityQuery ? 8 : 6)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!selectedCity) {
      setError('Escolha uma cidade da lista para ancorar o momento da pergunta.')
      return
    }

    setPending(true)
    setError(null)

    const payload: HoraryRequest = {
      question: values.question,
      date: values.date,
      time: values.time,
      lat: selectedCity.lat,
      lon: selectedCity.lon,
      timezone: selectedCity.timezone,
      orb_degrees: 4,
      house_system: 'P',
    }

    try {
      const next = await requestHorary(payload)
      setResult(next)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Nao consegui abrir essa leitura horaria agora.')
      }
    } finally {
      setPending(false)
    }
  }

  function resetForm() {
    setResult(null)
    setError(null)
  }

  return (
    <main className="relative min-h-screen overflow-hidden">
      <div className="aurora-field pointer-events-none absolute inset-0 opacity-80" />
      <div className="starfield pointer-events-none absolute inset-0 opacity-45" />

      <div className="relative mx-auto max-w-[1200px] px-5 pb-20 pt-8 sm:px-8">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.42em] text-[var(--muted-soft)]">Codigo do Destino</p>
            <h1 className="text-3xl font-semibold sm:text-5xl">Leitura horaria</h1>
            <p className="max-w-2xl text-sm text-[var(--muted)] sm:text-base">
              Para perguntas objetivas. O mapa se abre no instante exato em que a duvida e colocada.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link href="/" className="ritual-button-muted inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold">
              Voltar ao mapa natal
            </Link>
          </div>
        </header>

        <section className="mt-10 grid gap-6 xl:grid-cols-[0.95fr,1.05fr]">
          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, ease: 'easeOut' }}
            className="cosmic-shell-strong rounded-[36px] p-6 sm:p-8"
          >
            <div className="space-y-6">
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Pergunta objetiva</p>
                <textarea
                  value={values.question}
                  onChange={(event) => setValues((current) => ({ ...current, question: event.target.value }))}
                  placeholder="Ex.: Vou conseguir essa vaga? Vale insistir nessa relacao? Esse movimento profissional faz sentido?"
                  className="question-shell min-h-[140px] w-full resize-none px-5 py-4 text-base text-[var(--fg)] placeholder:text-[var(--muted-soft)]"
                  required
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="space-y-2">
                  <span className="text-xs uppercase tracking-[0.24em] text-[var(--muted-soft)]">Data da pergunta</span>
                  <input
                    type="date"
                    value={values.date}
                    onChange={(event) => setValues((current) => ({ ...current, date: event.target.value }))}
                    className="question-shell w-full px-4 py-3 text-[var(--fg)]"
                    required
                  />
                </label>
                <label className="space-y-2">
                  <span className="text-xs uppercase tracking-[0.24em] text-[var(--muted-soft)]">Hora exata</span>
                  <input
                    type="time"
                    value={values.time}
                    onChange={(event) => setValues((current) => ({ ...current, time: event.target.value }))}
                    className="question-shell w-full px-4 py-3 text-[var(--fg)]"
                    required
                  />
                </label>
              </div>

              <div className="space-y-3">
                <label className="space-y-2">
                  <span className="text-xs uppercase tracking-[0.24em] text-[var(--muted-soft)]">Cidade da pergunta</span>
                  <input
                    type="text"
                    value={values.cityQuery}
                    onChange={(event) =>
                      setValues((current) => ({
                        ...current,
                        cityQuery: event.target.value,
                        selectedCityId: null,
                      }))
                    }
                    placeholder="Digite sua cidade"
                    className="question-shell w-full px-4 py-3 text-[var(--fg)] placeholder:text-[var(--muted-soft)]"
                    required
                  />
                </label>

                <div className="grid gap-3 sm:grid-cols-2">
                  {filteredCities.map((city) => (
                    <button
                      key={city.id}
                      type="button"
                      onClick={() => setValues((current) => ({ ...current, cityQuery: city.label, selectedCityId: city.id }))}
                      className={`question-shell px-4 py-3 text-left ${
                        values.selectedCityId === city.id ? 'border-[rgba(241,212,162,0.4)] bg-white/10' : ''
                      }`}
                    >
                      <p className="text-sm font-semibold text-[var(--fg)]">{city.label}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <motion.button
                  type="submit"
                  whileHover={pending ? undefined : { y: -2 }}
                  whileTap={pending ? undefined : { scale: 0.985 }}
                  disabled={pending || !values.question || !selectedCity}
                  className="ritual-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {pending ? 'Abrindo o mapa da pergunta...' : 'Ler esta pergunta'}
                </motion.button>
                {result ? (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="ritual-button-muted inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold"
                  >
                    Fazer outra pergunta
                  </button>
                ) : null}
              </div>
            </div>
          </motion.form>

          <AnimatePresence mode="wait">
            {error ? (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
              >
                <ErrorStatePanel
                  message={error}
                  onReviewInputs={() => setError(null)}
                  reviewLabel="Voltar ao formulario"
                  compact
                />
              </motion.div>
            ) : result ? (
              <motion.section
                key="result"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
                transition={{ duration: 0.42, ease: 'easeOut' }}
                className="space-y-5"
              >
                <div className="cosmic-shell-strong rounded-[36px] p-6 sm:p-8">
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      <StatusBadge tone={result.is_radical ? 'warm' : 'muted'}>
                        {result.is_radical ? 'Mapa apto' : 'Mapa com restricoes'}
                      </StatusBadge>
                      <StatusBadge tone={result.confidence.level === 'high' ? 'warm' : result.confidence.level === 'medium' ? 'soft' : 'muted'}>
                        Confianca {result.confidence.level}
                      </StatusBadge>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs uppercase tracking-[0.28em] text-[var(--muted-soft)]">Julgamento</p>
                      <h2 className="text-3xl font-semibold sm:text-4xl">{result.judgment}</h2>
                      <p className="text-sm text-[var(--muted)]">{result.uncertainty_reason}</p>
                    </div>
                  </div>
                </div>

                <InfoPanel
                  title="Significadores"
                  body={`Voce entra pelo regente de ${result.significators.querent_sign.sign}; o assunto entra pela casa ${result.significators.quesited_house}, ligada a ${result.significators.quesited_domain.replaceAll('_', ' ')}.`}
                />

                <InfoPanel
                  title="A favor"
                  items={result.testimonies_for.map((item) => `${item.label} · peso ${item.weight.toFixed(2)}`)}
                />

                <InfoPanel
                  title="Contra"
                  items={result.testimonies_against.map((item) => `${item.label} · peso ${item.weight.toFixed(2)}`)}
                />

                {result.strictures.length ? (
                  <InfoPanel title="Consideracoes antes do julgamento" items={result.strictures.map((item) => item.message)} />
                ) : null}
              </motion.section>
            ) : (
              <motion.section
                key="empty"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
                className="cosmic-shell rounded-[36px] p-6 sm:p-8"
              >
                <div className="space-y-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted-soft)]">Como funciona</p>
                  <h2 className="text-3xl font-semibold sm:text-4xl">Pergunta clara, momento exato, resposta mais honesta.</h2>
                  <p className="text-sm text-[var(--muted)]">
                    Horaria nao substitui o mapa natal. Ela serve para duvidas concretas do agora, quando voce precisa saber se um
                    tema tende a abrir, travar ou permanecer indefinido.
                  </p>
                </div>
              </motion.section>
            )}
          </AnimatePresence>
        </section>
      </div>
    </main>
  )
}

function StatusBadge({ children, tone }: { children: ReactNode; tone: 'warm' | 'soft' | 'muted' }) {
  const toneClass =
    tone === 'warm'
      ? 'border-[rgba(241,212,162,0.34)] bg-[rgba(241,212,162,0.12)] text-[var(--accent-strong)]'
      : tone === 'soft'
        ? 'border-[rgba(129,149,219,0.28)] bg-[rgba(129,149,219,0.08)] text-[#d7def8]'
        : 'border-[var(--line)] bg-white/5 text-[var(--muted)]'

  return <span className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.2em] ${toneClass}`}>{children}</span>
}

function InfoPanel({ title, body, items }: { title: string; body?: string; items?: string[] }) {
  return (
    <div className="cosmic-shell rounded-[30px] px-5 py-5">
      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted-soft)]">{title}</p>
        {body ? <p className="text-sm text-[var(--muted)]">{body}</p> : null}
        {items?.length ? (
          <div className="space-y-2">
            {items.map((item) => (
              <div key={item} className="rounded-[20px] border border-[var(--line)] bg-white/5 px-4 py-3 text-sm text-[var(--fg)]">
                {item}
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}
