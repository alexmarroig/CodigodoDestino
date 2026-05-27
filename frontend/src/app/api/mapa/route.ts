import { NextRequest, NextResponse } from 'next/server'

const MAX_BODY_BYTES = 1024 * 1024 // 1 MB

function backendBaseUrl() {
  return (
    process.env.BACKEND_URL?.replace(/\/+$/, '') ||
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '') ||
    'http://127.0.0.1:8000'
  )
}

export async function POST(request: NextRequest) {
  const contentLength = request.headers.get('content-length')
  if (contentLength && Number(contentLength) > MAX_BODY_BYTES) {
    return NextResponse.json(
      { error: { message: 'Requisição excede o tamanho máximo permitido.' } },
      { status: 413 },
    )
  }

  const body = await request.text()

  if (Buffer.byteLength(body, 'utf8') > MAX_BODY_BYTES) {
    return NextResponse.json(
      { error: { message: 'Requisição excede o tamanho máximo permitido.' } },
      { status: 413 },
    )
  }

  try {
    const response = await fetch(`${backendBaseUrl()}/mapa`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body,
      cache: 'no-store',
    })

    const payload = await response.text()
    return new NextResponse(payload, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('content-type') ?? 'application/json',
      },
    })
  } catch {
    return NextResponse.json(
      {
        error: {
          message:
            'Backend indisponível. Configure BACKEND_URL no Vercel ou suba a API FastAPI localmente.',
        },
      },
      { status: 502 },
    )
  }
}
