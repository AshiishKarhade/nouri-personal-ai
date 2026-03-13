import { useFetch } from '../hooks/useApi'
import type { ProgressData, StatsResponse } from '../types/api'
import { TrendChart } from '../components/TrendChart'
import { WeekSummaryCard } from '../components/WeekSummaryCard'
import { Skeleton } from '../components/Skeleton'

export function Progress() {
  const { data, loading, error } = useFetch<ProgressData>('/api/v1/progress?weeks=8')
  const statsRes = useFetch<StatsResponse>('/api/v1/stats')

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

  const stats = statsRes.data

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ fontSize: 18, fontWeight: 700, paddingBottom: 4 }}>Progress</div>

      {/* Summary delta tiles */}
      {statsRes.loading ? (
        <div style={{ display: 'flex', gap: 8 }}>
          <Skeleton height={80} style={{ flex: 1 }} />
          <Skeleton height={80} style={{ flex: 1 }} />
        </div>
      ) : stats ? (
        <div style={{ display: 'flex', gap: 8 }}>
          {[
            {
              label: 'WEIGHT DELTA',
              delta: stats.weight_delta_kg,
              current: stats.current_weight_kg,
              unit: 'kg',
              lowerIsBetter: true,
            },
            {
              label: 'WAIST DELTA',
              delta: stats.waist_delta_cm,
              current: stats.current_waist_cm,
              unit: 'cm',
              lowerIsBetter: true,
            },
          ].map(({ label, delta, current, unit, lowerIsBetter }) => (
            <div
              key={label}
              style={{
                flex: 1,
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 12,
                padding: 14,
                textAlign: 'center',
              }}
            >
              <div
                style={{
                  fontSize: 22,
                  fontWeight: 800,
                  color:
                    delta == null
                      ? 'var(--text-secondary)'
                      : (lowerIsBetter ? delta <= 0 : delta >= 0)
                      ? 'var(--accent-green)'
                      : 'var(--accent-red)',
                }}
              >
                {delta != null
                  ? `${delta > 0 ? '+' : ''}${delta} ${unit}`
                  : '—'}
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-secondary)', marginTop: 4, fontWeight: 600, letterSpacing: '0.05em' }}>
                {label}
              </div>
              {current != null && (
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                  Now: {current} {unit}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : null}

      {/* Weight trend */}
      {loading ? (
        <Skeleton height={200} />
      ) : data && data.days.some((d) => d.weight_kg != null) ? (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            padding: '14px 14px 8px',
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.05em', marginBottom: 10 }}>
            WEIGHT TREND (kg)
          </div>
          <TrendChart
            data={data.days.filter((d) => d.weight_kg != null) as unknown[]}
            xKey="date"
            lines={[{ key: 'weight_kg', color: '#A855F7', name: 'Weight kg' }]}
            height={160}
          />
        </div>
      ) : !loading && data ? (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 12, padding: 20, textAlign: 'center', color: 'var(--text-secondary)', fontSize: 13 }}>
          No weight data yet. Log measurements via Telegram: "weight 78 kg"
        </div>
      ) : null}

      {/* Waist trend */}
      {loading ? (
        <Skeleton height={200} />
      ) : data && data.days.some((d) => d.waist_cm != null) ? (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            padding: '14px 14px 8px',
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.05em', marginBottom: 10 }}>
            WAIST TREND (cm)
          </div>
          <TrendChart
            data={data.days.filter((d) => d.waist_cm != null) as unknown[]}
            xKey="date"
            lines={[{ key: 'waist_cm', color: '#3B82F6', name: 'Waist cm' }]}
            height={160}
          />
        </div>
      ) : null}

      {/* Calorie vs target */}
      {loading ? (
        <Skeleton height={200} />
      ) : data && data.days.some((d) => d.cal_actual_mid != null) ? (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            padding: '14px 14px 8px',
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.05em', marginBottom: 10 }}>
            DAILY CALORIES vs TARGET
          </div>
          <TrendChart
            data={data.days.filter((d) => d.cal_actual_mid != null) as unknown[]}
            xKey="date"
            bars={[{ key: 'cal_actual_mid', color: '#22C55E', name: 'Calories' }]}
            referenceLine={{ key: 'cal_target', color: '#EF4444', label: 'Target' }}
            height={160}
          />
        </div>
      ) : null}

      {/* Weekly breakdown */}
      {stats?.weekly_history && stats.weekly_history.length > 0 && (
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.05em', marginBottom: 10 }}>
            WEEKLY BREAKDOWN
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {stats.weekly_history.slice(-4).reverse().map((w) => (
              <WeekSummaryCard key={w.week_number} week={w} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
