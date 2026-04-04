export type Intensity = 'high' | 'medium' | 'low'

export type BirthTimePrecision = 'exact' | 'window' | 'unknown'
export type BirthTimeWindow = 'morning' | 'afternoon' | 'evening'

export type UserContext = {
  relationship_status?: 'single' | 'dating' | 'married' | 'separated' | 'divorced' | 'widowed' | null
  employment_status?: 'employed' | 'unemployed' | 'self_employed' | 'student' | 'retired' | null
  has_children?: boolean | null
  living_situation?: 'alone' | 'with_partner' | 'with_family' | 'shared' | null
  father_present?: boolean | null
  mother_present?: boolean | null
}

export type RealityTranslation = {
  scenarios: string[]
  impact: string
  risk: string
  action: string
}

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
  user_context?: UserContext | null
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
  reality_translation?: RealityTranslation
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

export type DomainCoverageEntry = {
  key: string
  label: string
  status: 'active' | 'watch' | 'quiet'
  probability: number
  intensity: Intensity
  time_window: TimeWindow | null
  signals: string[]
  domains_considered: string[]
  dominant_domain: string | null
  summary: string
  confidence: 'high' | 'medium' | 'low'
}

export type ForecastHorizon = {
  status: 'active' | 'watch' | 'quiet'
  summary: string
  period_label: string | null
  peak_date: string | null
  probability: number
}

export type ForecastTimelineHit = {
  period: string
  status: 'active' | 'watch' | 'quiet'
  probability: number
  summary: string
  peak_date?: string | null
}

export type LifeEventWindow = {
  start: string
  peak: string
  end: string
  duration_days: number
  precision: string
}

export type LifeEvent = {
  type: string
  label: string
  area_key: string
  window: LifeEventWindow
  date: string
  intensity: Intensity
  strength: number
  cause: string
  summary: string
  transits: ExactTimedEvent[]
}

export type ForecastSpecialFocus = {
  key?: string
  summary: string
  advice?: string
  why_now?: string
  signals?: string[]
  peak_dates?: string[]
  current_theme?: string
  marriage_probability?: number
  bonding_probability?: number
  breakup_probability?: number
  tension_probability?: number
  growth_probability?: number
  restriction_probability?: number
  restructure_probability?: number
  volatility_probability?: number
  exact_hits?: ExactTimedEvent[]
  critical_periods?: ExactCriticalPeriod[]
  life_events?: LifeEvent[]
}

export type ExactTimedEvent = {
  type: string
  domain: string
  area_key?: string
  planet_a: string
  planet_b: string
  aspect: string
  label: string
  date: string
  orb: number
  weight: number
  applying: boolean
  intensity: Intensity
  time_window: TimeWindow
}

export type ExactCriticalPeriod = {
  month: string
  intensity: 'high' | 'medium'
  total_weight: number
  headline: string
  events: ExactTimedEvent[]
}

export type ForecastAreaEntry = {
  key: string
  label: string
  status: 'active' | 'watch' | 'quiet'
  probability: number
  confidence: 'high' | 'medium' | 'low'
  short_term: ForecastHorizon
  mid_term: ForecastHorizon
  long_term: ForecastHorizon
  peak_dates: string[]
  what_tends_to_happen: string
  why_now: string
  advice: string
  signals: string[]
  counter_signals: string[]
  special_focus?: ForecastSpecialFocus | null
  timeline_hits: ForecastTimelineHit[]
}

export type ForecastHouseEntry = {
  house: number
  label: string
  domains: string[]
  status: 'active' | 'watch' | 'quiet'
  probability: number
  confidence: 'high' | 'medium' | 'low'
  short_term: ForecastHorizon
  mid_term: ForecastHorizon
  long_term: ForecastHorizon
  timeline_hits: ForecastTimelineHit[]
  peak_dates: string[]
  what_tends_to_happen: string
  signals: string[]
}

export type TimelinePeriodEntry = {
  period_key: string
  label: string
  granularity: 'month' | 'quarter'
  horizon: 'short' | 'mid' | 'long'
  start: string
  end: string
  headline: string
}

export type LifeEpisode = {
  id: string
  title: string
  domain: string
  start: string
  end: string
  peak: string | null
  arc: string
  summary: string
  key_dates: string[]
}

export type TurningPoint = {
  date: string
  domain: string
  label: string
  probability: number
  headline: string
  summary: string
}

export type PurposeForecast = {
  summary: string
  current_focus: string
  long_arc: string
  focus_domains: string[]
  evidence: string[]
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
    relationship_analysis?: ForecastSpecialFocus
    financial_analysis?: ForecastSpecialFocus
    purpose_analysis?: PurposeForecast
    techniques_used: string[]
    domain_analysis?: {
      domains: DomainAnalysisEntry[]
      coverage?: DomainCoverageEntry[]
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
  forecast_360?: {
    summary: string
    areas_da_vida: ForecastAreaEntry[]
    casas: ForecastHouseEntry[]
    proposito?: PurposeForecast
    critical_periods?: ExactCriticalPeriod[]
    life_events?: LifeEvent[]
    timelines: {
      short_term: string
      mid_term: string
      long_term: string
    }
    key_dates: string[]
  }
  timeline?: {
    periods: TimelinePeriodEntry[]
  }
  life_episodes?: LifeEpisode[]
  turning_points?: TurningPoint[]
  exact_timing?: {
    timed_events: ExactTimedEvent[]
    critical_periods: ExactCriticalPeriod[]
  }
  life_events?: LifeEvent[]
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
