import { ReactNode } from 'react'

type SurfacePanelProps = {
  eyebrow?: string
  title: string
  subtitle?: string
  children: ReactNode
  className?: string
}

export function SurfacePanel({
  eyebrow,
  title,
  subtitle,
  children,
  className = '',
}: SurfacePanelProps) {
  return (
    <section className={`vercel-panel relative overflow-hidden rounded-[36px] p-6 sm:p-8 ${className}`}>
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[var(--line-strong)] to-transparent" />
      <header className="mb-7 space-y-3">
        {eyebrow ? (
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--muted-soft)]">{eyebrow}</p>
        ) : null}
        <div className="space-y-3">
          <h2 className="text-3xl font-semibold leading-[0.95] tracking-[-0.05em] text-[var(--fg)] sm:text-[2.25rem]">
            {title}
          </h2>
          {subtitle ? <p className="max-w-3xl text-sm text-[var(--muted)] sm:text-base">{subtitle}</p> : null}
        </div>
      </header>
      {children}
    </section>
  )
}
