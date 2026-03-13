import type { MealItem } from '../types/api'

const MEAL_EMOJI: Record<string, string> = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
  snack: '🍎',
}

interface MealCardProps {
  meal: MealItem
}

export function MealCard({ meal }: MealCardProps) {
  const emoji = MEAL_EMOJI[meal.meal_type] ?? '🍽️'

  // Format time: expects "HH:MM" or "HH:MM:SS"
  const timeLabel = meal.time ? meal.time.slice(0, 5) : ''

  return (
    <div
      className="flex items-start gap-3 rounded-xl p-3"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
    >
      {/* Emoji + time column */}
      <div className="flex flex-col items-center gap-1 pt-0.5" style={{ minWidth: 40 }}>
        <span style={{ fontSize: 20 }}>{emoji}</span>
        <span style={{ fontSize: 10, color: 'var(--text-secondary)', fontWeight: 500 }}>
          {timeLabel}
        </span>
      </div>

      {/* Description */}
      <div className="flex-1 min-w-0">
        <p
          className="font-medium leading-snug"
          style={{
            fontSize: 13,
            color: 'var(--text-primary)',
            overflow: 'hidden',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {meal.description}
        </p>
        <div className="flex items-center gap-2 mt-1.5">
          <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
            {meal.cal_low}–{meal.cal_high} kcal
          </span>
          <span style={{ color: 'var(--border)' }}>·</span>
          <span style={{ fontSize: 11, color: '#3B82F6', fontWeight: 600 }}>
            {meal.protein_g}g protein
          </span>
        </div>
      </div>

      {/* Cal mid badge */}
      <div className="flex flex-col items-end gap-1 pt-0.5">
        <span
          className="font-bold"
          style={{ fontSize: 15, color: 'var(--text-primary)' }}
        >
          {meal.cal_mid}
        </span>
        <span style={{ fontSize: 9, color: 'var(--text-secondary)', letterSpacing: '0.04em' }}>
          kcal
        </span>
      </div>
    </div>
  )
}
