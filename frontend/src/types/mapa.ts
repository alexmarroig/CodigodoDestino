export type Intensity = 'high' | 'medium' | 'low'

export type BirthTimePrecision = 'exact' | 'window' | 'unknown'
export type BirthTimeWindow = 'morning' | 'afternoon' | 'evening'

export type MapaRequest = {
  date: string
  time?: string
  lat: number
  lon: number
  timezone: string
  orb_degrees: number
  house_system: string
  reference_date?: string
  birth_time_precision?: BirthTimePrecision | null
  birth_time_window?: BirthTimeWindow | null
}

export type TimeWindow = {
  start: string
  end: string
  peak?: string
  duration_days?: number
  precision?: string
}

export type EventDriver = {
  kind: string
  code: string
  weight: number
  evidence: Record<string, unknown>
}

export type ForecastEvent = {
  id: string
  type: string
  event: string
  title: string
  summary: string
  category: string
  domains?: string[]
  intensity: Intensity
  score: number
  probability?: number
  priority: number
  confidence: number
  tags: string[]
  signals?: string[]
  cause?: string
  effect?: string
  advice?: string
  drivers: EventDriver[]
  recommendations: string[]
  time_window: TimeWindow
  narrative_hint: string
  counter_signals?: string[]
  context: Record<string, unknown>
  rank?: number
}

export type SignPosition = {
  longitude: number
  sign: string
  sign_en: string
  sign_index: number
  degree_in_sign: number
  degree: number
  minute: number
  second: number
  formatted: string
}

export type PlanetData = {
  longitude: number
  latitude: number
  distance_au: number
  speed_longitude?: number
  retrograde?: boolean
}

export type AspectData = {
  planet_a: string
  planet_b: string
  aspect: string
  target_angle: number
  exact_angle?: number
  orb: number
  phase?: string
  domain?: string
  transit_house?: number | null
  natal_house?: number | null
  time_window?: TimeWindow
  weight?: number
}

export type ProfileQuality = {
  code: 'A' | 'B' | 'C'
  label: string
  birth_time_precision: BirthTimePrecision
  birth_time_window?: BirthTimeWindow | null
  effective_time: string
  assumptions: string[]
  confidence_modifier: number
  can_use_houses: boolean
  can_use_angles: boolean
}

export type DomainSignal = {
  technique: string
  domain: string
  label: string
  weight: number
  polarity: 'supportive' | 'challenging' | 'mixed'
  phase: string
  kind: string
  time_window: TimeWindow
  evidence: Record<string, unknown>
}

export type DomainAnalysisEntry = {
  domain: string
  domain_label: string
  signal_count: number
  independent_techniques: string[]
  supportive_weight: number
  challenging_weight: number
  mixed_weight: number
  total_weight: number
  probability: number
  intensity: Intensity
  tone: 'supportive' | 'challenging' | 'mixed'
  converged: boolean
  signals: DomainSignal[]
  time_window: TimeWindow
}

export type Uncertainty = {
  domain: string
  kind: string
  message: string
  scenario_a: string
  scenario_b: string
  observables: string[]
}

export type AnalysisConfidence = {
  level: 'high' | 'medium' | 'low'
  score: number
  reason: string
  profile_quality: 'A' | 'B' | 'C'
}

export type MapaResponse = {
  request_id: string
  input: MapaRequest & { reference_date: string }
  computed: {
    utc: {
      input_local: {
        date: string
        time: string
        timezone: string
      }
      utc_datetime: string
      offset_applied: string
      is_dst: boolean
    }
    astrology: {
      utc_datetime: string
      julian_day: number
      planets: Record<string, PlanetData>
      angles: Record<string, number>
      houses: {
        system: string
        cusps: number[]
      }
      signs: Record<string, SignPosition>
      planet_houses?: Record<string, number | null>
    }
    aspects: {
      orb_degrees: number
      aspects: AspectData[]
    }
    numerology: {
      birth_date: string
      life_path_number: number
      personal_year: {
        reference_year: number
        value: number
        is_master: boolean
      }
    }
  }
  analysis?: {
    profile_quality: ProfileQuality
    theme_map: Record<string, string>
    transits?: {
      reference_utc: string
      aspects: AspectData[]
    }
    profections?: {
      age: number
      activated_house: number
      activated_domain: string
      activated_sign: SignPosition
      lord_of_year: string
      time_window: TimeWindow
    }
    solar_return?: {
      available: boolean
      utc_datetime?: string
      dominant_houses?: Array<{
        house: number
        domain: string
        planet_count: number
      }>
      angle_hits?: Array<{
        planet: string
        angle: string
        orb: number
      }>
      reason?: string
    }
    progressions?: {
      progressed_utc: string
      aspects: AspectData[]
    }
    solar_arc?: {
      age_years: number
      aspects: AspectData[]
    }
    techniques_used: string[]
    domain_analysis?: {
      domains: DomainAnalysisEntry[]
      uncertainties: Uncertainty[]
      confidence: AnalysisConfidence
    }
  }
  profile_quality: ProfileQuality
  confidence: AnalysisConfidence
  uncertainties: Uncertainty[]
  techniques_used: string[]
  events: ForecastEvent[]
  event_summary: {
    total: number
    categories: Record<string, number>
    intensity_breakdown: Record<string, number>
    top_event_ids: string[]
    top_tags: string[]
    average_score: number
    highest_priority: number
  }
  narrative: {
    text: string
    model: string
    provider: string
    usage: {
      input_tokens: number
      output_tokens: number
    }
    strategy: string
    requested_strategy?: string
    strategy_reason: string
    complexity_score: number
    prompt_event_count: number
    cached?: boolean
  }
  metadata: {
    engine_version: string
    cache_hit: boolean
    generated_at: string
    cache: {
      full_response: boolean
      computed_snapshot: boolean
      ephemeris: boolean
      redis_enabled: boolean
    }
    cost_control: {
      narrative_strategy: string
      strategy_reason: string
      complexity_score: number
      prompt_event_count: number
    }
    performance: {
      total_ms: number
      narrative_strategy?: string
    }
  }
}

export type HoraryRequest = {
  question: string
  date: string
  time: string
  lat: number
  lon: number
  timezone: string
  orb_degrees?: number
  house_system?: string
}

export type HoraryResponse = {
  request_id: string
  question: string
  domain: string
  chart: {
    utc: {
      input_local: {
        date: string
        time: string
        timezone: string
      }
      utc_datetime: string
      offset_applied: string
      is_dst: boolean
    }
  }
  is_radical: boolean
  strictures: Array<{
    code: string
    message: string
  }>
  significators: {
    querent_house: number
    querent_sign: SignPosition
    querent_ruler: string
    quesited_house: number
    quesited_domain: string
    quesited_sign: SignPosition
    quesited_ruler: string
    moon: string
  }
  testimonies_for: Array<{
    label: string
    weight: number
    evidence: Record<string, unknown>
  }>
  testimonies_against: Array<{
    label: string
    weight: number
    evidence: Record<string, unknown>
  }>
  judgment: string
  confidence: {
    level: 'high' | 'medium' | 'low'
    score: number
  }
  uncertainty_reason: string
}
