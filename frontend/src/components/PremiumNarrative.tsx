'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Block {
  title: string
  content: string
}

export function PremiumNarrative({ narrative, decisionResults }: any) {
  const text = narrative.text || ''
  const blocks = parseBlocks(text)
  const scores = decisionResults?.scores || {}

  return (
    <div className="space-y-8">
      {/* 1. MOMENTO AGORA & 2. QUEM ESTÁ ENVOLVIDO */}
      <div className="grid gap-6 md:grid-cols-2">
        <NarrativeBlock
          title="🔮 SEU MOMENTO AGORA"
          content={blocks[1] || ''}
          index={0}
        />
        <NarrativeBlock
          title="👤 QUEM ESTÁ ENVOLVIDO"
          content={blocks[2] || ''}
          index={1}
        />
      </div>

      {/* 4. SCORES (Visual Moderno) */}
      <section className="cosmic-shell rounded-[34px] px-8 py-8">
        <div className="mb-6">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted-soft)]">Dashboard de Intensidade</p>
          <h3 className="text-2xl font-semibold">Tendências do Ciclo</h3>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <ScoreCard label="Amor" score={scores.amor} />
          <ScoreCard label="Carreira" score={scores.carreira} />
          <ScoreCard label="Dinheiro" score={scores.dinheiro} />
          <ScoreCard label="Saúde" score={scores.saude} />
        </div>
      </section>

      {/* 3. LINHA DO TEMPO, 5. ALERTAS, 6. DIREÇÃO */}
      <div className="grid gap-6 md:grid-cols-3">
        <NarrativeBlock title="⏳ LINHA DO TEMPO" content={blocks[3] || ''} index={2} />
        <NarrativeBlock title="⚠️ ALERTAS" content={blocks[5] || ''} index={3} />
        <NarrativeBlock title="🚀 DIREÇÃO PRÁTICA" content={blocks[6] || ''} index={4} />
      </div>
    </div>
  )
}

function NarrativeBlock({ title, content, index }: { title: string, content: string, index: number }) {
  const [expanded, setExpanded] = useState(false)
  const lines = content.split('\n').filter(l => l.trim())

  const layer1 = lines.find(l => l.startsWith('👉')) || lines[0] || ''
  const explanation = lines.find(l => !l.startsWith('👉') && !l.startsWith('💡') && !l.startsWith('⚠️') && !l.startsWith('-')) || ''
  const bullets = lines.filter(l => l.startsWith('-'))
  const specialAlerts = lines.filter(l => l.startsWith('⚠️'))

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className="cosmic-shell flex flex-col rounded-[32px] px-7 py-7"
    >
      <h4 className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-[var(--muted-soft)]">{title}</h4>

      <div className="mb-3 text-lg font-medium leading-tight text-[var(--fg)]">
        {layer1.replace('👉', '').trim()}
      </div>

      <p className="mb-4 text-sm leading-relaxed text-[var(--muted)]">
        {explanation}
      </p>

      {bullets.length > 0 && (
        <div className="mb-4 space-y-2">
          {bullets.map((b, i) => (
            <div key={i} className="flex items-start gap-2 text-sm text-[var(--fg)]">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--accent)]" />
              {b.replace('-', '').trim()}
            </div>
          ))}
        </div>
      )}

      {/* Interactive Layer 3 */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-auto w-full rounded-2xl border border-[var(--line)] bg-white/5 py-3 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--muted)] transition-colors hover:bg-white/10"
      >
        {expanded ? 'Ver menos' : 'Ver profundidade'}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="pt-4 text-sm leading-relaxed text-[var(--muted-soft)] italic">
              A análise profunda revela que este movimento não é apenas circunstancial, mas um ponto de maturação necessário para sua evolução de longo prazo. O foco deve ser na integração consciente desses temas.
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  )
}

function ScoreCard({ label, score }: { label: string, score: number }) {
  const percentage = (score || 0) * 10
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-end">
        <span className="text-sm font-medium text-[var(--muted)]">{label}</span>
        <span className="text-xl font-bold font-mono">{score?.toFixed(1) || '5.0'}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          className="h-full bg-gradient-to-r from-[var(--accent-soft)] to-[var(--accent)]"
        />
      </div>
    </div>
  )
}

function parseBlocks(text: string): Record<number, string> {
  const blocks: Record<number, string> = {}
  const regex = /(\d\.\s[^123456]+)/g
  const parts = text.split(/\d\.\s/)
  parts.forEach((part, i) => {
    if (i > 0) blocks[i] = part.trim()
  })
  return blocks
}
