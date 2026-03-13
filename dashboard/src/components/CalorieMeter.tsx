interface CalorieMeterProps {
  consumed: number
  target: number
}

export function CalorieMeter({ consumed, target }: CalorieMeterProps) {
  const size = 120
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2

  // Semi-circle: 180 degrees. We use a path approach with SVG arc.
  // The arc goes from left to right across the bottom of the SVG.
  const cx = size / 2
  const cy = size / 2 + 10 // shift center down a bit for semi-circle framing

  const startAngle = -180 // degrees, leftmost point
  const endAngle = 0

  const pct = Math.min(consumed / target, 1.2) // allow slight overflow for visual
  const fillAngle = startAngle + pct * 180

  function polarToCartesian(angleDeg: number) {
    const rad = (angleDeg * Math.PI) / 180
    return {
      x: cx + radius * Math.cos(rad),
      y: cy + radius * Math.sin(rad),
    }
  }

  const start = polarToCartesian(startAngle)
  const end = polarToCartesian(endAngle)
  // clamp just before 0 for arc flag (reference point, not rendered directly)

  const ratio = consumed / target
  let arcColor = '#22C55E'
  if (ratio >= 1.0) arcColor = '#EF4444'
  else if (ratio >= 0.9) arcColor = '#EAB308'

  // Track path (full semi-circle)
  const trackPath = `M ${start.x} ${start.y} A ${radius} ${radius} 0 0 1 ${end.x} ${end.y}`

  // Fill path (partial arc)
  const fillEnd = polarToCartesian(Math.min(fillAngle, endAngle))
  const largeArc = pct > 0.5 ? 1 : 0
  const fillPath =
    pct > 0
      ? `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${fillEnd.x} ${fillEnd.y}`
      : ''

  return (
    <div
      className="flex flex-col items-center justify-center rounded-xl p-4 flex-1"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
    >
      <div className="relative" style={{ width: size, height: size * 0.65 }}>
        <svg
          width={size}
          height={size}
          style={{ position: 'absolute', top: 0, left: 0, overflow: 'visible' }}
        >
          {/* Track */}
          <path
            d={trackPath}
            fill="none"
            stroke="#262626"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          {/* Fill */}
          {fillPath && (
            <path
              d={fillPath}
              fill="none"
              stroke={arcColor}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.6s ease' }}
            />
          )}
        </svg>
        {/* Center label */}
        <div
          className="absolute flex flex-col items-center"
          style={{ bottom: -8, left: 0, right: 0 }}
        >
          <span
            className="font-extrabold leading-none"
            style={{ fontSize: 26, color: 'var(--text-primary)' }}
          >
            {consumed.toLocaleString()}
          </span>
          <span
            className="font-medium mt-1"
            style={{ fontSize: 10, color: 'var(--text-secondary)' }}
          >
            of {target.toLocaleString()} kcal
          </span>
        </div>
      </div>
      <span
        className="font-semibold mt-5 text-center"
        style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.05em' }}
      >
        CALORIES
      </span>
    </div>
  )
}
