export type TimelineEvent = {
  id: string
  evento: string
  categoria: string
  intensidade: string
  score: number
}

export function Timeline({ events }: { events: TimelineEvent[] }) {
  return (
    <div className="space-y-3">
      {events.map((event) => (
        <div key={event.id} className="rounded-lg border p-4 bg-white shadow-sm">
          <h3 className="font-semibold">{event.evento}</h3>
          <p className="text-sm text-gray-600">Categoria: {event.categoria}</p>
          <p className="text-sm text-gray-600">Intensidade: {event.intensidade}</p>
          <p className="text-sm text-gray-600">Score: {event.score}</p>
        </div>
      ))}
    </div>
  )
}
