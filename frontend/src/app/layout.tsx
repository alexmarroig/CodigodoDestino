import { ReactNode } from 'react'
import type { Metadata } from 'next'
import { Cormorant_Garamond, Manrope } from 'next/font/google'

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

export const metadata: Metadata = {
  title: 'Codigo do Destino',
  description: 'Uma experiencia imersiva de leitura pessoal com astrologia e numerologia.',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body
        className={`${bodyFont.variable} ${displayFont.variable} bg-[var(--bg)] font-sans text-[var(--fg)] antialiased`}
      >
        {children}
      </body>
    </html>
  )
}
