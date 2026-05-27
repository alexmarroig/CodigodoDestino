'use client'

import Link from 'next/link'
import { useDeferredValue, useEffect, useState, useTransition } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

import { BrandOrb } from '@/components/BrandOrb'
import { BirthForm } from '@/components/BirthForm'
import { ErrorStatePanel } from '@/components/ErrorStatePanel'
import { LivingBackground } from '@/components/LivingBackground'
import { LoadingSkeleton } from '@/components/LoadingSkeleton'
import { DestinyReading } from '@/components/DestinyReading'
import { SplashScreen } from '@/components/SplashScreen'
import { ApiError, requestMapa } from '@/lib/api'
import { MapaRequest, MapaResponse } from '@/types/mapa'

const orbitalTransition = {
  duration: 22,
  ease: 'linear' as const,
  repeat: Number.POSITIVE_INFINITY,
}

export default function Home() {
  const [journeyStarted, setJourneyStarted] = useState(false)
  const [result, setResult] = useState<MapaResponse | null>(null)
  const deferredResult = useDeferredValue(result)
  const [lastPayload, setLastPayload] = useState<MapaRequest | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!journeyStarted) {
      return
    }

    document.getElementById('intake-stage')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [journeyStarted])

  useEffect(() => {
    if (!deferredResult) {
      return
    }

    document.getElementById('reading-stage')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [deferredResult])

  async function handleGenerate(payload: MapaRequest) {
    setLastPayload(payload)
    setError(null)
    setIsSubmitting(true)

    try {
      const nextResult = await requestMapa(payload)
      startTransition(() => {
        setResult(nextResult)
      })
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Nao foi possivel abrir a sua leitura agora. Tente novamente em instantes.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleRetry() {
    if (!lastPayload) {
      return
    }

    await handleGenerate(lastPayload)
  }

  function beginJourney() {
    setJourneyStarted(true)
  }

  function handleRestart() {
    setResult(null)
    setError(null)
    setJourneyStarted(true)
    document.getElementById('intake-stage')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const showLoading = isSubmitting || isPending

  return (
    <main className="relative min-h-screen overflow-hidden">
      <SplashScreen />

      <LivingBackground />

      <motion.div
        animate={{ rotate: 360 }}
        transition={orbitalTransition}
        className="pointer-events-none absolute left-[-10rem] top-20 h-[28rem] w-[28rem] rounded-full border border-[var(--line)] opacity-30"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ ...orbitalTransition, duration: 30 }}
        className="pointer-events-none absolute right-[-12rem] top-[18rem] h-[36rem] w-[36rem] rounded-full border border-[var(--line)] opacity-20"
      />

      <div className="relative mx-auto max-w-[1440px] px-5 pb-24 pt-4 sm:px-8 lg:px-10">
        <section className="grid min-h-[88svh] items-center gap-12 py-10 xl:grid-cols-[1.02fr,0.98fr]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, ease: 'easeOut' }}
            className="space-y-8"
          >
            <div className="space-y-5">
              <p className="text-xs uppercase tracking-[0.42em] text-[var(--muted-soft)]">Uma leitura para o seu agora</p>
              <div className="space-y-4">
                <h1 className="max-w-4xl text-5xl font-semibold leading-[0.88] sm:text-7xl xl:text-[6.4rem]">
                  O seu destino agora tem forma, orbita e movimento.
                </h1>
                <p className="max-w-2xl text-base text-[var(--muted)] sm:text-lg">
                  Sinais, ciclos, datas e capitulos da sua historia aparecem aqui em uma leitura mais viva e mais clara.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <motion.button
                type="button"
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.985 }}
                onClick={beginJourney}
                className="ritual-button inline-flex items-center justify-center rounded-full px-7 py-3.5 text-sm font-semibold"
              >
                Comecar
              </motion.button>
            </div>

            <div className="section-rule" />

            <div className="grid gap-4 sm:grid-cols-3">
              <HeroWhisper title="Entrada suave" copy="A experiencia abre em camadas, sem jogar tudo de uma vez." />
              <HeroWhisper title="Timeline real" copy="A leitura entra por ciclos, nao por frases soltas." />
              <HeroWhisper title="Leitura final" copy="Eventos, casas e narrativa em uma linguagem mais humana." />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, ease: 'easeOut', delay: 0.08 }}
            className="relative flex justify-center xl:justify-end"
          >
            <div className="brand-stage relative h-[38rem] w-full max-w-[36rem] overflow-hidden rounded-[44px]">
              <div className="brand-stage-backdrop absolute inset-0" />
              <div className="brand-stage-noise absolute inset-0" />
              <div className="relative flex h-full items-center justify-center px-8 py-8">
                <BrandOrb size="hero" />
              </div>
            </div>
          </motion.div>
        </section>

        <section id="intake-stage" className="space-y-8">
          <AnimatePresence mode="wait">
            {showLoading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <LoadingSkeleton />
              </motion.div>
            ) : deferredResult ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.36 }}
              >
                <DestinyReading result={deferredResult} onRestart={handleRestart} />
              </motion.div>
            ) : error ? (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <ErrorStatePanel message={error} onRetry={lastPayload ? handleRetry : undefined} onReviewInputs={handleRestart} />
              </motion.div>
            ) : journeyStarted ? (
              <motion.div
                key="intake"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.34 }}
              >
                <BirthForm onSubmit={handleGenerate} pending={showLoading} />
              </motion.div>
            ) : (
              <motion.section
                key="invitation"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.34 }}
                className="cosmic-shell rounded-[36px] px-6 py-10 text-center sm:px-10"
              >
                <p className="text-xs uppercase tracking-[0.36em] text-[var(--muted-soft)]">Quando quiser comecar</p>
                <h2 className="mt-5 text-3xl font-semibold sm:text-5xl">Sua leitura se abre em seis passos curtos.</h2>
                <p className="mx-auto mt-4 max-w-2xl text-sm text-[var(--muted)] sm:text-base">
                  Nascimento, vida hoje e histórico emocional. Depois, doze seções claras sobre o seu destino.
                </p>
                <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                  <motion.button
                    type="button"
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.985 }}
                    onClick={beginJourney}
                    className="ritual-button inline-flex items-center justify-center rounded-full px-7 py-3.5 text-sm font-semibold"
                  >
                    Comecar agora
                  </motion.button>
                  <Link
                    href="/horaria"
                    className="ritual-button-muted inline-flex items-center justify-center rounded-full px-7 py-3.5 text-sm font-semibold"
                  >
                    Fazer pergunta horaria
                  </Link>
                </div>
              </motion.section>
            )}
          </AnimatePresence>
        </section>
      </div>
    </main>
  )
}

function HeroWhisper({ title, copy }: { title: string; copy: string }) {
  return (
    <div className="rounded-[28px] border border-[var(--line)] bg-white/5 px-4 py-4">
      <p className="text-sm font-semibold text-[var(--fg)]">{title}</p>
      <p className="mt-2 text-sm text-[var(--muted)]">{copy}</p>
    </div>
  )
}

function PortalLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-[var(--line)] pb-4 text-sm last:border-b-0 last:pb-0">
      <span className="text-[var(--muted-soft)]">{label}</span>
      <span className="max-w-[70%] text-right text-[var(--fg)]">{value}</span>
    </div>
  )
}
