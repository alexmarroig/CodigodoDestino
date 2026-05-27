'use client'

import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

import { appLinks, getMainSiteBridge } from '@/lib/siteBridge'

function isActive(pathname: string, href: string) {
  if (href === '/#intake-stage') {
    return pathname === '/'
  }

  return pathname === href || (href !== '/' && pathname.startsWith(href))
}

export function SiteNavBar() {
  const pathname = usePathname()
  const mainSite = useMemo(() => getMainSiteBridge(), [])
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    setMenuOpen(false)
  }, [pathname])

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 12)
    }

    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [menuOpen])

  return (
    <header className="site-nav-root sticky top-0 z-50">
      {mainSite ? (
        <div className="site-nav-utility border-b border-[var(--line)]">
          <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-4 px-5 py-2 sm:px-8 lg:px-10">
            <a
              href={mainSite.url}
              className="inline-flex min-w-0 items-center gap-2 text-sm font-semibold text-[var(--muted)] transition hover:text-[var(--accent)]"
            >
              <span aria-hidden="true">←</span>
              <span className="truncate">Voltar para {mainSite.name}</span>
            </a>
            <p className="hidden text-[11px] uppercase tracking-[0.24em] text-[var(--muted-soft)] sm:block">
              Leitura avancada · Codigo do Destino
            </p>
          </div>
        </div>
      ) : null}

      <div className={`site-nav-main ${scrolled ? 'site-nav-main-scrolled' : ''}`}>
        <div className="mx-auto flex max-w-[1440px] items-center gap-3 px-5 py-3 sm:px-8 lg:px-10">
          {mainSite?.logoUrl ? (
            <a href={mainSite.url} className="hidden shrink-0 sm:block" aria-label={`Voltar para ${mainSite.name}`}>
              <Image
                src={mainSite.logoUrl}
                alt=""
                width={120}
                height={32}
                className="h-8 w-auto object-contain opacity-90"
                unoptimized
              />
            </a>
          ) : null}

          <Link href="/" className="min-w-0 shrink-0">
            <p className="truncate font-display text-lg font-semibold leading-none text-[var(--fg)] sm:text-xl">
              Codigo do Destino
            </p>
            <p className="mt-1 truncate text-[11px] uppercase tracking-[0.22em] text-[var(--muted-soft)]">
              {mainSite ? `Ferramenta do ${mainSite.name}` : 'Leitura pessoal'}
            </p>
          </Link>

          <nav
            aria-label="Navegacao deste app"
            className="mx-auto hidden items-center gap-1 rounded-full border border-[var(--line)] bg-[rgba(255,255,255,0.02)] p-1 md:flex"
          >
            {appLinks.map((item) => {
              const active = isActive(pathname, item.href)
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`site-nav-link ${active ? 'site-nav-link-active' : ''}`}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            {mainSite ? (
              <a
                href={mainSite.url}
                className="site-nav-back hidden items-center rounded-full border border-[var(--line)] px-3 py-2 text-xs font-semibold text-[var(--muted)] transition hover:border-[var(--line-strong)] hover:text-[var(--fg)] sm:inline-flex"
              >
                Site principal
              </a>
            ) : null}

            <button
              type="button"
              className="site-nav-menu-button md:hidden"
              aria-expanded={menuOpen}
              aria-controls="site-mobile-menu"
              aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
              onClick={() => setMenuOpen((open) => !open)}
            >
              <span className={`site-nav-menu-line ${menuOpen ? 'site-nav-menu-line-top-open' : ''}`} />
              <span className={`site-nav-menu-line ${menuOpen ? 'site-nav-menu-line-mid-open' : ''}`} />
              <span className={`site-nav-menu-line ${menuOpen ? 'site-nav-menu-line-bottom-open' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {menuOpen ? (
          <motion.div
            id="site-mobile-menu"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            className="site-nav-mobile md:hidden"
          >
            <nav aria-label="Menu mobile" className="mx-auto max-w-[1440px] space-y-2 px-5 py-4 sm:px-8">
              {mainSite ? (
                <a href={mainSite.url} className="site-nav-mobile-link">
                  <span>← Voltar para {mainSite.name}</span>
                  <span className="text-xs text-[var(--muted-soft)]">Sair desta ferramenta</span>
                </a>
              ) : null}
              {appLinks.map((item) => {
                const active = isActive(pathname, item.href)
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`site-nav-mobile-link ${active ? 'site-nav-mobile-link-active' : ''}`}
                  >
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </nav>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </header>
  )
}
