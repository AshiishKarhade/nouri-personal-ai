interface MacroRowProps {
  label: string
  consumed: number
  target: number
  color: string
  unit?: string
}

function MacroRow({ label, consumed, target, color, unit = 'g' }: MacroRowProps) {
  const pct = target > 0 ? Math.min((consumed / target) * 100, 100) : 0

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span
          className="font-medium"
          style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}
        >
          {label}
        </span>
        <span className="font-semibold" style={{ fontSize: 13, color: 'var(--text-primary)' }}>
          {consumed}
          <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>
            {' '}/ {target}{unit}
          </span>
        </span>
      </div>
      <div
        className="relative rounded-full overflow-hidden"
        style={{ height: 6, background: '#262626' }}
      >
        <div
          className="absolute left-0 top-0 h-full rounded-full"
          style={{
            width: `${pct}%`,
            background: color,
            transition: 'width 0.5s ease',
          }}
        />
      </div>
    </div>
  )
}

interface MacroBarProps {
  protein: { consumed: number; target: number }
  carbs: { consumed: number; target: number }
  fats: { consumed: number; target: number }
  fiber: { consumed: number; target: number }
}

export function MacroBar({ protein, carbs, fats, fiber }: MacroBarProps) {
  return (
    <div
      className="rounded-xl p-4 flex flex-col gap-4"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
    >
      <span
        className="font-semibold"
        style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.06em', textTransform: 'uppercase' }}
      >
        Macros
      </span>
      <MacroRow label="Protein" consumed={protein.consumed} target={protein.target} color="#3B82F6" />
      <MacroRow label="Carbs" consumed={carbs.consumed} target={carbs.target} color="#EAB308" />
      <MacroRow label="Fats" consumed={fats.consumed} target={fats.target} color="#A855F7" />
      <MacroRow label="Fiber" consumed={fiber.consumed} target={fiber.target} color="#22C55E" />
    </div>
  )
}
