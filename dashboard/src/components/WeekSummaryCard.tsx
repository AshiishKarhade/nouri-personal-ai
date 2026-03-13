import type { WeeklyStats } from '../types/api'

interface WeekSummaryCardProps {
  week: WeeklyStats
}

export function WeekSummaryCard({ week }: WeekSummaryCardProps) {
  const items: [string, string, string][] = [
    ['Avg Cal', week.avg_calories != null ? `${Math.round(week.avg_calories)}` : '—', 'kcal'],
    ['Avg Protein', week.avg_protein_g != null ? `${Math.round(week.avg_protein_g)}` : '—', 'g'],
    ['On Target', String(week.days_on_target), 'days'],
    ['Workouts', String(week.workouts_completed), ''],
  ]

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 12,
        padding: '12px 16px',
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          color: 'var(--text-secondary)',
          letterSpacing: '0.06em',
          marginBottom: 10,
        }}
      >
        WEEK {week.week_number}
      </div>
      <div style={{ display: 'flex', gap: 12 }}>
        {items.map(([label, value, unit]) => (
          <div key={label} style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
              {value}
              {unit && value !== '—' && (
                <span style={{ fontSize: 10, fontWeight: 500, color: 'var(--text-secondary)', marginLeft: 2 }}>
                  {unit}
                </span>
              )}
            </div>
            <div style={{ fontSize: 9, color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.05em', marginTop: 4 }}>
              {label.toUpperCase()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
