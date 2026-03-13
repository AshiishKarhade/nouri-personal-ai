import { useState } from 'react'
import { useFetch } from '../hooks/useApi'
import type { HistoryDay } from '../types/api'
import { MealCard } from '../components/MealCard'
import { Skeleton } from '../components/Skeleton'
import { ChevronDown, ChevronRight } from 'lucide-react'

function dayColor(summary: HistoryDay['summary']): string {
  if (!summary?.cal_actual_mid || !summary?.cal_target) return 'var(--text-secondary)'
  const ratio = summary.cal_actual_mid / summary.cal_target
  if (ratio <= 1.05) return 'var(--accent-green)'
  if (ratio <= 1.15) return 'var(--accent-yellow)'
  return 'var(--accent-red)'
}

function DayRow({ day }: { day: HistoryDay }) {
  const [expanded, setExpanded] = useState(false)
  const color = dayColor(day.summary)
  const calActual = day.summary?.cal_actual_mid
  const protein = day.summary?.protein_g

  const dateLabel = new Date(day.date + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 12,
        overflow: 'hidden',
      }}
    >
      <button
        onClick={() => setExpanded((e) => !e)}
        style={{
          width: '100%',
          background: 'none',
          border: 'none',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          cursor: 'pointer',
          color: 'var(--text-primary)',
        }}
      >
        {/* Day number */}
        <span
          style={{
            fontSize: 11,
            fontWeight: 700,
            color: 'var(--text-secondary)',
            minWidth: 40,
            textAlign: 'left',
          }}
        >
          D{day.day_number ?? '?'}
        </span>

        {/* Date */}
        <span style={{ fontSize: 14, fontWeight: 600, flex: 1, textAlign: 'left' }}>
          {dateLabel}
        </span>

        {/* Cal badge */}
        {calActual != null && (
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color,
              background: `${color}18`,
              border: `1px solid ${color}30`,
              borderRadius: 6,
              padding: '2px 8px',
            }}
          >
            {calActual} kcal
          </span>
        )}

        {/* Protein */}
        {protein != null && (
          <span
            style={{
              fontSize: 11,
              color: 'var(--accent-blue)',
              minWidth: 44,
              textAlign: 'right',
            }}
          >
            {Math.round(protein)}g P
          </span>
        )}

        {/* Chevron */}
        <span style={{ color: 'var(--text-secondary)', marginLeft: 4 }}>
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </span>
      </button>

      {expanded && day.meals.length > 0 && (
        <div
          style={{
            borderTop: '1px solid var(--border)',
            padding: '10px 12px',
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
          }}
        >
          {day.meals.map((meal) => (
            <MealCard key={meal.id} meal={meal} />
          ))}
        </div>
      )}

      {expanded && day.meals.length === 0 && (
        <div
          style={{
            borderTop: '1px solid var(--border)',
            padding: '12px 16px',
            color: 'var(--text-secondary)',
            fontSize: 13,
          }}
        >
          No meals logged for this day.
        </div>
      )}
    </div>
  )
}

export function HistoryPage() {
  const { data, loading, error } = useFetch<HistoryDay[]>('/api/v1/history?days=30')

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ fontSize: 18, fontWeight: 700, paddingBottom: 4 }}>History</div>

      {error && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--accent-red)',
            borderRadius: 12,
            padding: 16,
            color: 'var(--accent-red)',
            fontSize: 14,
          }}
        >
          Failed to load: {error}
        </div>
      )}

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} height={52} />
          ))}
        </div>
      )}

      {!loading && data && data.length === 0 && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            padding: 24,
            textAlign: 'center',
            color: 'var(--text-secondary)',
            fontSize: 14,
          }}
        >
          No history yet. Start logging meals via Telegram.
        </div>
      )}

      {!loading && data && data.map((day) => <DayRow key={day.date} day={day} />)}
    </div>
  )
}
