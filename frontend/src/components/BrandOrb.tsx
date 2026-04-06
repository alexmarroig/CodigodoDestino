'use client'

import Image from 'next/image'
import { motion, useReducedMotion } from 'framer-motion'

const FRAME_SOURCES = [
  '/brand/frames/ezgif-frame-001.jpg',
  '/brand/frames/ezgif-frame-003.jpg',
  '/brand/frames/ezgif-frame-005.jpg',
  '/brand/frames/ezgif-frame-010.jpg',
  '/brand/frames/ezgif-frame-015.jpg',
  '/brand/frames/ezgif-frame-020.jpg',
]

type BrandOrbProps = {
  size?: 'header' | 'hero' | 'splash'
  showWordmark?: boolean
  className?: string
}

export function BrandOrb({ size = 'hero', showWordmark = false, className = '' }: BrandOrbProps) {
  const prefersReducedMotion = useReducedMotion()
  const scale = size === 'header' ? 'h-16 w-16' : size === 'splash' ? 'h-[18rem] w-[18rem] sm:h-[24rem] sm:w-[24rem]' : 'h-[20rem] w-[20rem] sm:h-[28rem] sm:w-[28rem]'
  const ringScale = size === 'header' ? 'h-24 w-24' : size === 'splash' ? 'h-[24rem] w-[24rem] sm:h-[32rem] sm:w-[32rem]' : 'h-[28rem] w-[28rem] sm:h-[38rem] sm:w-[38rem]'
  const frameSize = size === 'header' ? 'h-8 w-8' : size === 'splash' ? 'h-16 w-16 sm:h-20 sm:w-20' : 'h-14 w-14 sm:h-[4.5rem] sm:w-[4.5rem]'

  return (
    <div className={`relative flex flex-col items-center ${className}`}>
      <div className={`relative ${ringScale} flex items-center justify-center`}>
        <motion.div
          animate={prefersReducedMotion ? undefined : { rotate: 360 }}
          transition={{ duration: size === 'header' ? 22 : 34, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
          className="orb-ring orb-ring-outer absolute inset-0"
        />
        <motion.div
          animate={prefersReducedMotion ? undefined : { rotate: -360 }}
          transition={{ duration: size === 'header' ? 18 : 28, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
          className="orb-ring orb-ring-mid absolute inset-[10%]"
        />
        <motion.div
          animate={prefersReducedMotion ? undefined : { rotate: 360, scale: [1, 1.03, 1] }}
          transition={{ duration: 16, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
          className="orb-aura absolute inset-[19%] rounded-full"
        />

        <div className={`orb-video-shell ${scale} relative overflow-hidden rounded-full`}>
          <video
            className="orb-video absolute inset-0 h-full w-full object-cover"
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            poster="/brand/orb-poster.png"
            aria-label="Logotipo animado do Codigo do Destino"
          >
            <source src="/brand/orb-logo.mp4" type="video/mp4" />
          </video>
          <div className="orb-video-glow absolute inset-0" />
        </div>

        <motion.div
          animate={prefersReducedMotion ? undefined : { rotate: 360 }}
          transition={{ duration: 48, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
          className="pointer-events-none absolute inset-0"
        >
          {FRAME_SOURCES.map((src, index) => {
            const angle = (360 / FRAME_SOURCES.length) * index
            return (
              <motion.div
                key={src}
                animate={prefersReducedMotion ? undefined : { y: [0, -6, 0], opacity: [0.76, 1, 0.76] }}
                transition={{ duration: 4 + index * 0.35, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
                className={`orb-frame-chip ${frameSize}`}
                style={{
                  left: '50%',
                  top: '50%',
                  transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-42%)`,
                  transformOrigin: 'center center',
                }}
              >
                <div
                  className="relative h-full w-full overflow-hidden rounded-[18px] border border-white/20 bg-[rgba(7,11,24,0.92)] shadow-[0_20px_50px_rgba(0,0,0,0.42)]"
                  style={{ transform: `rotate(${-angle}deg)` }}
                >
                  <Image src={src} alt="" fill sizes="96px" className="object-cover opacity-85" />
                </div>
              </motion.div>
            )
          })}
        </motion.div>
      </div>

      {showWordmark ? (
        <div className="mt-6 text-center">
          <p className="orb-wordmark text-[10px] uppercase tracking-[0.52em] text-cyan-200/70">Codigo do Destino</p>
          <h2 className="mt-2 text-balance text-3xl font-semibold tracking-[-0.04em] text-white sm:text-5xl">
            A esfera abre a leitura
          </h2>
        </div>
      ) : null}
    </div>
  )
}
