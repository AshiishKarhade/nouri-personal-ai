interface ProgressRingProps {
  day: number
  total?: number
}

export function ProgressRing({ day, total = 56 }: ProgressRingProps) {
  const size = 120
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = Math.min(day / total, 1)
  const dashOffset = circumference * (1 - progress)

  return (
    <div
      className="flex flex-col items-center justify-center rounded-xl p-4"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#262626"
            strokeWidth={strokeWidth}
          />
          {/* Progress */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#22C55E"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        {/* Center text */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center"
          style={{ transform: 'rotate(0deg)' }}
        >
          <span
            className="font-extrabold leading-none"
            style={{ fontSize: 28, color: 'var(--text-primary)' }}
          >
            {day}
          </span>
          <span
            className="font-medium"
            style={{ fontSize: 10, color: 'var(--text-secondary)', marginTop: 2 }}
          >
            of {total}
          </span>
        </div>
      </div>
      <span
        className="font-semibold mt-2 text-center"
        style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.05em' }}
      >
        DAY
      </span>
    </div>
  )
}
