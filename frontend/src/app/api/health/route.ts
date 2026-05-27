import { NextResponse } from 'next/server'

function backendBaseUrl() {
  return (
    process.env.BACKEND_URL?.replace(/\/+$/, '') ||
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '') ||
    'http://127.0.0.1:8000'
  )
}

export async function GET() {
  try {
    const response = await fetch(`${backendBaseUrl()}/health`, { cache: 'no-store' })
    const payload = await response.json()
    return NextResponse.json({
      frontend: 'ok',
      backend: payload,
      backend_url: backendBaseUrl(),
    })
  } catch {
    return NextResponse.json(
      {
        frontend: 'ok',
        backend: { status: 'unreachable' },
        backend_url: backendBaseUrl(),
      },
      { status: 502 },
    )
  }
}
