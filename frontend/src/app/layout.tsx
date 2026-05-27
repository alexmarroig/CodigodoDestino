import { ReactNode } from 'react'
import type { Metadata, Viewport } from 'next'
import { Cormorant_Garamond, Manrope } from 'next/font/google'

import { SiteNavBar } from '@/components/SiteNavBar'

import './globals.css'

const bodyFont = Manrope({
  subsets: ['latin'],
  variable: '--font-body',
})

const displayFont = Cormorant_Garamond({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['500', '600', '700'],
})

export const viewport: Viewport = {
  themeColor: '#050812',
  colorScheme: 'dark',
  width: 'device-width',
  initialScale: 1,
}

export const metadata: Metadata = {
  title: {
    default: 'Código do Destino',
    template: '%s · Código do Destino',
  },
  description: 'Uma experiência imersiva de leitura pessoal com astrologia e numerologia. Descubra ciclos, eventos e narrativa do seu mapa natal.',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://codigododestino.com.br'),
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    title: 'Código do Destino',
    description: 'Uma experiência imersiva de leitura pessoal com astrologia e numerologia.',
    siteName: 'Código do Destino',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Código do Destino',
    description: 'Uma experiência imersiva de leitura pessoal com astrologia e numerologia.',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body
        className={`${bodyFont.variable} ${displayFont.variable} bg-[var(--bg)] font-sans text-[var(--fg)] antialiased`}
      >
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-full focus:bg-[var(--accent)] focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-[#160f09]"
        >
          Pular para conteúdo
        </a>
        <SiteNavBar />
        <div id="main-content">
          {children}
        </div>
      </body>
    </html>
  )
}
