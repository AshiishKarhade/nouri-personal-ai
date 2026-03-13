import { Dumbbell, Salad } from 'lucide-react'

interface AgentNotesProps {
  coachNotes: string | null
  nouriNotes: string | null
}

export function AgentNotes({ coachNotes, nouriNotes }: AgentNotesProps) {
  if (!coachNotes && !nouriNotes) return null

  return (
    <div className="flex flex-col gap-3">
      <span
        className="font-semibold"
        style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.06em', textTransform: 'uppercase' }}
      >
        Agent Notes
      </span>
      <div className="flex flex-col gap-3">
        {coachNotes && (
          <div
            className="rounded-xl p-3 flex gap-3"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
          >
            <div className="flex-shrink-0 mt-0.5">
              <div
                className="flex items-center justify-center rounded-lg"
                style={{ width: 28, height: 28, background: '#1a1a2e' }}
              >
                <Dumbbell size={14} color="#3B82F6" strokeWidth={2} />
              </div>
            </div>
            <div>
              <span
                className="font-semibold block mb-1"
                style={{ fontSize: 11, color: '#3B82F6', letterSpacing: '0.04em' }}
              >
                IRON
              </span>
              <p
                className="italic leading-relaxed"
                style={{ fontSize: 13, color: 'var(--text-secondary)' }}
              >
                {coachNotes}
              </p>
            </div>
          </div>
        )}
        {nouriNotes && (
          <div
            className="rounded-xl p-3 flex gap-3"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
          >
            <div className="flex-shrink-0 mt-0.5">
              <div
                className="flex items-center justify-center rounded-lg"
                style={{ width: 28, height: 28, background: '#1a2a1a' }}
              >
                <Salad size={14} color="#22C55E" strokeWidth={2} />
              </div>
            </div>
            <div>
              <span
                className="font-semibold block mb-1"
                style={{ fontSize: 11, color: '#22C55E', letterSpacing: '0.04em' }}
              >
                NOURI
              </span>
              <p
                className="italic leading-relaxed"
                style={{ fontSize: 13, color: 'var(--text-secondary)' }}
              >
                {nouriNotes}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
