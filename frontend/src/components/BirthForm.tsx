'use client'

import { FormEvent, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

import { BRAZIL_CITY_OPTIONS } from '@/lib/brazilCities'
import { MapaRequest } from '@/types/mapa'

type BirthFormProps = {
  id?: string
  onSubmit: (payload: MapaRequest) => Promise<void>
  pending: boolean
}

type FormState = {
  date: string
  time: string
  timeUnknown: boolean
  cityQuery: string
  selectedCityId: string | null
}

const initialState: FormState = {
  date: '1995-03-10',
  time: '',
  timeUnknown: false,
  cityQuery: '',
  selectedCityId: null,
}

function normalizeValue(value: string) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()
}

export function BirthForm({ id, onSubmit, pending }: BirthFormProps) {
  const [step, setStep] = useState(0)
  const [values, setValues] = useState<FormState>(initialState)
  const [validationError, setValidationError] = useState<string | null>(null)

  const selectedCity = useMemo(
    () => BRAZIL_CITY_OPTIONS.find((city) => city.id === values.selectedCityId) ?? null,
    [values.selectedCityId],
  )

  const filteredCities = useMemo(() => {
    const query = normalizeValue(values.cityQuery)

    if (!query) {
      return BRAZIL_CITY_OPTIONS.slice(0, 7)
    }

    return BRAZIL_CITY_OPTIONS.filter((city) => normalizeValue(city.label).includes(query)).slice(0, 7)
  }, [values.cityQuery])

  function goToStep(nextStep: number) {
    setValidationError(null)
    setStep(nextStep)
  }

  function handleTimeChange(nextTime: string) {
    setValidationError(null)
    setValues((current) => ({
      ...current,
      time: nextTime,
      timeUnknown: false,
    }))
  }

  function handleUnknownTime() {
    setValidationError(null)
    setValues((current) => ({
      ...current,
      timeUnknown: true,
      time: '12:00',
    }))
    window.setTimeout(() => {
      setStep(2)
    }, 140)
  }

  function handleCityQueryChange(nextQuery: string) {
    setValidationError(null)
    setValues((current) => ({
      ...current,
      cityQuery: nextQuery,
      selectedCityId:
        current.selectedCityId && normalizeValue(nextQuery) === normalizeValue(selectedCity?.label ?? '')
          ? current.selectedCityId
          : null,
    }))
  }

  function handleCitySelect(cityId: string) {
    const city = BRAZIL_CITY_OPTIONS.find((item) => item.id === cityId)
    if (!city) {
      return
    }

    setValidationError(null)
    setValues((current) => ({
      ...current,
      cityQuery: city.label,
      selectedCityId: city.id,
    }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!values.date) {
      setValidationError('Escolha a sua data de nascimento para continuar.')
      setStep(0)
      return
    }

    if (!values.time && !values.timeUnknown) {
      setValidationError('Para uma leitura astrologica precisa, informe a hora do nascimento.')
      setStep(1)
      return
    }

    if (!selectedCity) {
      setValidationError('Escolha uma cidade da lista para que a leitura fique consistente.')
      setStep(2)
      return
    }

    await onSubmit({
      date: values.date,
      time: values.timeUnknown ? undefined : values.time || undefined,
      timezone: selectedCity.timezone,
      lat: selectedCity.lat,
      lon: selectedCity.lon,
      orb_degrees: 6,
      house_system: 'P',
      birth_time_precision: values.timeUnknown ? 'unknown' : 'exact',
    })
  }

  return (
    <motion.form
      id={id}
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 26 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: 'easeOut' }}
      className="cosmic-shell-strong relative overflow-hidden rounded-[36px] p-6 sm:p-8 lg:p-10"
    >
      <div className="aurora-field absolute inset-0 opacity-80" />
      <div className="starfield absolute inset-0 opacity-50" />

      <div className="relative">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.4em] text-[var(--muted-soft)]">Sua leitura</p>
            <div className="flex gap-2">
              {[0, 1, 2].map((index) => (
                <span
                  key={index}
                  className={`h-1.5 w-12 rounded-full ${
                    index <= step ? 'bg-[var(--accent)]' : 'bg-white/10'
                  }`}
                />
              ))}
            </div>
          </div>
          <p className="text-sm text-[var(--muted)]">Tres passos para abrir a leitura.</p>
        </div>

        <div className="section-rule my-8" />

        <AnimatePresence mode="wait">
          {step === 0 ? (
            <motion.section
              key="step-date"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -18 }}
              transition={{ duration: 0.28 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Primeiro passo</p>
                <div className="space-y-3">
                  <h2 className="text-4xl font-semibold leading-[0.92] sm:text-5xl">Quando voce nasceu?</h2>
                  <p className="max-w-2xl text-base text-[var(--muted)] sm:text-lg">
                    A data desenha o contorno da sua leitura e revela o clima maior da sua origem.
                  </p>
                </div>
              </div>

              <div className="question-shell max-w-md px-4 py-3">
                <input
                  type="date"
                  value={values.date}
                  onChange={(event) => setValues((current) => ({ ...current, date: event.target.value }))}
                  className="w-full border-0 bg-transparent px-2 py-3 text-lg text-[var(--fg)]"
                  required
                />
              </div>

              <motion.button
                type="button"
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.985 }}
                disabled={!values.date}
                onClick={() => goToStep(1)}
                className="ritual-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40"
              >
                Continuar
              </motion.button>
            </motion.section>
          ) : null}

          {step === 1 ? (
            <motion.section
              key="step-time"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -18 }}
              transition={{ duration: 0.28 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Segundo passo</p>
                <div className="space-y-3">
                  <h2 className="text-4xl font-semibold leading-[0.92] sm:text-5xl">Qual foi o horario do seu nascimento?</h2>
                  <p className="max-w-2xl text-base text-[var(--muted)] sm:text-lg">
                    Aqui mora boa parte da precisao astrologica. Se voce souber a hora, a leitura fica muito mais fiel.
                  </p>
                </div>
              </div>

              <div className="question-shell max-w-md px-4 py-3">
                <input
                  type="time"
                  value={values.timeUnknown ? '' : values.time}
                  onChange={(event) => handleTimeChange(event.target.value)}
                  className="w-full border-0 bg-transparent px-2 py-3 text-lg text-[var(--fg)]"
                />
              </div>

              <div className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4 text-sm text-[var(--muted)]">
                Se voce nao souber a hora exata, ainda podemos seguir. Mas a leitura perde precisao, especialmente nas camadas mais sensiveis do mapa.
              </div>

              <div className="flex flex-wrap gap-3">
                <motion.button
                  type="button"
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.985 }}
                  onClick={() => goToStep(0)}
                  className="ritual-button-muted inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold"
                >
                  Voltar
                </motion.button>
                <motion.button
                  type="button"
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.985 }}
                  disabled={!values.time}
                  onClick={() => goToStep(2)}
                  className="ritual-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Continuar com horario exato
                </motion.button>
                <motion.button
                  type="button"
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.985 }}
                  onClick={handleUnknownTime}
                  className="ritual-button-muted inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold"
                >
                  Nao sei a hora exata
                </motion.button>
              </div>
            </motion.section>
          ) : null}

          {step === 2 ? (
            <motion.section
              key="step-city"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -18 }}
              transition={{ duration: 0.28 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <p className="text-xs uppercase tracking-[0.34em] text-[var(--muted-soft)]">Terceiro passo</p>
                <div className="space-y-3">
                  <h2 className="text-4xl font-semibold leading-[0.92] sm:text-5xl">Onde voce nasceu?</h2>
                  <p className="max-w-2xl text-base text-[var(--muted)] sm:text-lg">
                    Digite sua cidade e escolha a sugestao mais proxima. Assim a leitura encontra o seu ponto de origem.
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="question-shell max-w-2xl px-4 py-3">
                  <input
                    type="text"
                    value={values.cityQuery}
                    onChange={(event) => handleCityQueryChange(event.target.value)}
                    placeholder="Digite sua cidade"
                    className="w-full border-0 bg-transparent px-2 py-3 text-lg text-[var(--fg)] placeholder:text-[var(--muted-soft)]"
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {filteredCities.map((city) => (
                    <motion.button
                      key={city.id}
                      type="button"
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.985 }}
                      onClick={() => handleCitySelect(city.id)}
                      className={`question-shell px-4 py-4 text-left ${
                        values.selectedCityId === city.id ? 'border-[rgba(241,212,162,0.4)] bg-white/10' : ''
                      }`}
                    >
                      <p className="text-base font-semibold text-[var(--fg)]">{city.label}</p>
                      <p className="mt-1 text-sm text-[var(--muted)]">Selecionar esta cidade</p>
                    </motion.button>
                  ))}
                </div>

                {values.selectedCityId ? (
                  <div className="rounded-[24px] border border-[var(--line)] bg-white/5 px-4 py-4">
                    <p className="text-sm text-[var(--fg)]">
                      Cidade escolhida: {selectedCity?.label}
                      {values.timeUnknown
                        ? ' | horario aproximado'
                        : values.time
                          ? ` | ${values.time}`
                          : ''}
                    </p>
                  </div>
                ) : null}
              </div>

              <div className="flex flex-wrap gap-3">
                <motion.button
                  type="button"
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.985 }}
                  onClick={() => goToStep(1)}
                  className="ritual-button-muted inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold"
                >
                  Voltar
                </motion.button>
                <motion.button
                  type="submit"
                  whileHover={pending ? undefined : { y: -2 }}
                  whileTap={pending ? undefined : { scale: 0.985 }}
                  disabled={!selectedCity || pending}
                  className="ritual-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {pending ? 'Abrindo sua leitura...' : 'Ver minha leitura'}
                </motion.button>
              </div>
            </motion.section>
          ) : null}
        </AnimatePresence>

        {validationError ? <p className="mt-6 text-sm text-[var(--danger)]">{validationError}</p> : null}
      </div>
    </motion.form>
  )
}
