import { useFetch } from '../hooks/useApi'
import type { TodayResponse } from '../types/api'
import { ProgressRing } from '../components/ProgressRing'
import { CalorieMeter } from '../components/CalorieMeter'
import { MacroBar } from '../components/MacroBar'
import { MealCard } from '../components/MealCard'
import { StatTile } from '../components/StatTile'
import { AgentNotes } from '../components/AgentNotes'
import { Skeleton } from '../components/Skeleton'

export function Today() {
  const { data, loading, error } = useFetch<TodayResponse>('/api/v1/today')

  if (error) {
    return (
      <div style={{ padding: 16 }}>
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
      </div>
    )
  }

  if (loading || !data) {
    return (
      <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', gap: 12 }}>
          <Skeleton width={148} height={164} />
          <Skeleton height={164} style={{ flex: 1 }} />
        </div>
        <Skeleton height={120} />
        <div style={{ display: 'flex', gap: 8 }}>
          <Skeleton height={80} style={{ flex: 1 }} />
          <Skeleton height={80} style={{ flex: 1 }} />
          <Skeleton height={80} style={{ flex: 1 }} />
        </div>
        <Skeleton height={200} />
      </div>
    )
  }

  const dateLabel = new Date(data.date + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 4 }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
            Today
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{dateLabel}</div>
        </div>
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            padding: '3px 8px',
            borderRadius: 6,
            background: data.day_type === 'training' ? 'rgba(34,197,94,0.12)' : 'rgba(138,138,138,0.12)',
            color: data.day_type === 'training' ? 'var(--accent-green)' : 'var(--text-secondary)',
            border: `1px solid ${data.day_type === 'training' ? 'rgba(34,197,94,0.25)' : 'var(--border)'}`,
            letterSpacing: '0.05em',
          }}
        >
          {data.day_type.toUpperCase()}
        </span>
      </div>

      {/* Row 1: ProgressRing + CalorieMeter */}
      <div style={{ display: 'flex', gap: 12 }}>
        <ProgressRing day={data.day_number} />
        <CalorieMeter
          consumed={data.calories.consumed_mid}
          target={data.calories.target}
        />
      </div>

      {/* Macro bars */}
      <MacroBar
        protein={{ consumed: data.macros.protein_g, target: data.macros.protein_target_g }}
        carbs={{ consumed: data.macros.carbs_g, target: 200 }}
        fats={{ consumed: data.macros.fats_g, target: 56 }}
        fiber={{ consumed: data.macros.fiber_g, target: 25 }}
      />

      {/* Protein warning */}
      {!data.protein_on_track && (
        <div
          style={{
            background: 'rgba(234,179,8,0.1)',
            border: '1px solid rgba(234,179,8,0.3)',
            borderRadius: 10,
            padding: '10px 14px',
            fontSize: 13,
            color: 'var(--accent-yellow)',
          }}
        >
          Protein behind target — aim for a high-protein meal soon.
        </div>
      )}

      {/* Stat tiles */}
      <div style={{ display: 'flex', gap: 8 }}>
        <StatTile
          icon="steps"
          value={data.steps ?? '—'}
          label="Steps"
          color={
            data.steps == null
              ? 'var(--text-secondary)'
              : data.steps >= 8000
              ? 'var(--accent-green)'
              : 'var(--accent-yellow)'
          }
        />
        <StatTile
          icon="sleep"
          value={data.sleep_hrs != null ? `${data.sleep_hrs}h` : '—'}
          label="Sleep"
          color={
            data.sleep_hrs == null
              ? 'var(--text-secondary)'
              : data.sleep_hrs >= 7
              ? 'var(--accent-green)'
              : 'var(--accent-red)'
          }
        />
        <StatTile
          icon="workout"
          value={data.workout_done == null ? '—' : data.workout_done ? '✓' : '✗'}
          label="Workout"
          color={
            data.workout_done == null
              ? 'var(--text-secondary)'
              : data.workout_done
              ? 'var(--accent-green)'
              : 'var(--accent-red)'
          }
        />
      </div>

      {/* Meals */}
      <div>
        <div
          style={{
            fontSize: 12,
            fontWeight: 600,
            color: 'var(--text-secondary)',
            letterSpacing: '0.06em',
            marginBottom: 8,
          }}
        >
          MEALS TODAY ({data.meals_count})
        </div>
        {data.meals.length === 0 ? (
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 12,
              padding: 20,
              textAlign: 'center',
              color: 'var(--text-secondary)',
              fontSize: 13,
            }}
          >
            No meals logged yet. Tell Nouri what you ate via Telegram.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.meals.map((meal) => (
              <MealCard key={meal.id} meal={meal} />
            ))}
          </div>
        )}
      </div>

      {/* Agent notes */}
      {(data.summary?.coach_notes || data.summary?.nouri_notes) && (
        <AgentNotes
          coachNotes={data.summary?.coach_notes ?? null}
          nouriNotes={data.summary?.nouri_notes ?? null}
        />
      )}
    </div>
  )
}
