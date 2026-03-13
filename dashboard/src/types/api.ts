// API response types matching FastAPI backend schemas

export interface MealItem {
  id: number
  date: string
  meal_type: string
  time: string | null
  description: string | null
  cal_low: number | null
  cal_high: number | null
  cal_mid: number | null
  protein_g: number | null
  carbs_g: number | null
  fats_g: number | null
  fiber_g: number | null
  photo_path: string | null
  ai_analysis: string | null
  parse_failed: boolean
  created_at: string
}

export interface DailySummaryItem {
  id: number
  date: string
  day_number: number | null
  day_type: string | null
  cal_target: number | null
  cal_actual_mid: number | null
  protein_g: number | null
  carbs_g: number | null
  fats_g: number | null
  fiber_g: number | null
  meals_count: number
  steps: number | null
  sleep_hrs: number | null
  sleep_quality: number | null
  workout_done: boolean | null
  workout_notes: string | null
  coach_notes: string | null
  nouri_notes: string | null
  synced_to_sheets: boolean
  updated_at: string
}

export interface CalorieSummary {
  target: number
  consumed_low: number
  consumed_high: number
  consumed_mid: number
  remaining_mid: number
  on_track: boolean
}

export interface MacroSummary {
  protein_g: number
  protein_target_g: number
  carbs_g: number
  fats_g: number
  fiber_g: number
}

export interface TodayResponse {
  date: string
  day_number: number
  day_type: string
  calories: CalorieSummary
  macros: MacroSummary
  meals: MealItem[]
  meals_count: number
  steps: number | null
  steps_target: number
  sleep_hrs: number | null
  sleep_quality: number | null
  workout_done: boolean | null
  latest_weight_kg: number | null
  latest_waist_cm: number | null
  protein_on_track: boolean
  summary: DailySummaryItem | null
}

export interface DayProgressPoint {
  date: string
  day_number: number | null
  cal_actual_mid: number | null
  cal_target: number | null
  protein_g: number | null
  steps: number | null
  sleep_hrs: number | null
  weight_kg: number | null
  waist_cm: number | null
  workout_done: boolean | null
}

export interface MeasurementItem {
  id: number
  date: string
  week_number: number | null
  weight_kg: number | null
  waist_cm: number | null
  body_fat_pct: number | null
  notes: string | null
  created_at: string
}

export interface ProgressData {
  weeks: number
  start_date: string
  end_date: string
  days: DayProgressPoint[]
  measurements: MeasurementItem[]
}

export interface HistoryDay {
  date: string
  day_number: number | null
  summary: DailySummaryItem | null
  meals: MealItem[]
}

export interface WeeklyStats {
  week_number: number
  avg_calories: number | null
  avg_protein_g: number | null
  days_on_target: number
  days_over_target: number
  avg_steps: number | null
  avg_sleep_hrs: number | null
  workouts_completed: number
}

export interface StatsResponse {
  current_day_number: number
  current_week_number: number
  total_meals_logged: number
  days_tracked: number
  avg_calories_this_week: number | null
  avg_protein_this_week: number | null
  days_on_target_this_week: number
  avg_steps_this_week: number | null
  avg_sleep_this_week: number | null
  workouts_this_week: number
  current_weight_kg: number | null
  current_waist_cm: number | null
  weight_delta_kg: number | null
  waist_delta_cm: number | null
  weekly_history: WeeklyStats[]
}
