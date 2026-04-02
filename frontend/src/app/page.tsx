'use client'

import { useState } from 'react'
import { Timeline, TimelineEvent } from '../components/Timeline'

export default function Home() {
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [loading, setLoading] = useState(false)

  async function onSubmit(formData: FormData) {
    setLoading(true)
    const payload = {
      date: formData.get('date'),
      time: formData.get('time'),
      timezone: formData.get('timezone'),
      city: formData.get('city'),
      lat: Number(formData.get('lat')),
      lon: Number(formData.get('lon')),
      orb_degrees: Number(formData.get('orb_degrees')),
      house_system: 'P',
    }

    const res = await fetch('http://localhost:8000/mapa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    setEvents(data.events ?? [])
    setLoading(false)
  }

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-3xl space-y-6">
        <h1 className="text-2xl font-bold">Mapa Astrológico com IA</h1>
        <form action={onSubmit} className="grid grid-cols-2 gap-3 rounded-lg bg-white p-4 shadow">
          <input name="date" type="date" className="border p-2 rounded" required />
          <input name="time" type="time" className="border p-2 rounded" required />
          <input name="timezone" defaultValue="America/Sao_Paulo" className="border p-2 rounded" required />
          <input name="city" placeholder="Cidade" className="border p-2 rounded" required />
          <input name="lat" type="number" step="any" placeholder="Latitude" className="border p-2 rounded" required />
          <input name="lon" type="number" step="any" placeholder="Longitude" className="border p-2 rounded" required />
          <input name="orb_degrees" type="number" defaultValue={6} className="border p-2 rounded" required />
          <button type="submit" className="rounded bg-black text-white p-2">{loading ? 'Gerando...' : 'Gerar Mapa'}</button>
        </form>
        <Timeline events={events} />
      </div>
    </main>
  )
}
