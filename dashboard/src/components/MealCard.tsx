import type { MealItem } from '../types/api'

const MEAL_EMOJI: Record<string, string> = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
  snack: '🍎',
  pre_workout: '⚡',
  post_workout: '💪',
}

const MEAL_LABEL: Record<string, string> = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
  pre_workout: 'Pre-workout',
  post_workout: 'Post-workout',
}

export function MealCard({ meal }: { meal: MealItem }) {
  const emoji = MEAL_EMOJI[meal.meal_type] ?? '🍽️'
  const label = MEAL_LABEL[meal.meal_type] ?? meal.meal_type
  const time = meal.time ? meal.time.slice(0, 5) : ''

  return (
    <div style={{
      background: '#141414', border: '1px solid #262626', borderRadius: 12,
      padding: '12px 14px', display: 'flex', gap: 12, alignItems: 'flex-start',
    }}>
      {/* Emoji */}
      <div style={{ fontSize: 24, lineHeight: 1, paddingTop: 2, flexShrink: 0 }}>{emoji}</div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
          <span style={{ fontSize: 11, fontWeight: 700, color: '#8A8A8A', letterSpacing: '0.05em' }}>
            {label.toUpperCase()}
            {time && <span style={{ fontWeight: 400, marginLeft: 6, color: '#666' }}>{time}</span>}
          </span>
          <span style={{ fontSize: 16, fontWeight: 800, color: '#F5F5F5', flexShrink: 0 }}>
            {meal.cal_mid ?? '—'}
            <span style={{ fontSize: 10, fontWeight: 500, color: '#8A8A8A', marginLeft: 2 }}>kcal</span>
          </span>
        </div>
        <div style={{ fontSize: 14, color: '#F5F5F5', marginTop: 3, fontWeight: 500, lineHeight: 1.4 }}>
          {meal.description ?? 'No description'}
        </div>
        <div style={{ display: 'flex', gap: 10, marginTop: 5, fontSize: 11, color: '#8A8A8A' }}>
          {meal.cal_low != null && meal.cal_high != null && (
            <span>{meal.cal_low}–{meal.cal_high} kcal</span>
          )}
          {meal.protein_g != null && (
            <span style={{ color: '#3B82F6', fontWeight: 600 }}>{Math.round(meal.protein_g)}g protein</span>
          )}
        </div>
      </div>
    </div>
  )
}
