import { Footprints, Moon, Dumbbell } from 'lucide-react'

const ICON_MAP = {
  steps: Footprints,
  sleep: Moon,
  workout: Dumbbell,
}

interface StatTileProps {
  icon: keyof typeof ICON_MAP
  value: string | number
  label: string
  color?: string
}

export function StatTile({ icon, value, label, color = 'var(--text-primary)' }: StatTileProps) {
  const Icon = ICON_MAP[icon]

  return (
    <div
      style={{
        flex: 1,
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 12,
        padding: '12px 8px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 4,
        minWidth: 0,
      }}
    >
      <Icon size={18} color={color} strokeWidth={2} />
      <span style={{ fontSize: 16, fontWeight: 800, color, lineHeight: 1 }}>
        {value}
      </span>
      <span
        style={{
          fontSize: 9,
          fontWeight: 600,
          color: 'var(--text-secondary)',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
        }}
      >
        {label}
      </span>
    </div>
  )
}
