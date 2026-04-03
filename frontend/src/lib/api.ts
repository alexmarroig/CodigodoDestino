import { HoraryRequest, HoraryResponse, MapaRequest, MapaResponse } from '@/types/mapa'

const EXPLICIT_API_URL = process.env.NEXT_PUBLIC_API_URL
const API_URL_CANDIDATES = EXPLICIT_API_URL
  ? [EXPLICIT_API_URL]
  : ['http://127.0.0.1:8000', 'http://localhost:8000']

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function requestJson<T>(path: string, payload: unknown, fallbackMessage: string): Promise<T> {
  let response: Response | null = null
  let lastConnectionError: unknown = null
  let lastTriedUrl = API_URL_CANDIDATES[0]

  for (const apiUrl of API_URL_CANDIDATES) {
    lastTriedUrl = apiUrl

    try {
      response = await fetch(`${apiUrl}${path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        cache: 'no-store',
      })
      break
    } catch (error) {
      lastConnectionError = error
      response = null
    }
  }

  if (!response) {
    if (lastConnectionError instanceof TypeError) {
      throw new ApiError(
        `Nao consegui conectar com a API em ${lastTriedUrl}. Verifique se o backend FastAPI esta rodando e se o CORS permite http://localhost:3000.`,
        0,
      )
    }

    throw new ApiError('Nao foi possivel conectar com a API.', 0)
  }

  if (!response.ok) {
    let message = fallbackMessage

    try {
      const parsed = (await response.json()) as { error?: { message?: string } }
      message = parsed.error?.message ?? message
    } catch {
      message = response.statusText || message
    }

    throw new ApiError(message, response.status)
  }

  return (await response.json()) as T
}

export function requestMapa(payload: MapaRequest): Promise<MapaResponse> {
  return requestJson<MapaResponse>('/mapa', payload, 'Nao foi possivel gerar o mapa.')
}

export function requestHorary(payload: HoraryRequest): Promise<HoraryResponse> {
  return requestJson<HoraryResponse>('/horaria', payload, 'Nao foi possivel abrir a leitura horaria.')
}
