import { NextRequest, NextResponse } from 'next/server'

function backendBaseUrl() {
  return (
    process.env.BACKEND_URL?.replace(/\/+$/, '') ||
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '') ||
    'http://127.0.0.1:8000'
  )
}

export async function POST(request: NextRequest) {
  const body = await request.text()

  try {
    const response = await fetch(`${backendBaseUrl()}/horaria`, {
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
            'Backend indisponivel. Configure BACKEND_URL no Vercel ou suba a API FastAPI localmente.',
        },
      },
      { status: 502 },
    )
  }
}
