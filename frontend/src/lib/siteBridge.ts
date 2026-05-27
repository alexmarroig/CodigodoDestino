export type MainSiteBridge = {
  url: string
  name: string
  logoUrl: string | null
}

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, '')
}

export function getMainSiteBridge(): MainSiteBridge | null {
  const url = process.env.NEXT_PUBLIC_MAIN_SITE_URL?.trim()
  if (!url) {
    return null
  }

  return {
    url: trimTrailingSlash(url),
    name: process.env.NEXT_PUBLIC_MAIN_SITE_NAME?.trim() || 'Meu site',
    logoUrl: process.env.NEXT_PUBLIC_MAIN_SITE_LOGO_URL?.trim() || null,
  }
}

export const appLinks = [
  { href: '/', label: 'Mapa do destino' },
  { href: '/horaria', label: 'Horaria' },
  { href: '/#intake-stage', label: 'Nova leitura' },
] as const
