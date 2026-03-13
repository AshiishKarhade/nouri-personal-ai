import { useFetch } from '../hooks/useApi'
import { Skeleton } from '../components/Skeleton'

interface UserProfile {
  name?: string
  age?: number
  height_cm?: number
  goal?: string
  program_start?: string
  target_date?: string
  cal_target_training?: number
  cal_target_rest?: number
  protein_target_g?: number
  steps_target?: number
  supplements?: string[]
}

export function SettingsPage() {
  const { data, loading, error } = useFetch<UserProfile>('/api/v1/memory')

  const rows: [string, string | number | undefined | null][] = [
    ['Name', data?.name],
    ['Age', data?.age ? `${data.age} years` : undefined],
    ['Height', data?.height_cm ? `${data.height_cm} cm` : undefined],
    ['Goal', data?.goal],
    ['Program Start', data?.program_start],
    ['Target Date', data?.target_date],
    ['Cal Target (Training)', data?.cal_target_training ? `${data.cal_target_training} kcal` : undefined],
    ['Cal Target (Rest)', data?.cal_target_rest ? `${data.cal_target_rest} kcal` : undefined],
    ['Protein Target', data?.protein_target_g ? `${data.protein_target_g}g / day` : undefined],
    ['Steps Target', data?.steps_target ? `${data.steps_target.toLocaleString()} steps` : undefined],
  ]

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ fontSize: 18, fontWeight: 700, paddingBottom: 4 }}>Settings</div>

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
          {error}
        </div>
      )}

      {/* Profile card */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--border)',
            fontSize: 12,
            fontWeight: 600,
            color: 'var(--text-secondary)',
            letterSpacing: '0.06em',
          }}
        >
          PROFILE
        </div>
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <div key={i} style={{ padding: '10px 16px', borderBottom: '1px solid var(--border)' }}>
                <Skeleton height={16} />
              </div>
            ))
          : rows.map(([label, value]) =>
              value != null ? (
                <div
                  key={label}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '11px 16px',
                    borderBottom: '1px solid var(--border)',
                  }}
                >
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{label}</span>
                  <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                    {String(value)}
                  </span>
                </div>
              ) : null
            )}
      </div>

      {/* Supplements */}
      {data?.supplements && data.supplements.length > 0 && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--border)',
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--text-secondary)',
              letterSpacing: '0.06em',
            }}
          >
            SUPPLEMENTS
          </div>
          {data.supplements.map((s) => (
            <div
              key={s}
              style={{
                padding: '11px 16px',
                borderBottom: '1px solid var(--border)',
                fontSize: 13,
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <span style={{ color: 'var(--accent-green)' }}>✓</span>
              {s}
            </div>
          ))}
        </div>
      )}

      {/* Info note */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          padding: 14,
          fontSize: 13,
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
        }}
      >
        This dashboard is <strong style={{ color: 'var(--text-primary)' }}>read-only</strong>.
        All data entry is done via Telegram — chat with Iron (Coach) or Nouri (Nutritionist).
      </div>

      {/* Version */}
      <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-secondary)', paddingTop: 4 }}>
        Transformation Coach v1.0.0
      </div>
    </div>
  )
}
