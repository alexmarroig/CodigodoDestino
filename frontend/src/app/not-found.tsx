import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-16">
      <div className="aurora-field pointer-events-none absolute inset-0 opacity-90" />
      <div className="starfield pointer-events-none absolute inset-0 opacity-45" />

      <section className="cosmic-shell-strong relative max-w-2xl rounded-[36px] px-8 py-12 text-center sm:px-12">
        <p className="text-xs uppercase tracking-[0.4em] text-[var(--muted-soft)]">Caminho nao encontrado</p>
        <h1 className="mt-6 text-4xl font-semibold leading-[0.92] sm:text-6xl">
          Essa passagem nao esta aberta agora.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-sm text-[var(--muted)] sm:text-base">
          Volte para a entrada principal e continue a leitura por la.
        </p>

        <Link
          href="/"
          className="ritual-button mt-8 inline-flex items-center justify-center rounded-full px-7 py-3.5 text-sm font-semibold"
        >
          Voltar ao inicio
        </Link>
      </section>
    </main>
  )
}
