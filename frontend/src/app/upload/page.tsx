import Link from 'next/link'

export default function UploadPage() {
  return (
    <main className="min-h-screen bg-[#0b1020] px-6 py-24 text-white">
      <div className="mx-auto max-w-2xl rounded-3xl border border-white/10 bg-white/5 p-10 shadow-2xl shadow-black/30 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Codigo do Destino</p>
        <h1 className="mt-4 text-4xl font-semibold text-white">Upload indisponivel por enquanto</h1>
        <p className="mt-4 text-base leading-7 text-slate-300">
          Essa rota foi mantida so para compatibilidade. O fluxo principal agora acontece na leitura
          natal e na tela de horaria.
        </p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Link
            href="/"
            className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          >
            Voltar para a leitura
          </Link>
          <Link
            href="/horaria"
            className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:border-cyan-300 hover:text-cyan-200"
          >
            Abrir horaria
          </Link>
        </div>
      </div>
    </main>
  )
}
